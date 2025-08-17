# Business Logic

The application is divided into two main parts.

## Public Section

A search engine for court judgments with basic functions, offered to users for free, without requiring login. However, limits may apply, e.g., the number of requests per hour.

### Data Source
Court judgments are, in principle, public. Therefore, access is planned either via public APIs (e.g., [SAOS](https://www.saos.org.pl/)), if available, or through formal requests to public institutions.

### Basic Features
Initially, it will be satisfactory to provide:
- text search, including word inflections,
- various filters, such as:
  - type of court (e.g., criminal, administrative),
  - court level (e.g., appeals, district court judgments),
  - date of judgment,
  - case reference number.

### Additional Features
Further options to consider include search by:
- judge data – this seems possible and GDPR-compliant (judges are public figures, and their names are public by default), but requires legal consultation,
- thematic keywords – requires extended domain knowledge,
- legal basis – potentially difficult to implement,
- parameters specific to a given type of court (e.g., the challenged authority in administrative courts),
- parts of the judgment (e.g., only judgments with reasoning).

---

## Commercial Section

A paid part of the application, requiring login – initially subscription-based (monthly), with a possible future transition to a pay-per-use model.

### AI Search Engine
An extension of search capabilities using more advanced methods than word matching, e.g., through embeddings.  
Additionally: the ability to search within the user’s own documents.  

> **Note!** Introducing such features, even free of charge, requires legal consultation – in order not to fall into the category of providing legal services, which only lawyers are authorized to do.

### Anonymization Tool
The goal is to develop a tool for anonymizing documents. Initially, an effectiveness rate of around 90% will be sufficient.  
Both classical methods and AI can be used, with confidentiality issues taken into account.  

The ideal solution would work client-side, in the browser.  
No legal consultations are required (apart from trust, confidentiality, and personal data processing concerns).

### Extractor
A tool for summarizing legal documents and extracting information from them.  

> **Note!** Introducing such features, even free of charge, requires legal consultation – in order not to fall into the category of providing legal services, which only lawyers are authorized to do.
