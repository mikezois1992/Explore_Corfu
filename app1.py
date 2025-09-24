from flask import Flask, render_template, make_response, jsonify, request, redirect, url_for, flash, g, session

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import get_flashed_messages
import os 
from functools import lru_cache
import re
from bs4 import BeautifulSoup, Comment
import argostranslate.package as argos_pkg
import argostranslate.translate as argos

GREEK_REGEX = re.compile(r'[\u0370-\u03FF]')  # εύρεση ελληνικών χαρακτήρων

@lru_cache(maxsize=1)
def _installed_langs():
    return argos.get_installed_languages()

def _(text):
    target = request.cookies.get('language', 'en')  # default EN
    return translate_text(text, target_code=target)



def _find_language(code: str):
    for lang in _installed_langs():
        if getattr(lang, "code", None) == code:
            return lang
    return None

@lru_cache(maxsize=4)
def _get_translator(src_code: str, tgt_code: str):
    src = _find_language(src_code)
    tgt = _find_language(tgt_code)
    if not src or not tgt:
        return None
    try:
        return src.get_translation(tgt)
    except Exception:
        return None

def ensure_el_en_models(download_if_missing: bool = True):
    have_el_en = bool(_get_translator("el", "en"))
    have_en_el = bool(_get_translator("en", "el"))
    if have_el_en and have_en_el:
        return
    if not download_if_missing:
        return
    try:
        argos_pkg.update_package_index()
        for p in argos_pkg.get_available_packages():
            if {p.from_code, p.to_code} == {"el", "en"}:
                argos_pkg.install_from_path(p.download())
                _installed_langs.cache_clear()
                _get_translator.cache_clear()
    except Exception:
        pass

def _detect_lang(text: str) -> str:
    return "el" if GREEK_REGEX.search(text or "") else "en"

@lru_cache(maxsize=4096)
def translate_text(text: str, target_code: str) -> str:
    if not text:
        return text
    src = _detect_lang(text)
    if src == target_code:
        return text
    tr = _get_translator(src, target_code)
    if not tr:
        return text
    try:
        return tr.translate(text)
    except Exception:
        return text
try:
    ensure_el_en_models(download_if_missing=True)
except Exception:
    pass

# Provide access to the current language for templates


def get_locale():
    return request.cookies.get('language', 'en')  

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.get("/debug/argos")
def debug_argos():
    try:
        langs = _installed_langs()
        codes = [getattr(l, "code", "?") for l in langs]
        tr_el_en = bool(_get_translator("el", "en"))
        tr_en_el = bool(_get_translator("en", "el"))
        return {
            "cookie_language": request.cookies.get("language", "en"),
            "installed_codes": codes,
            "has_el_to_en": tr_el_en,
            "has_en_to_el": tr_en_el,
        }
    except Exception as e:
        return {"error": str(e)}, 500


@app.before_request
def _set_current_lang():
    # default ΕΛΛΗΝΙΚΑ όταν δεν υπάρχει cookie:
    g.current_lang = request.cookies.get("language", "el")

@app.after_request
def _translate_full_html_when_english(resp):
    try:
        p = request.path or ""
        if p.startswith("/static/") or p.startswith("/api/") or p.startswith("/lang/") or p.startswith("/debug/"):
            return resp
        status = getattr(resp, "status_code", 200)
        if status in (204, 304):
            return resp
        ct = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" not in ct:
            return resp
        try:
            resp.direct_passthrough = False
        except Exception:
            pass
        target = getattr(g, "current_lang", request.cookies.get("language", "el"))
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
    # ΜΟΝΟ όταν ζητάς Αγγλικά γίνεται καθολική μετάφραση
        if target != "en":
            return resp
        html = resp.get_data(as_text=True) or ""
        if not html.strip():
            return resp
        soup = BeautifulSoup(html, "html.parser")
        text_nodes = []
        greek_texts = []
        uniq_index = {}
        for node in soup.find_all(string=True):
            if isinstance(node, Comment):
                continue
            txt = str(node)
            if not txt.strip():
                continue
            parent = (node.parent.name or "").lower() if node.parent else ""
            if parent in ("script", "style", "code", "pre", "noscript"):
                continue
            # Κράτα ό,τι περιέχει ελληνικούς χαρακτήρες
            if GREEK_REGEX.search(txt):
                if txt not in uniq_index:
                    uniq_index[txt] = len(greek_texts)
                    greek_texts.append(txt)
                text_nodes.append(node)
        if not greek_texts:
            return resp  
        translated = [translate_text(t, "en") for t in greek_texts]
        # Αντικατάσταση στους κόμβους
        for node in text_nodes:
            idx = uniq_index[str(node)]
            node.replace_with(translated[idx])
        # Επιστροφή νέου HTML
        new_html = str(soup)
        resp.set_data(new_html)
        return resp
    except Exception:
        return resp

def _filter_autotranslate(s: str):
    # αν για οποιονδήποτε λόγο δεν υπάρχει g.current_lang (π.χ. εκτός request), πέφτουμε στο cookie ή 'el'
    target = getattr(g, "current_lang", request.cookies.get("language", "el"))
    return translate_text(s, target)

app.jinja_env.filters["autotranslate"] = _filter_autotranslate

@app.context_processor
def _inject_autotranslate():
    def autotranslate(s: str):
        return translate_text(s, g.current_lang)
    return {"autotranslate": autotranslate, "current_lang": g.current_lang}

app.jinja_env.filters["autotranslate"] = lambda s: translate_text(s, g.current_lang) #προαιρετικό  φίλτρο

def _home_redirect():
    # Προσπάθησε να επιστρέψεις εκεί που ήσουν
    if request.referrer:
        try:
            return redirect(request.referrer)
        except Exception:
            pass
    # Αλλιώς προσπάθησε γνωστά endpoints
    for ep in ("home", "index"):
        try:
            return redirect(url_for(ep))
        except Exception:
            continue
    # Τελευταίο fallback
    return redirect("/")


@app.get("/lang/<code>")
def switch_lang(code):
    code = (code or "").lower()
    if code not in ("el", "en"):
        code = "el"
    resp = make_response(_home_redirect())
    resp.set_cookie("language", code, max_age=60*60*24*90, path="/", samesite="Lax")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.get("/lang/reset")
def lang_reset():
    resp = make_response(_home_redirect())
    resp.delete_cookie("language", path="/")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.post("/api/translate_bulk")
def api_translate_bulk():
    """
    Δέχεται: {"items": ["κείμενο1", "κείμενο2", ...], "target": "en"|"el"}
    Επιστρέφει: {"ok": true, "items": ["μετάφραση1", "μετάφραση2", ...]}
    Η σειρά είναι 1:1 με την είσοδο.
    """
    data = request.get_json(force=True) or {}
    items = data.get("items", [])
    target = (data.get("target") or "en").strip().lower()
    out = []
    for s in items:
        s = s or ""
        out.append(translate_text(s, target))
    resp = jsonify({"ok": True, "items": out})
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

# Συμβατότητα με παλιά κουμπιά/φόρμες:
@app.get("/set_language/<lang>")
def legacy_set_language(lang):
    return switch_lang(lang)

@lru_cache(maxsize=1)
def _ready():
    return True  # τα μοντέλα τα εγκαταστήσαμε ήδη

def autodetect_and_translate(text: str, target_lang: str) -> str:
    _ready()
    has_greek = any('\u0370' <= ch <= '\u03FF' for ch in text)
    source = "el" if has_greek else "en"
    if source == target_lang:
        return text
    return argos_translate.translate(text, source, target_lang)

@app.post("/api/translate")
def api_translate():
    data = request.get_json(force=True) or {}
    text = data.get("q", "").strip()
    target = data.get("target", "en").strip()
    if not text:
        return jsonify({"ok": False, "error": "empty text"}), 400
    try:
        out = translate_text(text, target)
        return jsonify({"ok": True, "translatedText": out})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.context_processor
def inject_translator():
    return dict(_=_, get_locale=get_locale)


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
