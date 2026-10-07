install:
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
train:
python -m src.train_model
run-api:
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
run-ui:
streamlit run frontend/app.py
test:
pytest -q
security:
bandit -r src
pip-audit -r requirements.txt
