# Secure Phishing URL Detection Pipeline

A small DevSecMLOps project that statically analyzes URL text with a Random Forest classifier. It never visits submitted URLs.

## Local setup

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python -m src.train_model
pytest -q
```

## Run locally

Terminal 1:

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2:

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501`. API docs: `http://localhost:8000/docs`. Health check: `http://localhost:8000/health`.

## API test

```bash
curl -X POST http://localhost:8000/predict \\
  -H 'Content-Type: application/json' \\
  -H 'X-API-Key: change-this-demo-key' \\
  -d '{"url":"http://secure-login-verify-account.example.com"}'
```

## Docker deployment

```bash
cp .env.example .env
# Edit .env and replace API_KEY with your own value
docker compose up --build
```

Open `http://localhost:8501` and `http://localhost:8000/docs`.

## Security checks

```bash
bandit -r src
pip-audit -r requirements.txt
```

## Demo URLs

Use these as text examples only; do not open them:

- Legitimate: `https://www.wikipedia.org`
- Phishing-like: `http://secure-login-verify-account.example.com`
- Invalid: `hello world`
