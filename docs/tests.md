# Test Writing Instructions

## Scope of Tests

Within the project, we maintain the following types of tests:

- **Unit tests**
- **Integration tests**
- **E2E tests** are not currently implemented. Once GUI development starts, they will likely be written and placed in the GUI repository, probably using the `playwright-python` library.

## Technology Stack

The following technologies are used in the project:

- Standard `unittest` library (mainly for patching)
- `pytest` for test management
- `pytest-asyncio` for asynchronous test support
- `testcontainers` for integration tests

Currently, there are **no plans to use plugins** for test parallelization or data generation libraries such as `faker`. Adding new testing libraries requires prior agreement with the team.

## Configuration Files

- The main project configuration is stored in **`pyproject.toml`**.
- Each test directory level contains a **`conftest.py`** file with commonly used fixtures.

### Key files include:
- `tests/conftest.py`
- `tests/unit/conftest.py`
- `tests/integration/conftest.py`

Detailed documentation for these files can be found on separate documentation pages.  
Other `conftest.py` files are documented with docstrings inside the files themselves.

### Test Data File

- The `tests/test_consts.py` file contains example test data, for example:
STRONG_PASSWORD = "StrongPassword12;"

- Place recurring, valid data used for success scenarios there.

## Unit Tests

Unit tests are created by the developer responsible for implementing a given functionality (e.g., based on a Jira story).

In unit tests, you should especially test:
- Endpoints (mainly API stability), also Pydantic models (validators and validation logic)
- Business services in `app/domain/services` (core business logic; focus on coverage here)
- Utility services in `app/infrastructure/utilities`
- Repositories – in particularly complex cases (most repository testing should be handled by integration tests)

All external services should be mocked in unit tests, as well as other application parts as needed (e.g., endpoint tests should not directly invoke services).

After writing unit tests, request a code review from another developer — the goal is to evaluate functional coverage and consider negative and edge-case scenarios.

## Integration Tests

### Review Checklist

- Are success scenarios tested?
- Are edge cases tested?
- Are exceptions/failures tested?
- Is the full functional scope covered without duplication?
- Are fixtures used appropriately without duplication/misuse?

Integration tests are prepared by a designated developer as a separate Jira task.

### Integration Test Scope

- The entire path is tested: from endpoint call to response.
- Do not mock services that can be recreated locally (e.g., Redis, PostgreSQL) — use `testcontainers`.
- Other services (e.g., cloud storage, LLM conversations) should be mocked.
- All integration tests should use shared container instances (due to their initialization time).
- Each test should prepare its own test environment (e.g., insert data into the database) and clean up after itself.
- Tests must be fully independent of each other.
- It’s recommended to use a try block with cleanup in `finally` to ensure container state consistency even on test failure.
- **Before creating integration tests, carefully review the fixture documentation in `tests/integration/conftest.py`.**

If necessary, initial data for test containers can be set up using Alembic migrations. Any changes in this area must be agreed with the team.

When writing tests, use existing examples from the repository as a reference.
