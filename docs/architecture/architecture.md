# Application Architecture

## Introduction
This project is about the backend of a web application, for which a JavaScript client is planned, but temporarly due to lack of frontend developers HTML views are made.

The main framework is FastAPI. It is intended to run in Podman containers, which may cause issues when running on Windows systems.

In the production environment, the application is intended to can be run both on premise or in cloud. Dependence on a specific cloud provider is acceptable, but should be avoided whenever possible, also on premise alternative should be ensured, but some non-critical functions can be disabled in that environment.

The main part of the code is located in the `app` folder.

The following sections of this document contain information about:

  - [coding rules](coding_rules.md),
  - [rationale for library selection](libraries.md),
  - [external services description](external_services.md),
  - [Project Structure](#project-structure)

## Project Structure

The application follows the **Clean Architecture** principles, enforcing separation of concerns and dependency rules. The code is organized into concentric layers, where inner layers contain business logic and are independent of outer layers (infrastructure, frameworks).

### `app/domain`
This folder represents the core of the application and contains the **Enterprise Business Rules**. It is the innermost layer and has no dependencies on other layers.
- **Entities**: Domain objects with state and behavior.
- **Value Objects**: Immutable objects defined by their attributes.
- **Services**: Logic that doesn't naturally fit within a single entity.
- **Ports & Interfaces**: Abstract definitions for repositories and external services (found in `ports/` and `interfaces/`), implemented by the Infrastructure layer.
- **Exceptions**: Domain-specific exceptions.

### `app/application`
This layer contains the **Application Business Rules**. It orchestrates the flow of data to and from the domain entities and directs those entities to use their Critical Business Rules to achieve the goals of the use case.
- **Use Cases**: Specific application actions.
- **DTOs (Data Transfer Objects)**: Data structures used to pass data between the application layer and framework. Use to do not contain business logic part, by framework, like pydantic.

### `app/infrastructure`
This layer acts as an adapter, implementing the interfaces (Ports) defined in the Domain and Application layers. It handles technical details and communication with external systems.
- **Repositories**: Implementations of repository interfaces (e.g., `relational_db`, `key_value_db`, `vector_db`).
- **File Storage**: Implementations for file handling.
- **External Services**: Adapters for third-party APIs (e.g., `embeddings_generator`).

### `app/framework`
This layer corresponds to the **Frameworks** (and partly Interface Adapters) layer. It contains tools and delivery mechanisms, specifically related to the web framework (FastAPI).
- **API**: REST API endpoints (Routers), request/response models, also HTMl responses.
- **Web**: HTML views - use Jinja2 framework.
- **Dependencies**: Dependency injection setup and wiring.

### `app/shared`
This folder contains common utilities and configuration shared across the application. While Clean Architecture emphasizes separation, some cross-cutting concerns reside here.
- **Settings**: Application configuration.
- **Constants & Enums**: Shared static values.
- **Logging**: Logging configuration.
- **Exceptions**: Common base exceptions.

## Import Structure Rules

To maintain the integrity of Clean Architecture, strict rules regarding imports must be followed. The general rule is that dependencies point inwards.

- **`app/domain`**: This is the core. It **must not** import from `application`, `infrastructure`, or `framework`. It should only rely on standard Python libraries or specific standalone third-party libraries.
- **`app/application`**: Can import from `domain`. It **must not** import from `infrastructure` or `framework`.
- **`app/infrastructure`**: Can import from `application` (especially DTOs) and `domain`. It **must not** import from `framework`.
- **`app/framework`**: As the delivery mechanism and dependency injection root, it can import from anywhere. However, it should primarily import from `infrastructure` (for concrete implementations) and `application` (for Use Cases and DTOs).
- **`app/shared`**: Can be imported by any layer. However, `shared` itself should rarely import from other layers to avoid circular dependencies.

