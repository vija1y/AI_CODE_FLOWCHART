# AI-Enhanced Code & Flowchart Learning System

Full-stack educational tool: convert code ↔ flowcharts, classify logic with a
scikit-learn Decision Tree, and explain code with Google Gemini.

## Stack

- **Backend:** Flask (Python 3.10+), JWT auth, MySQL
- **Frontend:** HTML + Bootstrap 5 + vanilla JS, Monaco Editor, Mermaid.js
- **ML:** scikit-learn DecisionTreeClassifier (5 logic classes)
- **GenAI:** Google Gemini API

## Folder layout

```
Backend/   Flask app, routes, services, models, templates(HTML), static( CSS , js ) 
ML/        dataset + training script + saved model
Documentation/  README, architecture notes
```

## 1. Prerequisites

- Python 3.10+
- MySQL 8.x running locally
- Google Gemini API key (https://aistudio.google.com/app/apikey)

## 2. Setup

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit DB + Gemini key
```

Create the database (the app will also auto-create it on first run if the user has privileges):

```sql
CREATE DATABASE ai_code_flowchart CHARACTER SET utf8mb4;
```

## 3. Train the ML model

```bash
cd ..
python ML/train_model.py
# -> ML/logic_classifier.pkl
```

## 4. Run

```bash
cd Backend
python app.py
# http://localhost:5000
```

Open `/register`, create an account, then explore:

- `/dashboard` – stats and recent sessions
- `/editor` – Monaco editor → flowchart / classify / explain / suggest
- `/flowchart-to-code` – Mermaid → Python via Gemini
- `/history` – browse and delete past sessions
- `/profile` – account info

## API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/register` | – | Create user, returns JWT |
| POST | `/api/login` | – | Returns JWT |
| GET  | `/api/me` | ✓ | Current user |
| POST | `/api/code-to-flowchart` | ✓ | Code → Mermaid |
| POST | `/api/flowchart-to-code` | ✓ | Mermaid → code (Gemini) |
| POST | `/api/classify-logic` | ✓ | ML logic classification |
| POST | `/api/explain-code` | ✓ | Gemini step-by-step |
| POST | `/api/generate-summary` | ✓ | Gemini short summary |
| POST | `/api/suggest-improvements` | ✓ | Gemini optimization tips |
| GET  | `/api/history` | ✓ | All learning sessions |
| DELETE | `/api/history/<id>` | ✓ | Delete one session |

Send `Authorization: Bearer <token>` on protected endpoints.

## ML features

The Decision Tree uses 6 features per snippet:

```
num_conditions, num_loops, num_functions,
num_operators, code_length, complexity_score
```

Labels: `Sequential`, `Conditional`, `Looping`, `Nested`, `FunctionBased`.

Retrain anytime by editing `ML/dataset.csv` and rerunning `train_model.py`.

## Notes

- The code→flowchart converter is a heuristic line parser — robust for
  educational snippets, not a full compiler.
- The Gemini calls require `GEMINI_API_KEY` in `.env`.
- Passwords are hashed with bcrypt; tokens are HS256 JWTs.
