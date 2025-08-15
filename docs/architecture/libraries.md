# Library Overview

This document contains information about selected libraries along with the reasoning behind their use. It also compares alternative solutions — both other services and different implementation approaches.  
This means the section explains, for example, why a specific Postgres driver was chosen, but does not explain why Postgres was selected over MySQL.  
Justifications for choosing components that work with the application can be found in [external services](external_services.md).

If a library is used with a major version lower than the latest, a justification for this should also be provided.

Information about the currently used library versions can be found in the `pyproject.toml` file.

---

## Required dependencies

Below are the dependencies essential for the application to run, which should be included in the production release.

### asyncpg

Chosen as an asynchronous Postgres client, consistent with the philosophy of the [FastAPI](#fastapi) framework, which encourages asynchronous code.  
The downside is connection sharing issues during tests — see the [integration tests](/docs/tests/integration_fixtures.md) section for more details.

`asyncpg` was selected due to its top performance in benchmarks. `psycopg3` was also considered, as its support for both synchronous and asynchronous APIs could simplify certain operations (e.g., `alembic` migrations, which are already used as an optional dependency). However, performance was deemed more critical due to frequent database reads.

Switching the driver later should be relatively easy thanks to the use of the [SQLAlchemy](#sqlalchemyasyncio) ORM.

---

### bcrypt

A password hashing library chosen for security reasons.  
`bcrypt` provides strong resistance to brute-force attacks and is easy to use.

Alternatives:  
- **`hashlib`** (Python standard library) — lacks salt support, which would increase implementation complexity or expose hashes to rainbow table attacks.  
- **`passlib`** — supports `argon2`, which is more secure than `bcrypt`. However, it was considered unnecessary, and its longer hashing time could negatively impact the user experience during login.

---

### email-validator

An optional Pydantic dependency used to validate email addresses in the application.

---

### fastapi

The main framework used in the project. Selected for:  
- high performance due to asynchronous programming support,  
- data validation via Pydantic,  
- automatic documentation generation (Swagger),  
- easier testing through dependency injection.

Alternatives:  
- **Flask** — weaker asynchronous support and requires installing numerous plugins for basic functionality.  
- **Django** — overly complex for the project’s needs (e.g., HTML file hosting, rigid ORM structure). The application is intended to operate as a set of SOA services communicating via REST API, where FastAPI is a lighter, more flexible option.

---

### google-cloud-storage

The official Google Cloud client for file handling, chosen because the application uses GCP for file storage.  
The downside is that it is synchronous — currently, asynchronous wrappers must be created. If an async version becomes available, implementing it would be a significant improvement.

---

### granian

An HTTP server written in Rust, supporting HTTP/2.  
Pros: high performance.  
Cons: harder debugging compared to Python-based servers (e.g., Hypercorn).

---

### pydantic-settings

A library for managing application configuration.  
Pros:  
- type and value validation,  
- centralized configuration,  
- minimal impact on application size (Pydantic is already in use).  

Alternatives were not extensively researched.

---

### python-multipart

A library for handling file uploads in applications based on [FastAPI](#fastapi).

---

### qdrant-client

The official client for the Qdrant database — essentially the only option.

---

### redis

The official client for Redis — standard solution.

---

### sqlalchemy[asyncio]

The most popular ORM in Python.  
Pros:  
- rich functionality and documentation,  
- production maturity,  
- built-in connection pooling.  

Cons:  
- steep learning curve,  
- documentation covers both legacy (1.4) and modern (2.x) versions, which can be confusing.  

Alternative: **Tortoise ORM** — natively asynchronous and simpler to use, though less popular.