# Prawobiorca

Prawobiorca is an application developed within the WMS_DEV science club at the Wrocław University of Science and Technology.
Its goal is to help students defend and assert their rights.

The core part of the application is a regulations search engine. It allows collecting information in a simple and accessible way by entering queries, which are then processed based on their meaning rather than exact text matching.

Plans include:
- **Application Generator** - create elegant PDF documents by simply describing what you want to achieve.
- **Court Judgments Search Engine** - check if other students have defended their cases in court and what the outcomes were.
- **Court Judgments Summarizer** - easily extract important facts from a sea of legal jargon!
- **Dean's Office Simulator** - practice in front of a computer to avoid stress at the counter.

## How to Contribute

1. **Clone the project and install dependencies**, preferably with [uv](https://docs.astral.sh/uv/):
    ```sh
    uv sync --all-groups
    ```

2. **Set up the commit hook**:
    ```sh
    git config core.hooksPath .githooks
    ```

3. **Open the documentation**:
    ```sh
    zensical serve
    ```
    - Read the section about **Workflow**, especially regarding the commit format.
    - Read about **Project Architecture**, especially the coding rules.

4. **Develop your code**:
    - Write your code on a feature branch.

5. **Submit**:
    - If everything works, push your code to the repository (remember to do it on a feature branch) and contact **Eryk Mikołajewicz** for a code review.

## Running the Application
To check how the application works, launch it using the script below. Note that you must have **Podman** installed for it to work!
Firstly activate virtual environment
- on Linux:
```bash
source .venv/bin/activate
```
- on Windows:
```powershell
.venv/Scripts/activate
```

Start with building main service image with:
```sh
podman image build --tag=prawobiorca-backend .
```

next step build supporting service:

```sh
python cicd/scripts/build_text_transformator.py
```

Then run:
```sh
python cicd/scripts/run_locally.py
```

## Initialize relational database
To initialize tables in a database, use command:
```sh
python -m alembic upgrade head
```

Then, seed the database with data:
```sh
python cicd/init/seed_relational_db.py
```

## Initialize vector db
This step can last some time

```sh
python cicd/init/seed_vector_db.py
```

Then visit the main application page:
[http://127.0.0.1:8000/](https://127.0.0.1:8000/)

Or view the Swagger documentation:
[http://127.0.0.1:8000/docs](https://127.0.0.1:8000/docs)
