from flask import Flask, render_template, make_response, jsonify, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import get_flashed_messages
import os 
import requests
from functools import lru_cache
import re
import json

GREEK_REGEX = re.compile(r'[\u0370-\u03FF]')  # εύρεση ελληνικών χαρακτήρων
LOCAL_ENDPOINT = 'http://127.0.0.1:5010/translate'
PUBLIC_ENDPOINT = 'https://libretranslate.com/translate'



def _(text):
    target = request.cookies.get('language', 'en')  # default στα αγγλικά
    if target == 'el':
        return text  # αν ζητάς ελληνικά, μην καλείς μεταφραστή
    return translate(text, target_lang=target)

# Provide access to the current language for templates
def get_locale():
    return request.cookies.get('language', 'en')  # ίδιο default

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_translator():
    return dict(_=_, get_locale=get_locale)


def _post_translate(url, text, source, target, timeout=5):
    return requests.post(
        url,
        headers={'Content-Type': 'application/json'},
        json={'q': text, 'source': source, 'target': target, 'format': 'text'},
        timeout=timeout
    )

@lru_cache(maxsize=1024)
def translate(text, target_lang='en'):
    # Γρήγορο short-circuit
    if not text or not isinstance(text, str):
        return text

    print(f"[DEBUG] Translating to: {target_lang} | Text: {text[:50]}...")

    # 1) Αν φαίνεται ελληνικό, δοκίμασε πρώτα ρητά source='el' στο local.
    source_guess = 'el' if GREEK_REGEX.search(text) else 'auto'

    try:
        # --- ΠΡΩΤΗ ΠΡΟΣΠΑΘΕΙΑ: τοπικός translator ---
        r = _post_translate(LOCAL_ENDPOINT, text, source_guess, target_lang)
        print("[DEBUG][LOCAL] Status:", r.status_code)
        print("[DEBUG][LOCAL] Response:", r.text)

        if r.ok:
            data = r.json()
            out = data.get('translatedText', text)
            detected = (data.get('detectedLanguage') or {}).get('language')

            # Αν γύρισε αμετάφραστο ή ανίχνευσε 'en' με μηδενική βεβαιότητα, κάνε failover
            same_text = out.strip() == text.strip()
            low_conf_en = (detected == 'en' and (data.get('detectedLanguage') or {}).get('confidence', 1.0) == 0.0)

            if not same_text and not low_conf_en:
                return out
            else:
                print("[DEBUG] Local translator returned same text or low-confidence detection; trying public.")
        else:
            # 400 κλπ (π.χ. "el is not supported")
            print("[DEBUG] Local translator error; trying public.")
    except Exception as e:
        print(f"[ERROR] Local translate error: {e}. Trying public endpoint...")

    # 2) FAILOVER: δημόσιο endpoint με καθαρό source
    try:
        fallback_source = 'el' if GREEK_REGEX.search(text) else 'auto'
        r2 = _post_translate(PUBLIC_ENDPOINT, text, fallback_source, target_lang)
        print("[DEBUG][PUBLIC] Status:", r2.status_code)
        print("[DEBUG][PUBLIC] Response:", r2.text)

        if r2.ok:
            data2 = r2.json()
            out2 = data2.get('translatedText', text)
            return out2
    except Exception as e2:
        print(f"[ERROR] Public translate error: {e2}")

    # 3) Τελικό fallback: επέστρεψε όπως είναι για να μην “χαλάσεις” UI
    return text



def autotranslate(text):
    try:
        target = request.cookies.get('language', 'en')
    except RuntimeError:
        target = 'en'
    return text if target == 'el' else translate(text, target_lang=target)

app.jinja_env.filters['autotranslate'] = autotranslate


@app.route('/set_language/<lang>')
def set_language(lang):
    response = make_response(redirect(request.referrer or '/'))
    response.set_cookie('language', lang, max_age=60*60*24*30)  # 30 ημέρες
    return response


@app.route('/ping-translate')
def ping_translate():
    return translate('Καλημέρα', 'en')


# Μοντέλα
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150)) 
    searches = db.relationship('Search', backref='user', lazy=True)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_search_user'), nullable=False)


# Home Page 
@app.route('/', methods=['GET', 'POST'])
def home():
    print("DEBUG: Flash messages before render:", get_flashed_messages(with_categories=True))
    if request.method == 'POST':
        location = request.form.get('location')
        if location:
            if 'user_id' in session:
                new_search = Search(location=location, user_id=session['user_id'])
                db.session.add(new_search)
                db.session.commit()
            else:
                    flash(_('Πρέπει να συνδεθείς πρώτα για να κάνεις αναζήτηση.'), 'warning')
                    return redirect(url_for('login'))
    return render_template('home_1.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # Ελέγχουμε αν ο χρήστης είναι ήδη συνδεδεμένος
        session.modified = True
        flash(_('Ήδη είσαι συνδεδεμένος.'), 'info')
        return redirect(url_for('home'))  # Επιστροφή στην αρχική σελίδα
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        # Έλεγχος για τον χρήστη
        if user and user.password == password:
            session['user_id'] = user.id  # Αποθήκευση στο session
            session['username'] = user.username  # 
            flash(_('Η σύνδεση ήταν επιτυχής!'), 'success')
            return redirect(url_for('home'))  # Μετά την είσοδο πηγαίνουμε στο home
        else:
            flash(_('Λάθος όνομα χρήστη ή κωδικός.'), 'danger')
            return redirect(url_for('login'))  # Αν υπάρχει λάθος, επιστροφή στο login
    
    return render_template('login.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash(_('Είσαι ήδη συνδεδεμένος. Κάνε αποσύνδεση για να δημιουργήσεις νέο λογαριασμό.'), 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash(_('Συμπλήρωσε όλα τα πεδία.'), 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash(_('Το όνομα χρήστη υπάρχει ήδη.'), 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash(_('Το email χρησιμοποιείται ήδη.'), 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username  
        flash(_('Η εγγραφή ήταν επιτυχής!'), 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html')

# Ιστορικό αναζητήσεων
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    searches = Search.query.filter_by(user_id=user_id).all()

    title_to_url = {s['title'].lower(): s['url'] for s in SUGGESTIONS}

    # Μοναδικές τοποθεσίες (τελευταία εμφάνιση για κάθε μία)
    seen = set()
    unique_searches = []
    for s in reversed(searches):  # Από τις πιο πρόσφατες προς τις παλιότερες
        loc = s.location.strip().lower()
        if loc not in seen:
            seen.add(loc)
            unique_searches.append({
                'id': s.id,
                'location': s.location,
                'url': title_to_url.get(loc)
            })

    unique_searches.reverse()  # Για να τα εμφανίζεις με σωστή σειρά

    return render_template('history.html', searches=unique_searches)

@app.route('/delete_search/<int:search_id>', methods=['POST'])
def delete_search(search_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = Search.query.get_or_404(search_id)
    if search.user_id != session['user_id']:
        flash(_('Μη εξουσιοδοτημένη ενέργεια.'), 'danger')
        return redirect(url_for('history'))

    # Διαγράφουμε όλες τις εμφανίσεις της συγκεκριμένης τοποθεσίας για τον χρήστη
    Search.query.filter_by(user_id=session['user_id'], location=search.location).delete()
    db.session.commit()

    flash(_('Η αναζήτηση διαγράφηκε.'), 'success')
    return redirect(url_for('history'))




# Route για Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)  #  καθάρισε και αυτό
    flash(_('Αποσυνδεθήκατε.'), 'info')
    return redirect(url_for('home'))


# Συνέχεια ως επισκέπτης
@app.route('/guest')
def guest():
    session['guest'] = True
    return redirect(url_for('home'))




SUGGESTIONS = [{
        "title": "Vlaxerena",
        "image": "/static/img/Vlaxerena/vlaxerna/icon1.jpg",
        "description": "Vlaxerena",
        "url": "/vlaxerena"
    },
    {
        "title": "Nisaki",
        "image": "/static/img/Nisaki/nisaki pezoporia/icon1.jpg",
        "description": "Nisaki",
        "url": "/Nisaki"
    },
    {
        "title": "Ag. Gordios",
        "image": "/static/img/Ag.Gorgios/nayagio agios gordis-20250524T162344Z-1-001/nayagio agios gordis/icon1.jpg",
        "description": "Ag.Gordios",
        "url": "/agGordios"
    },
    {
        "title": "Arkoudilas",
        "image": "/static/img/arkoudilas/arkoudilas/icon1.jpg.jpg",
        "description": "arkoudilas",
        "url": "/arkoudilas"
    },
    {
        "title": "Erimitis",
        "image": "/static/img/Erimitis/erimitis/Ερημίτης/1.jpg",
        "description": "erimitis",
        "url": "/erimitis"
    },
    {
        "title": "Loggas",
        "image": "/static/img/loggas peroulades-20250717T175654Z-1-001/loggas peroulades/1.jpg",
        "description": "loggas",
        "url": "/loggas"
    },
    {
        "title": "Canal",
        "image": "/static/img/canal/canal damour/1.jpg",
        "description": "canal",
        "url": "/canal"
    },
    {
        "title": "Ermones",
        "image": "/static/img/ermones/ermones ekklisaki/1.jpg",
        "description": "ermomes",
        "url": "/ermones"
    },
    {
        "title": "Giannades",
        "image": "/static/img/giannades/Προφήτης Ηλίας- Γιαννάδες/1.jpg",
        "description": "giannades",
        "url": "/giannades"
    },
    {
        "title": "Makrades",
        "image": "/static/img/makrades/makrades/1.jpg",
        "description": "makrades",
        "url": "/makrades"
    },
    {
        "title": "Cape_Drastis",
        "image": "/static/img/cape drastis/1.jpg",
        "description": "cape drastis",
        "url": "/Cape_Drastis"
    },
    {
        "title": "MonRepos",
        "image": "/static/img/mon repo/1.jpg",
        "description": "MonRepos",
        "url": "/MonRepos"
    },
    {
        "title": "nimfes",
        "image": "/static/img/Καταρράκτες Νυμφές/1.jpg",
        "description": "nimfes",
        "url": "/nimfes"
    },
    {
        "title": "Old Fortress ",
        "image": "/static/img/palaio frourio/6.jpg",
        "description": "Old Fortress ",
        "url": "/oldFort"
    },
    {
        "title": "Porto Timoni ",
        "image": "/static/img/Πόρτο Τιμόνι-αφιωνας/16.jpg",
        "description": "Porto Timoni ",
        "url": "/porto_timoni"
    },
    {
        "title": "Perama ",
        "image": "/static/img/dromos toy nerou perama/2.jpg",
        "description": "Perama ",
        "url": "/perama"
    },
    {
        "title": "Gastouri ",
        "image": "/static/img/agia kyriaki gastouri/1.jpg",
        "description": "Gastouri ",
        "url": "/Gastouri"
    },
    {
        "title": "Stavros ",
        "image": "static/img/stavros loop/1.jpg",
        "description": "Stavros ",
        "url": "/stavros"
    }
    ]


# Καταχώρηση αναζήτησης
@app.route('/search', methods=['POST'])
def search():
    if request.is_json:
        data = request.get_json()
        location = data.get('location')
    else:
        location = request.form.get('location')

    if not location:
        return _("No search term provided"), 400

    if 'user_id' in session:
        user_id = session['user_id']
        new_search = Search(location=location, user_id=user_id)
        db.session.add(new_search)
        db.session.commit()

    return redirect(url_for('home'))


@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').lower()
    # matches = [s for s in SUGGESTIONS if query in s['title'].lower().startswith(query)]
    matches = [s for s in SUGGESTIONS if s['title'].lower().startswith(query)]

    print("Returned matches:", matches)  # debug
    return jsonify(matches)


@app.route("/about/")
def about():
    title = _('About Us')
    return render_template("about.html", title=title)


@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/routes/")
def routes():
    return render_template("Routes.html")

@app.route("/vlaxerena/")
def vlaxerena():
    lang = request.cookies.get('language', 'el')
    return render_template("vlaxerena.html", title="vlaxerena", lang=get_locale())

@app.route("/Nisaki/")
def nisaki():
    return render_template("Nisaki.html", title="nisaki")

@app.route("/agGordios/")
def agGordios():
    return render_template("agGordios.html", title="ag.gordios")

@app.route("/arkoudilas/")
def arkoudilas():
    return render_template("arkoudilas.html", title="arkoudilas")

@app.route("/erimitis/")
def erimitis():
    return render_template("erimitis.html", title="erimitis")

@app.route("/loggas/")
def loggas():
    return render_template("loggas.html", title="loggas")

@app.route("/canal/")
def canal():
    return render_template("canal.html", title="canal")

@app.route("/ermones/")
def ermones():
    return render_template("ermones.html", title="ermones")

@app.route("/giannades/")
def giannades():
    return render_template("giannades.html", title="giannades")

@app.route("/makrades/")
def makrades():
    return render_template("makrades.html", title="makrades")

@app.route("/Cape_Drastis/")
def cape():
    return render_template("Cape_Drastis.html", title="cape_drastis")

@app.route("/MonRepos/")
def monRepo():
    return render_template("MonRepos.html", title="MonRepos")

@app.route("/nimfes/")
def nimfes():
    return render_template("nimfes.html", title="nimfes")

@app.route("/oldFortress/")
def oldFort():
    return render_template("oldFort.html", title="oldFortress")

@app.route("/Porto Timoni/")
def porto():
    return render_template("porto_timoni.html", title="Porto Timoni")

@app.route("/Gastouri/")
def gastouri():
    return render_template("Gastori.html", title="Gastouri")

@app.route("/perama/")
def perama():
    return render_template("perama.html", title="Perama")

@app.route("/stavros/")
def stavros():
    return render_template("stavros.html", title="Stavros")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Αν δεν υπάρχει μεταβλητή PORT, χρησιμοποίησε 5000
    app.run(host='0.0.0.0', port=port)
