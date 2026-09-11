# Civil QuantEstimate

AI-assisted construction **quantity takeoff** tool built with Streamlit + Groq API.
Hackathon MVP — calculates material quantities only (no cost yet).

## Modules
- Brickwork / Masonry
- Plaster
- Concrete / RCC
- Steel / BBS
- AI Assistant (Groq) — explains formulas and last result

## Project structure
```
civil_estimator/
├── app.py                  # Streamlit UI + page routing
├── requirements.txt
├── utils/
│   ├── calculations.py     # all formulas (civil teammate: edit here)
│   ├── data.py              # mix ratios, brick size, wastage %, constants
│   └── groq_helper.py       # Groq API wrapper for AI Assistant tab
└── .streamlit/
    └── secrets.toml.example
```

## 1. Run locally

```bash
# clone your repo
git clone https://github.com/<your-username>/<your-repo>.git
cd civil_estimator

# create virtual env (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# add your Groq key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real GROQ_API_KEY

# run
streamlit run app.py
```

App opens at `http://localhost:8501`.

## 2. Get a free Groq API key
1. Go to https://console.groq.com
2. Sign up / log in
3. Go to **API Keys** → **Create API Key**
4. Paste it into `.streamlit/secrets.toml` as `GROQ_API_KEY = "..."`
5. **Never commit this file** — it's already in `.gitignore`.

## 3. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - Civil QuantEstimate MVP"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 4. Deploy (Streamlit Community Cloud — free)
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **New app** → select your repo, branch `main`, main file `app.py`
4. Under **Advanced settings → Secrets**, paste:
   ```
   GROQ_API_KEY = "your_real_key_here"
   ```
5. Click **Deploy** — you get a live URL like `your-app.streamlit.app`

## Team split suggestion
- **Civil teammate:** owns `utils/data.py` and `utils/calculations.py` — verify formulas, mix ratios, wastage %, brick sizes against standard practice.
- **CS teammate:** owns `app.py`, `utils/groq_helper.py`, GitHub, and deployment.

## Roadmap (post-hackathon)
- Add material rates + labour rates → cost estimation module
- Export results as PDF/BOQ
- Save/load projects
