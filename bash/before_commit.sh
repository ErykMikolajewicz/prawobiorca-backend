bandit -r app/
read -p "Press Enter, to continue."
isort .
black .
python -m pytest tests/unit
