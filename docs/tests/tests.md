# Test Writing Instructions

## Scope of Tests

Within the project, we maintain the following types of tests:

- **Unit tests**
- **Integration tests**
- **E2E tests** are not currently implemented. Once GUI development starts, they will likely be written and placed in the GUI repository, probably using the `playwright` library.

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
- `tests/integration/conftest.py`

Detailed documentation for these files can be found on separate documentation pages.  
Other `conftest.py` files are documented with docstrings inside the files themselves.

### Test Data File

- The `tests/test_consts.py` file contains example test data, for example,
STRONG_PASSWORD = "StrongPassword12;"

- Place recurring, valid data used for success scenarios there.

## Unit Tests

Unit tests are created by the developer responsible for implementing a given functionality (e.g., based on a Jira story).

In unit tests, you should only test:
- Use cases within the application layer.
- Domain services and entities/value objects (provided they exhibit internal behaviors or logic)
- Repositories/Ports - only in special cases (sophisticated mapping logic).
- Endpoints - only when verifying custom Pydantic validation logic.

All external services should be mocked in unit tests, as well as other application parts as needed.

## Integration Tests

Integration tests are prepared by developers, with help from other team members if needed. 

### Review Checklist

- Are success scenarios tested?
- Are potentially dangerous situations tested (e.g., connection errors that could lead to data inconsistency)?
- Is the full functional scope covered without duplication?
- Are fixtures used appropriately without duplication/misuse?

Please note that during these tests, storage and external services are running in containers, but the application itself runs locally to allow for the mocking of its specific components.

### Integration Test Scope

- The entire path is tested: from endpoint call to response.
- Do not mock services that can be recreated locally (PostgreSQL, text-transformator) — use `testcontainers`.
- Other services (e.g., cloud storage, LLM conversations) should be mocked.
- All integration tests should use shared container instances (due to their initialization time).
- Each test should prepare its own test environment (e.g., insert data into the database) and clean up after itself.
- Tests must be fully independent of each other.
- It’s recommended to use a try block with cleanup in `finally` to ensure container state consistency even on test failure.
- **Before creating integration tests, carefully review the fixture documentation in `tests/integration/conftest.py`.**

When writing tests, use existing examples from the repository as a reference.
