# Fixtures used in integration tests

It was deemed that the approach used in the integration tests could raise legitimate questions; therefore, it was decided to add an additional explanatory section at the beginning.

## Service connections

In the tests, connections to asynchronous services are duplicated:

- First connection – used to override the connection in FastAPI.

- Second connection – used to initialize test data and, if necessary, restore the database to its initial state.

This solution results from issues with sharing an asynchronous connection between the tests and the FastAPI application.
To my knowledge, asynchronous tests in the pytest framework are run in separate threads. As a result, problems arise from having different event loops in individual threads.

Synchronous connections can be shared without any additional problems.
Alternative solution

It would probably be possible to override FastAPI’s event loop with pytest’s event loop.
However, it was decided that:

- it could lead to unexpected errors,

- it would require too much interference with the FastAPI framework.

## Drawbacks of the current solution

The currently used solution is satisfactory, although it has two major drawbacks:

- Code duplication – in tests, two dependencies must be used instead of one.

- Lack of transaction sharing – between data initialization and application operations. This makes it impossible to clean up the database by rolling back the transaction at the end. It requires manual cleanup by the users.

## Solution summary

- The adopted approach, despite some drawbacks, allows for asynchronous integration testing with acceptable inconveniences.

- There is also a slight benefit in terms of increased consistency in the testers’ approach, as they must manually ensure the proper state of all databases, since key-value does not support transactions anyway.

## Information about individual fixtures

::: integration.conftest