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
Firstly, activate a virtual environment
- on Linux:
```bash
source .venv/bin/activate
```
- on Windows:
```powershell
.venv/Scripts/activate
```

Start with building images with:
```sh
poe build_images
```

Then run:
```sh
poe run_locally
```

## Initialize databases
```sh
poe init_databases
```
This command may take a while, it is making some hard extraction from PDFs.

Then visit the main application page:
[http://127.0.0.1:8000/](https://127.0.0.1:8000/)

Or view the Swagger documentation:
[http://127.0.0.1:8000/docs](https://127.0.0.1:8000/docs)
