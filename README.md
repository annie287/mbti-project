# mbti-project
A MBTI matching website, you would know yourself better here
#### 🔜Video demo: https://youtu.be/Dmhou08vHqc?si=AVPfRN03BqNGCzT2
#### Description: This is a MBTI matching website, users can find their best matches and worst matches, discover their own type of animal and celebrity type, view the mind map of historical users' types.
## Features:
1. Select your own MBTI type
2. Visualise your spirit animals for each MBTIs in handbook
3. Mind-map based visualisation of visitor history using **vis.js**
4. User registration and Login with session tracking
5. Deployed with Render

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript (vis)
- **Backend:** Python flask
- **Database:** SQL
- ** Deployment:** Render

## Project Structure
```bash
mbti-project/
├── static/                 # CSS, images, etc.
├── templates/              # HTML templates
├── app.py                  # Flask backend
├── mbti_profiles.json      # MBTI data with animals & quotes
├── mbti_data.json          # Strengths & weaknesses
├── mbti_colour.json        # Background colours
├── requirements.txt        # Python dependencies
└── README.md

