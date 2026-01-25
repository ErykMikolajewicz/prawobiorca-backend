# External Services

---

## Relational Database

### Technology Choice and Justification
PostgreSQL was chosen as the relational database. The decision was driven by the need for a scalable and durable solution for storing information. Postgres stands out with its rich set of data types (e.g., JSON support), high performance, and broad support within the Python ecosystem — efficient drivers are available, implemented in Cython/C, including asynchronous versions.

### Scope of Use
Postgres serves as the default data storage location in the application. Other forms of storage are used only when required for performance reasons or due to the absence of certain functionality in the relational database.

### Abstraction Layer and Integration
The application uses the SQLAlchemy ORM for database communication, which provides a sufficient abstraction layer. There are no additional layers on top of SQLAlchemy, as replacing this tool is considered unlikely. Additionally, the Unit of Work pattern is used for transaction management.

### Capabilities and Future Plans
Replacing Postgres is considered unlikely but possible. The potentially biggest challenge is the high cost of database maintenance and management. Scalability issues may also arise. In such cases, migration to a commercially supported database (e.g., EnterpriseDB) or the use of managed solutions offered by cloud providers is possible.

---

## Key–Value Database

### Technology Choice and Justification
Redis was chosen as the key–value database. This type of database is necessary due to the need to share data (e.g., access tokens) between instances of the web application, and storing them in a relational database would be too slow.

### Scope of Use
Redis is primarily used to store tokens and other small, frequently used data, where reading from the relational database would be unnecessarily slow. It also simplifies managing data with a limited lifespan.

### Abstraction Layer and Integration
The project uses an abstraction layer referred to as the “key–value database.” However, in type hints, the Redis client is used directly. Replacing Redis with another technology is considered unlikely, so the lack of a full additional abstraction layer is a deliberate choice. Adding such a layer would increase complexity without providing benefits in terms of easier maintenance or future flexibility.

### Capabilities and Future Plans
Due to the lack of technologies offering functionality comparable to Redis, there are no plans to replace it. The solution is close to being open source — although there are some licensing controversies — it is not simply MIT or Apache. The benefits of being independent of the chosen technology were assessed as low.

---

## Cloud Storage

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
