# Application Architecture

## 1. Introduction and System Overview

**Prawobiorca** is a modern backend platform providing intelligent legal search and document management capabilities. The system supports AI-assisted (semantic vector search) retrieval of legal acts, as well as case management and document drafting for authenticated users.

The system is designed to run in two primary environments:
- **Cloud (GCP / Google Cloud Platform)**: Utilizing containerized workloads with scale-to-zero capabilities for resource-heavy operations to optimize cost and resource allocation.
- **On-Premise**: Running containerized services using **Podman** / Docker.

---

## 2. System Architecture & Components

The architecture follows a **Monolith** pattern for core business logic, paired with **specialized microservices** for compute-heavy tasks:

```text
                            [Client / Vue]
                                  │
                                  │ (HTTP REST)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │                     core-service                       │
       │           (Auth, Cases, Files, Search Engine)          │
       └────┬─────────────────────────────┬─────────────────┬───┘
            │                             │                 │
      (Dispatches Task)                   │ (Generates      │ (Vector &
            |                             │  Query Embed)   │  Relational DB)
            │                             │                 │
            ▼                             ▼                 │
       ┌──────────┐              ┌──────────────┐           │
       │  Broker  │              │ embeddings-  │           │
       │          │              │   service    │           │
       │          │              │ (ONNX/Scale) │           │
       └────┬─────┘              └──────────────┘           │
            │                            ▲                  │
            │ (Consumes Task)            │ (Batch Embed)    │
            ▼                            │                  │
       ┌────────────────────────┐        │                  │
       │     Taskiq Worker      ├────────┘                  │
       │ (File Preparator /     │                           │
       │  Chunking / Indexing)  │                           │
       └────┬───────────────────┘                           │
            │                                               │
 (extract)  │                                               │
   text)    ▼                                               │
 ┌──────────────────────┐                       ┌───────────▼────────────┐
 │                      │                       │ PostgreSQL + pgvector  │
 │  extraction-service  │                       │(Metadata, Chunks, DB)  │
 └──────────────────────┘                       └────────────────────────┘
```

### 2.1. `core-service` (Main API & Taskiq Worker)
Hosts the core domain logic, user-facing endpoints, and background document indexing within a single modular codebase:
* **Core API (FastAPI)**:
  * User authentication, authorization, and profile management.
  * Case (*Sprawy*) management and document metadata handling (filenames, upload status, permissions).
  * Storage orchestration: uploading and retrieving raw documents to/from Google Cloud Storage / S3 / local storage.
  * Fast synchronous search execution: requests single query embeddings from `embeddings-service` and performs vector similarity search against PostgreSQL (`pgvector`).
  * Dispatches asynchronous file processing tasks to the broker using **Taskiq**.
* **File Preparator (Taskiq Worker)**:
  * Consumes document preparation jobs from the Taskiq broker.
  * Coordinates document processing pipeline: sends file to `extraction-service`, chunks structured text, requests batch embeddings from `embeddings-service`, and persists vector embeddings into PostgreSQL.
  * Updates document processing status in PostgreSQL directly without inter-service RPC overhead.

### 2.2. `embeddings-service`
* **Responsibilities**:
  * Dedicated, stateless microservice for generating dense vector embeddings for text chunks and search queries using **ONNX Runtime** / transformer models.
* **Characteristics**:
  * **Isolated Compute**: Heavy tensor computation and embedding model memory footprints are completely decoupled from the main API, preventing thread blockage and memory spikes.
  * **Independent Scaling**: Can be scaled independently (e.g., on GPU or high-CPU compute instances) based on search traffic and document ingestion volume.
  * Exposes simple, low-latency endpoints for single-text and batch-text embeddings.

### 2.3. `extraction-service`
* **Responsibilities**:
  * Document layout analysis, and text extraction (PDFs) into structured JSON format, using Docling.
* **Characteristics**:
  * Completely stateless service.
  * **Scale-to-0 on GCP**: Instances spin up on incoming HTTP processing requests and scale down to 0 during idle periods, significantly reducing RAM and compute costs.
  * Runs as a dedicated container in On-Premise deployments.

---

## 3. Key Architectural Decisions & Patterns

### 3.1. Monolith for Core Business (`core-service`)
* **Simplicity & Velocity**: Simple monolith, but with clean architecture, possibly to modularize, if team growth.
* **Architecture**: Use cases and domain entities for documents, cases, with separate layers for framework, and infrastructure (e.g. db connection).

### 3.2. Asynchronous Job Processing with Taskiq
NOT YET IMPLEMENTED
* **Modern Async-First Design**: Native integration with FastAPI and asynchronous Python runtimes.
* **Broker Agnostic**: Supports Redis, RabbitMQ, or other brokers with minimal configuration changes.
* **Resilience**: Provides built-in retry mechanisms, failure handling, and transparent task parameter serialization.

### 3.3. Compute Decoupling (Embeddings & Extraction)
* **Resource Isolation**: CPU/GPU-intensive tasks (OCR extraction and vector embedding generation) reside in specialized microservices.
* **Guaranteed Latency**: The primary web API stays lightweight, responsive, and fast under heavy indexing workloads.

---

## 4. More about core-service architecture

Each microservice in the repository follows **Clean Architecture** principles, enforcing strict inward-pointing dependency rules.

```
                    ┌────────────────────────┐
                    │       Framework        │ (FastAPI, Taskiq Workers)
                    │  ┌──────────────────┐  │
                    │  │  Infrastructure  │  │ (DB Repos, HTTP Clients, Storage)
                    │  │  ┌────────────┐  │  │
                    │  │  │Application │  │  │ (Use Cases, DTOs, Ports)
                    │  │  │  ┌──────┐  │  │  │
                    │  │  │  │Domain│  │  │  │ (Entities, Value Objects)
                    │  │  │  └──────┘  │  │  │
                    │  │  └────────────┘  │  │
                    │  └──────────────────┘  │
                    └────────────────────────┘
```

### 4.1. Layers

#### `app/domain`
The innermost core of the service containing **Enterprise Business Rules**. It has zero dependencies on outer layers or external frameworks.
- **Entities**: Business models encapsulating identity and business state (e.g., `User`, `Case`, `Document`, `Chunk`).
- **Value Objects**: Immutable data structures representing concepts without identity.
- **Services**: Pure business algorithms and domain rules.
- **Exceptions**: Domain-specific error definitions.

#### `app/application` (or `src/app`)
Contains **Application Business Rules** and use case orchestrations.
- **Use Cases**: Individual business workflows (e.g., `RegisterUser`, `ProcessUploadedDocument`, `SearchDocuments`).
- **DTOs**: Data Transfer Objects defining input/output contracts.
- **Ports & Interfaces**: Abstract contracts for repositories, vector embedders, and external APIs implemented by the Infrastructure layer.

#### `app/infrastructure`
Acts as adapters for external systems and technical tools, implementing ports defined in domain/application.
- **Relational DB**: SQLAlchemy repositories, connection pools, and database schemas.
- **External Clients**: HTTP/gRPC clients communicating with external services (`embeddings-service`, `extraction-service`).
- **Object Storage**: S3 / Google Cloud Storage / local filesystem adapters.

#### `app/framework`
The outermost delivery mechanism and dependency injection root.
- **API**: FastAPI routes, middleware, and request/response serialization.
- **Workers**: Taskiq worker definitions and task registrations.
- **Dependencies**: Dependency injection wiring combining infrastructure implementations with application use cases.

#### `app/shared`
Cross-cutting concerns across layers (configuration settings, logging utilities, common base exceptions).

---

## 5. Import Rules

To preserve architectural boundaries:
- **`domain`** must NOT import from `application`, `infrastructure`, or `framework`.
- **`application`** can import from `domain`, but must NOT import from `infrastructure` or `framework`.
- **`infrastructure`** can import from `application` (interfaces, DTOs) and `domain`. It must NOT import from `framework`.
- **`framework`** is the assembly root and can import from `application`, `domain`, and `infrastructure` to wire dependencies.
- **`shared`** can be imported by any layer, but should not depend on domain or infrastructure specifics.
