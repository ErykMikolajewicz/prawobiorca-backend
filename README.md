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

## Generating and adding a certificate to the browser

Download tool to create certs from:
https://github.com/FiloSottile/mkcert/releases
Move it to the same directory as repo, and rename to mkcert.

Then create cert file, and key file:
```sh
./mkcert --cert-file certificate.crt --key-file private.key localhost 127.0.0.1
```

Install certificate in system trust store:
On linux previously install libnss3-tools
```bash
sudo apt install libnss3-tools
```

Then on both Windows and Linux:
```sh
./mkcert -install
```

If still not work add root certificate to your browser. The directory of cert you can find by:
```sh
./mkcert -CAROOT
```
Then find instruction, how add cert, for your browser

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

Then run:
```sh
python scripts/run_app.py
```

## Initialize relational database
To initialize tables in a database, use command:
```sh
python -m alembic upgrade head
```

Then, seed the database with data:
```sh
python scripts/seed_db.py
```

Then visit the main application page:
[https://127.0.0.1:8000/](https://127.0.0.1:8000/)

Or view the Swagger documentation:
[https://127.0.0.1:8000/docs](https://127.0.0.1:8000/docs)
