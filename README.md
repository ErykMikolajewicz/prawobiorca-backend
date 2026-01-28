# Prawobiorca


## How to contribute:

- Clone project, then install dependencies, preferably with [uv](https://docs.astral.sh/uv/)
```bash
uv sync --all-groups
```

- Run script to set commit hook
```bash
git config core.hooksPath .githooks
```

- Open docs via command:
```bash
mkdocs serve
```

- Read fragment about Workflow, especially about commit format

- Read about project architecture, especially codding rules

- Write your code to a feature branch.

- If everything work push your code to repo, remember to do it on a feature branch, and call me (Eryk Mikołajewicz) about code review


If you want check how application is working use 2 scripts to launch it:
bash/run_external_services.sh
bash/graian_run.sh
Then go on:
https://127.0.0.1:8000/docs#/
to see app swagger
You have to had podman installed, to it worked!