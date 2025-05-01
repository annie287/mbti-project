from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import json
import os
import math
app = Flask(__name__)
app.secret_key = 'your_secret_key'

with open("mbti_profiles.json", "r") as f:
    mbti_profiles = json.load(f)

with open ('mbti_data.json', 'r')as f:
    mbti_data = json.load(f)

with open ('mbti_colour.json', 'r')as f:
    mbti_colour = json.load(f)

MATCHING = {
    'INFP': {
        'best_match': ['ENFJ', 'ENTJ'],
        'worst_match': ['ESTP']
    },
    'ENFP': {
        'best_match': ['INFJ', 'INTJ'],
        'worst_match': ['ISTJ']
    },
    'INFJ': {
        'best_match': ['ENFP', 'ENTP'],
        'worst_match': ['ESTP']
    },
    'ENFJ': {
        'best_match': ['INFP', 'ISFP'],
        'worst_match': ['ISTP']
    },
    'INTJ': {
        'best_match': ['ENFP', 'ENTP'],
        'worst_match': ['ESFP']
    },
    'ENTJ': {
        'best_match': ['INFP', 'INTP'],
        'worst_match': ['ISFP']
    },
    'INTP': {
        'best_match': ['ENTJ', 'ESTJ'],
        'worst_match': ['ESFJ']
    },
    'ENTP': {
        'best_match': ['INFJ', 'INTJ'],
        'worst_match': ['ISFJ']
    },
    'ISFP': {
        'best_match': ['ENFJ', 'ESTJ', 'ESFJ'],
        'worst_match': ['ENTJ']
    },
    'ESFP': {
        'best_match': ['ISFJ', 'ISTJ'],
        'worst_match': ['INTJ']
    },
    'ISTP': {
        'best_match': ['ESFJ', 'ESTJ'],
        'worst_match': ['ENFJ']
    },
    'ESTP': {
        'best_match': ['ISFJ', 'ISTJ'],
        'worst_match': ['INFJ']
    },
    'ISFJ': {
        'best_match': ['ESFP', 'ESTP'],
        'worst_match': ['ENTP']
    },
    'ESFJ': {
        'best_match': ['ISFP', 'ISTP'],
        'worst_match': ['INTP']
    },
    'ISTJ': {
        'best_match': ['ESFP', 'ESTP'],
        'worst_match': ['ENFP']
    },
    'ESTJ': {
        'best_match': ['INTP', 'ISFP', 'ISTP'],
        'worst_match': ['INFP']
    },
}



@app.route('/')
def home():
    return render_template('index.html')

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mbti_type TEXT NOT NULL,
        best_match TEXT,
        worst_match TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        mbti_type TEXT
    )
    ''')
    conn.commit()
    conn.close()
init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and user[2] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()

            session['username'] = username
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists! Please choose another one."
        
    return render_template('register.html')  

@app.route('/handbook')
def handbook():
    return render_template(
        'handbook.html', 
        profiles=mbti_profiles
    )

@app.route('/aboutyou')
def about_you():
    if 'username' not in session:
        return redirect(url_for('login'))  
    username = session['username']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT mbti_type FROM users WHERE username = ?', (username,))
    user_mbti = c.fetchone()
    conn.close()

    if user_mbti:
        mbti_type = user_mbti[0]
        profile = mbti_profiles.get(mbti_type, {})
        return render_template(
            'aboutyou.html', 
            username=username, 
            mbti_type=mbti_type, 
            profile=profile
            )
    else:
        return "No MBTI profile found for you yet!"


@app.route('/match_detail')
def match_detail():
    match_type = request.args.get('type')
    relation = request.args.get('relation')  # best or worst

    detail_text = ""

    if relation == 'best':
        detail_text = f"{match_type} is your Best Match! You complement each other's strengths and cover each other's weaknesses. 🌟"
    else:
        detail_text = f"{match_type} might be a Challenging Match. You have very different priorities and approaches. 💔"

    return render_template('match_detail.html', 
                            match_type=match_type,
                            relation=relation,
                            detail_text=detail_text)

@app.route('/pairing')
def pairing():
    mbti = request.args.get('mbti', '').upper()
    best_match = MATCHING.get(mbti, {}).get('best_match', [])
    worst_match = MATCHING.get(mbti, {}).get('worst_match', [])
    strengths = mbti_data.get(mbti, {}).get('strengths', [])
    weaknesses = mbti_data.get(mbti, {}).get('weaknesses', [])
    profile = mbti_profiles.get(mbti, {})
    bg_color = mbti_colour.get(mbti, {})

    return render_template('pairing.html', 
                           mbti=mbti, 
                           best_match=best_match, 
                           worst_match=worst_match,
                           strengths=strengths,
                           weaknesses=weaknesses,
                           profile=profile,
                           bg_color=bg_color
                        )

@app.route('/explore-pairing')
def explore_pairing():
    return render_template(
        'explore_pairing.html',
        matching=MATCHING
        )

@app.route('/submit_mbtitest', methods=['POST', 'GET'])
def submit_mbtitest():
    if request.method == 'GET':
        return redirect(url_for('home'))
    
    mbti = request.form['mbti'].upper() #Get users mbti type.

    #fetch best and worst match mbti types.
    best_match = MATCHING.get(mbti, {}).get('best_match', [])
    worst_match = MATCHING.get(mbti, {}).get('worst_match', [])

    strengths = mbti_data.get(mbti, {}).get('strengths', [])
    weaknesses = mbti_data.get(mbti, {}).get('weaknesses', [])

    profile = mbti_profiles.get(mbti, {})
    bg_color = mbti_colour.get(mbti, {})

    # Store the result in the database.
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO results (mbti_type, best_match, worst_match)
    VALUES (?, ?, ?)
    ''', (mbti, ', '.join(best_match), ', '.join(worst_match)))
    conn.commit()
    conn.close()

    return render_template(
        'result.html', 
        mbti=mbti, 
        best_match=best_match, 
        worst_match=worst_match, 
        strengths=strengths, 
        weaknesses=weaknesses, 
        profile=profile,
        bg_color=bg_color
    )

@app.route('/results')
def view_results():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM results')
    rows = c.fetchall()
    conn.close()
    return render_template('result.html', rows=rows)

@app.route('/history')
def view_history():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT mbti_type FROM results')
    rows = c.fetchall()
    conn.close()

    mbti_counts = {}
    for row in rows:
        mbti = row[0]
        if mbti:
            mbti_counts[mbti] = mbti_counts.get(mbti, 0) + 1

    return render_template('history.html', mbti_counts=mbti_counts) 

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))