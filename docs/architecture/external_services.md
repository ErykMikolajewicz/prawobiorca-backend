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

## Cloud Storage
Currently not used, replaced by just local file hierarchy.

### Technology Choice and Justification
Google Cloud Storage was chosen as the file storage solution. This decision was made for performance reasons — storing files in the relational database would likely negatively impact the overall database performance, and serving them via the web application would be a heavy load on the network. To maintain consistency in the technology stack, Google Cloud Storage was selected because the Google Cloud platform is also used in other areas of the project.

### Scope of Use
Google Cloud Storage is used to store both public and private files:

- **Public files** (e.g., laws, court rulings) are accessible via a standard URL.
- **Private user files** are available only through signed URLs with a limited validity period.

Files are written via the web application, but their reading will often be done directly from the URL by the frontend client.

### Abstraction Layer and Integration
Functions using Google Cloud Storage are designed in an abstract way to allow for the potential use of another platform in the future. The default Google Cloud Storage client is synchronous, so an asynchronous wrapper has been prepared in the project to ensure proper integration with the rest of the application, which uses asynchronous calls.

### Capabilities and Future Plans
An alternative considered in the design phase was storing files in a file system and serving them via Nginx, but this was deemed less scalable and more difficult for access management. The decision was made to keep an abstraction layer that would allow switching to another cloud environment in case, for example, of unfavorable data storage conditions on the Google Cloud platform.
