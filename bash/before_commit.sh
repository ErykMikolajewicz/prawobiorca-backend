bandit -r app/
read -p "Press Enter, to continue."
ruff check .
python -m pytest tests/unit
