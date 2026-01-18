# Project Workflow

## 1. Team Collaboration

When additional team members join the project:

- **Taiga** is introduced for task and story management.
- **Definition of Done:**
    - A story is considered complete when its status is changed in Taiga by project manager, 
    - or after passing code review and integration tests (for backend-only features).

## 2. Branching Model (Git)

The repository maintains the following main branches:

- `dev` – Main development branch where developers merge their changes.
- `feature/*` – Per-story (feature/task) branches for implementing individual functionalities.
- `test` – Branch used for automatic deployment to the test environment; accessible to manual testers, clients, and beta testers.
- `main` – Main production branch for production releases.

## 3. Workflow

- **Task Creation in Taiga**  
    Project Manager creates a new story (feature/task) in Taiga.

- **Working on the Task**  
    A branch `feature/<story-name>` is created.  
    The developer implements the feature and prepares unit tests.

- **Merging to dev**  
    After development and initial testing, the feature branch is merged (PR) into `dev`.

- **Integration Testing**  
    A designated developer prepares integration tests for new or modified components.

- **Merging to test**  
    After successful integration tests and code review, code from `dev` is merged into `test`.  
    The `test` branch is automatically deployed to the test environment.

- **E2E/Manual Testing**  
    After successful E2E/manual testing, the approved code is merged into `main`.

- **Production Release**  
    Code from `main` is deployed to the production environment according to business needs (e.g., new features, critical fixes).

### 3.1 Exceptions

- Branches may be created directly from `main`, and dedicated test branches may be used for urgent fixes observed in production; however, all changes must undergo full testing and code review before merging.
- Optionally, Test Driven Development (TDD) can be applied—writing tests before code—though not required for every task.

## 4. Additional Guidelines

- Every change must undergo code review (including test quality).
- Automated tests run on every PR to `dev` and `main`.
- Commit messages follow the **Conventional Commits** specification.
- Every feature branch is named according to the Jira task number and description.
- Documentation is updated as needed, at the latest in the sprint following feature implementation.

## 5. Commit Standard: Conventional Commits

**Format:**

`<type>[scope]: <short description>`

[longer description]

[breaking changes/issues]

**Common commit types:**

- `feature` – New functionality
- `bugfix` – Bug fix
- `chore` – Technical changes (e.g., dependency upgrades)
- `docs` – Documentation changes
- `refactor` – Code refactoring, including performance improvements
- `test` – Add or improve tests
- `style` – Changes that don’t affect logic (e.g., formatting, whitespace)

**Versioning and Commits:**

- `bugfix`, `docs`, `test`, `style` – Increment the patch version (X.Y.Z)
- `feature`, `refactor`, `chore` – Increment the minor version (X.Y.Z)
- **Breaking changes:** Increment the major version (X.Y.Z). Breaking changes should be prepared over several commits on a dedicated branch.
