from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os
app = Flask(__name__)

with open("mbti_profiles.json", "r") as f:
    mbti_profiles = json.load(f)

with open ('mbti_data.json', 'r')as f:
    mbti_data = json.load(f)

with open ('mbti_colour.json', 'r')as f:
    mbti_colour = json.load(f)

MATCHING = {
    'ISTJ': {
        'best_match': ['ESFP'],
        'worst_match': ['ENFP']
    },
    'ISFJ': {
        'best_match': ['ESTP'],
        'worst_match': ['ENTP']
    },
    'INFJ': {
        'best_match': ['ENFP'],
        'worst_match': ['ESTP']
    },
    'INTJ': {
        'best_match': ['ENFP', 'INTP'],
        'worst_match': ['ESFP']
    },
    'ISTP': {
        'best_match': ['ESFJ'],
        'worst_match': ['ENFJ']
    },
    'ISFP': {
        'best_match': ['ESTJ'],
        'worst_match': ['ENTJ']
    },
    'INFP': {
        'best_match': ['ENFJ'],
        'worst_match': ['ESTP']
    },
    'INTP': {
        'best_match': ['ENTJ', 'ENFP'],
        'worst_match': ['ESFJ']
    },
    'ESTP': {
        'best_match': ['ISFJ'],
        'worst_match': ['INFJ']
    },
    'ESFP': {
        'best_match': ['ISTJ'],
        'worst_match': ['INTJ']
    },
    'ENFP': {
        'best_match': ['INFJ'],
        'worst_match': ['ISTJ']
    },
    'ENTP': {
        'best_match': ['INFJ'],
        'worst_match': ['ISFJ']
    },
    'ESTJ': {
        'best_match': ['ISFP'],
        'worst_match': ['INFP']
    },
    'ESFJ': {
        'best_match': ['ISFP', 'ISTP'],
        'worst_match': ['INTP']
    },
    'ENFJ': {
        'best_match': ['INFP', 'ISFP'],
        'worst_match': ['ISTP']
    },
    'ENTJ': {
        'best_match': ['INTP', 'ENFP'],
        'worst_match': ['ISFP']
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
    conn.commit()
    conn.close()
init_db()

@app.route('/handbook')
def handbook():
    return render_template('handbook.html')

@app.route('/aboutyou')
def about_you():
    return render_template('aboutyou.html')

@app.route('/peoplelikeyou')
def people_like_you():
    return render_template('peoplelikeyou.html')

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
    c.execute('SELECT * FROM results')
    results = c.fetchall()
    conn.close()
    return render_template('history.html', results=results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))