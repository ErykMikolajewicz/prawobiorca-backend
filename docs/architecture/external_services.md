# External Services

---

## Relational Database

### Technology Choice and Justification
PostgreSQL was chosen as the relational database. The decision was driven by the need for a scalable and durable solution for storing information. Postgres stands out with its rich set of data types (e.g., JSON support), high performance, and broad support within the Python ecosystem — efficient drivers are available, implemented in Cython/C, including asynchronous versions.

### Scope of Use
Postgres serves as the default data storage location in the application. Other forms of storage are used only when required for performance reasons or due to the absence of certain functionality in the relational database.

### Abstraction Layer and Integration
The application uses the SQLAlchemy ORM for database communication. There is a repository pattern used to gather all data access code in one place and decouple app layer for orm related concerns.

### Capabilities and Plans
Replacing Postgres is considered unlikely but possible.

---

## TextTransformator

Api with an option to embed document and split PDF files for elements.

---

## LLM Service

### Technology Choice and Justification
**OpenVINO Model Server (OVMS)** serves the conversational LLM directly — no custom application code — using a pre-quantized int8 OpenVINO IR build of Gemma-4 E4B (`OpenVINO/gemma-4-E4B-it-int8-ov` on Hugging Face). An earlier iteration wrapped **OpenVINO GenAI** in a custom FastAPI app; OVMS replaced it once Gemma-4 VLM support landed there (OVMS 2026.3), since it removes that app entirely in favor of a maintained server with an OpenAI-compatible API, at the cost of continuous batching, which isn't available for this model yet (no PagedAttention support — see [openvinotoolkit/model_server#4178](https://github.com/openvinotoolkit/model_server/issues/4178)). This keeps the service consistent with the rest of the stack's preference for Intel-hardware-friendly, CPU-first inference (as in `embedding-service`'s ONNX Runtime usage).

### Scope of Use
Standalone service exposing an OpenAI-compatible `/v3/chat/completions` endpoint (model name `gemma-4-e4b-it`). It has no consumers yet — `core-service` integration (a chat feature usable by application users) is planned future work, not part of this iteration.

### Abstraction Layer and Integration
OVMS pulls the model repository from Hugging Face on first start (`--source_model`) into a mounted persistent volume, so restarts reuse the cached model instead of re-downloading it. No custom image build or model-baking step is needed.

### Capabilities and Future Plans
Planned follow-ups: wiring a client into `core-service` (port/adapter/use case, mirroring the existing `TextsEmbedder`/`RegulationSplitter` pattern), streaming responses, and revisiting continuous batching once OVMS/OpenVINO GenAI add PagedAttention support for Gemma-4.

---

## Object Storage

### Technology Choice and Justification
Files are kept in an S3-compatible object storage rather than the relational database — storing files in Postgres would hurt database performance, and serving them through the web application would put a heavy load on `core-service`. The application talks to storage exclusively through the S3 protocol, which lets the same client code run against different backends depending on the deployment mode: **RustFS** on-premise (run as a container via Podman) and **Google Cloud Storage** in the cloud, accessed through its S3 interoperability API. No environment-specific storage code is needed.

### Scope of Use
Object storage holds both public and private files:

- **Public files** (e.g., laws, court rulings) are accessible via a presigned/standard URL.
- **Private user files** are available only through presigned URLs with a limited validity period.

Files never transit through `core-service`. The browser writes a file directly to storage using a presigned POST target (URL + form fields) that `core-service` generates and hands back after registering the file's metadata; it then calls back a confirmation endpoint so `core-service` can schedule background processing. Reading works the same way in reverse: `core-service` returns a presigned GET URL, and the browser fetches the file directly from storage. The Taskiq worker is the one component that reads raw file bytes itself, for text extraction/chunking/embedding.

### Abstraction Layer and Integration
The storage port is a small `Protocol` in the application layer, backed by a single S3-protocol adapter (`aiobotocore`) in infrastructure — the same adapter class is used unchanged for both RustFS and GCS. Two clients are configured: the main client, used for internal calls, and a "presign" client pointed at a public endpoint URL (`OBJECT_STORAGE_PUBLIC_ENDPOINT_URL`), used only to generate presigned URLs so they stay reachable from the browser even when the internal endpoint (`OBJECT_STORAGE_ENDPOINT_URL`) is not (e.g. an internal cluster hostname in local/on-premise deployments).

### Capabilities and Future Plans
An alternative considered in the design phase was storing files in a file system and serving them via Nginx, but this was deemed less scalable and more difficult for access management. Because integration goes through the S3 protocol rather than a cloud-specific SDK, switching to another S3-compatible backend in the future would not require any application code changes.
