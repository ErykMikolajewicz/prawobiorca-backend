# Prawobiorca


## How to contribute:

- Clone project, then install dependencies, preferably with [uv](https://docs.astral.sh/uv/)
```bash
uv sync --all-groups
```

- Open docs via command:
```bash
mkdocs serve
```

- Read fragment about Workflow, especially about commit format

- Read about project architecture, especially codding rules

- Write your code to a feature branch.

- Format code in repo:
```bash
isort .
black .
```

- run unit tests via:
```bash
python -m pytest tests/unit
```

- If everything work push your code to repo, remember to do it on a feature branch, and call me (Eryk Mikołajewicz) about code review