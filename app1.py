from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import get_flashed_messages
from flask_babel import Babel, gettext as _
import os 


app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['BABEL_DEFAULT_LOCALE'] = 'el'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)

babel = Babel(app)

@babel.select_locale
def get_locale():
    return session.get('lang', 'el')




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

@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))


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
        "image": "/static/img/arkoudilas/arkoudilas/icon1.jpg",
        "description": "arkoudilas",
        "url": "/arkoudilas"
    }]


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
    return render_template("vlaxerena.html", title="vlaxerena")

@app.route("/Nisaki/")
def nisaki():
    return render_template("Nisaki.html", title="nisaki")

@app.route("/agGordios/")
def agGordios():
    return render_template("agGordios.html", title="ag.gordios")

@app.route("/arkoudilas/")
def arkoudilas():
    return render_template("arkoudilas.html", title="arkoudilas")


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Αν δεν υπάρχει μεταβλητή PORT, χρησιμοποίησε 5000
    app.run(host='0.0.0.0', port=port)
