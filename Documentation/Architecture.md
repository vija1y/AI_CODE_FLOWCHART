# Architecture

```
┌─────────────┐   HTTPS/JWT    ┌──────────────────────────────┐
│  Browser    │ ─────────────▶ │  Flask App (app.py)          │
│  Bootstrap  │                │   routes/   services/        │
│  Monaco     │                │   models/   database/        │
│  Mermaid.js │ ◀───────────── │                              │
└─────────────┘                └────┬──────────┬──────────────┘
                                    │          │
                              MySQL │          │ HTTPS
                                    ▼          ▼
                            ┌──────────────┐ ┌────────────────┐
                            │   MySQL DB   │ │ Google Gemini  │
                            │ users,       │ │ (genai SDK)    │
                            │ sessions     │ └────────────────┘
                            └──────────────┘
                                    ▲
                                    │ joblib
                            ┌──────────────┐
                            │ ML/          │
                            │ DecisionTree │
                            └──────────────┘
```

## Request flow examples

**Code → Flowchart**
1. Browser POSTs `{code, language}` with JWT.
2. `services/code_to_flowchart.py` parses code into Mermaid syntax.
3. Result saved in `learning_sessions`.
4. Mermaid.js renders SVG client-side.

**Classify logic**
1. POST `/api/classify-logic` with `{code}`.
2. `services/ml_service.py` loads `logic_classifier.pkl` once,
   extracts 6 features, predicts class + confidence.
3. Result saved to history.

**Explain code (Gemini)**
1. POST `/api/explain-code` with `{code}`.
2. `services/gemini_service.py` calls `gemini-1.5-flash` with a tutoring prompt.
3. Text response saved to history and shown in the AI tab.

## Security

- bcrypt password hashing
- JWT (HS256) with configurable expiry
- All non-auth endpoints behind `@auth_required`
- CORS enabled for local dev
- SQL via parameterized queries (mysql-connector)
