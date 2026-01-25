# Application Architecture

## Introduction
This project is about the backend of a web application, for which a JavaScript client is planned.

The backend is written in Python, with the use of additional libraries written in C/C++ and Rust, such as Pydantic. The current Python version in use is 3.13. If compatibility issues arise, a downgrade to version 3.12 will be possible, although this is unlikely.

The main framework is FastAPI. The application will follow the REST architecture and will not host HTML files. It is intended to run in Podman containers, which may cause issues when running on Windows systems.

In the production environment, the application is intended to run in the cloud. Dependence on a specific cloud provider is acceptable, but should be avoided whenever possible.

The main part of the code is located in the `app` folder.

The following sections of this document contain information about:

  - [coding rules](coding_rules.md),
  - [rationale for library selection](libraries.md),
  - [external services description](external_services.md),
  - project structure description,
  - design patterns discussion.
