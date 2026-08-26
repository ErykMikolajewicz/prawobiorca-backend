# Old Application Architecture

## 1. Introduction and System Overview

This document describes the previous architecture of the **Prawobiorca** platform. It serves as a historical reference to understand how the system evolved to its current state.

Previously, the system consisted of only two main components:
- **core-service (FastAPI App)**
- **text-transformator**

There was no message broker (like Redis or RabbitMQ) and no background task workers (like Taskiq) in use.

---

## 2. System Architecture & Components

The old architecture was heavily centralized around the main API, with basic offloading of text and PDF operations to the `embedding-service`.

```text
                            [Client / Vue]
                                  │
                                  │ (HTTP REST)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │             core-service (FastAPI App)                 │
       │        (Auth, Cases, Files, Search Engine)             │
       │                                                        │
       │  [ Background Threads for Heavy Tasks ]                │
       └────┬─────────────────────────────┬─────────────────┬───┘
            │                             │                 │
            │ (HTTP POST                  │                 │ (Relational DB
            │  for OCR/Embeddings)        │                 │  & Vector DB)
            ▼                             │                 │
 ┌──────────────────────┐                 │             ┌───▼────────────────────┐
 │  text-transformator  │                 │             │ PostgreSQL + pgvector  │
 │(Docling, ONNX Models)│                 └────────────►│(Metadata, Chunks, DB)  │
 └──────────────────────┘                               └────────────────────────┘
```

### 2.1. `core-service` (Main API)
The core service was responsible for almost everything:
* User authentication and authorization.
* Case management and file uploading.
* Storage orchestration (GCS/S3/local).
* **Heavy Task Execution**: Instead of using an asynchronous task queue (like Taskiq), long-running tasks such as document indexing, chunking, and preparation were simply dispatched to **separate threads** running within the FastAPI application process.
* Direct synchronous communication with PostgreSQL and the `embedding-service`.

### 2.2. `embedding-service`
This service was a combined monolith for AI and extraction tasks.
* **Responsibilities**:
  * Parsing PDF documents and performing layout extraction using Docling.
  * Generating embeddings and counting tokens using ONNX models.
* It handled both CPU-heavy text extraction and memory-heavy tensor computations in a single process.

---

## 3. Key Limitations of the Old Architecture

The decision to migrate to the new architecture was driven by several limitations in this older model:

1. **Thread Starvation & Memory Bloat**: Running heavy document processing tasks on background threads within the main `core-service` could block the event loop, consume excessive memory, and degrade the performance of user-facing HTTP endpoints.
2. **Lack of Resilience**: Without a message broker, if the `core-service` crashed or restarted, all in-progress background threads for document processing were lost without any retry mechanism.
3. **Monolithic AI Service**: The `embedding-service` handled both PDF extraction and embedding generation. This prevented independent scaling. For example, PDF extraction can scale-to-zero when idle, while embedding generation requires models loaded in memory for fast search queries.
4. **Poor Resource Utilization**: Mixing heavy ML models with standard OCR extraction meant compute resources could not be optimized separately (e.g., using GPUs for embeddings and high-CPU for Docling).
