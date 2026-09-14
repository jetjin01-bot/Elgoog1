# Elgoog

Elgoog ingests heterogeneous business files, resolves canonical entities and logical documents, preserves provenance and conflicts, and exposes the resulting knowledge model through an interactive Streamlit interface.

The system combines a deterministic core with governed AI-assisted schema discovery and generalized extraction. AI is used to propose structure and extract observations, while canonical resolution remains evidence-based and conservative.

---

## 1. Project Overview

Companies rarely store operational knowledge in one clean system.

The same customer, project, person, transaction or document may appear across:

- PDFs
- emails
- spreadsheets
- folders
- filenames
- invoices
- quotations
- purchase orders
- delivery notes
- correspondence
- drawings
- specifications
- reports
- technical documents

The challenge is therefore not simply to extract text, but to determine:

- what real entities exist
- when two observations refer to the same entity
- how documents relate to projects and companies
- which evidence supports each relationship
- what to do when evidence disagrees
- when a system should refuse to resolve something automatically

Elgoog builds a structured, queryable and explainable business knowledge model over fragmented source files.

---

## 2. Problem Framing

The system is designed around several principles:

> Folder structure is evidence, not truth.

> Content can override filenames and folder placement when stronger evidence exists.

> Canonical entities use stable internal IDs.

> Observed aliases are preserved rather than overwritten.

> Observations remain separate from canonical entities.

> Evidence from different extraction methods is preserved independently.

> Ambiguous matches are surfaced for review rather than aggressively merged.

> Relationships retain confidence and provenance.

> Conflicting evidence is preserved instead of silently selecting a winner.

> A wrong merge is more dangerous than an unresolved record.

The objective is not to create a searchable collection of extracted text.

The objective is to build a model precise enough that downstream software can reason over companies, projects, people, documents and relationships without hiding uncertainty.

---

## 3. What I Built

The pipeline currently supports:

### Source Ingestion

- recursive file discovery
- file metadata capture
- SHA-256 hashing
- folder context capture
- source file persistence
- ingestion status tracking

### Document Resolution

- filename-based document identity detection
- content-based document identity verification
- logical document creation
- source-file-to-logical-document linking
- filename/content conflict detection
- support for multiple physical files representing one logical document

### Entity Extraction

- company mentions
- project mentions
- person mentions from email metadata
- aliases from labelled PDF fields
- schema-constrained AI entity extraction
- provenance-aware observations

### Canonical Entity Resolution

- canonical companies
- canonical projects
- canonical people
- stable internal IDs
- alias preservation
- confidence tracking
- candidate match review
- deterministic enrichment using supporting evidence
- unresolved states when evidence is insufficient

### Schema Discovery and Governance

- sample-based schema discovery for unfamiliar files
- proposed document types
- proposed entity types
- suggested attributes
- proposed relationship types
- ambiguity detection
- human review before schema activation
- separation between proposed and active schemas

### Generalized Processing

- schema-constrained AI extraction
- provenance-aware entity mentions
- deterministic project enrichment from folder context
- deterministic person enrichment from email evidence
- generalized logical document creation
- reuse of existing canonical resolvers
- unresolved observations preserved when evidence is insufficient

### Relationship Construction

- Company → Project
- Document → Project
- Document → Company
- Document → Person
- Document → Document

### Provenance and Data Quality

- extraction issues
- unresolved references
- filename/content conflicts
- evidence records
- source file traceability
- extraction method tracking
- human review queues

### User Interface

- Overview
- Entity Explorer
- Graph Explorer
- Resolution Review
- Schema Review
- Generalized Processing
- Data Quality
- Relationships
- Ask the Knowledge Model

---

## 4. Architecture

The system uses a deterministic-first architecture.

A governed generalized layer extends the deterministic baseline when unfamiliar document structures or entity types are encountered.

```text
Source Files
    ↓
File Scanner
    ↓
Content Extraction
    ↓
Document Identification
    ↓
Logical Document Resolution
    ↓
Deterministic Entity Mention Extraction
    ↓
Canonical Entity Resolution
    ↓
Optional Generalized Processing
    ↓
Schema Discovery
    ↓
Human Schema Review
    ↓
Approved Active Schema
    ↓
AI Entity / Document Extraction
    ↓
Deterministic Evidence Enrichment
    ↓
Canonical Entity Resolution
    ↓
Relationship Construction
    ↓
Evidence / Conflict Persistence
    ↓
SQLite Knowledge Model
    ↓
Streamlit Interface
```

The SQLite database is treated as a derived, rebuildable knowledge model over the source corpus.

The original files remain the underlying evidence layer.

---

## 5. Technology Stack

### Core

- Python
- SQLite
- Pandas
- PyYAML

### Document Processing

- PyMuPDF

### Entity Resolution

- deterministic normalization
- alias matching
- RapidFuzz-assisted candidate scoring
- identifier-based canonical resolution

### Generalized Extraction

- OpenAI API
- schema discovery
- schema-constrained entity extraction
- ambiguity identification
- python-dotenv for local API configuration

### Graph Exploration

- NetworkX
- PyVis

### Interface

- Streamlit

The canonical resolution layer does not depend on an LLM making identity decisions.

AI is used for schema discovery and semantic extraction, while deterministic evidence and existing resolution policies control whether an observation is linked to a canonical entity.

This keeps identity resolution reproducible, reviewable and easier to explain.

---

## 6. Data Model

The core business entities are:

### Company

Represents a canonical organisation.

### Project

Represents a canonical job or project.

### Person

Represents a canonical individual, generally resolved using reliable identifiers such as email evidence.

### Document

Represents a logical business document rather than a physical file.

Supported document categories include:

- Invoice
- Quotation
- Purchase Order
- Delivery Note
- Drawing
- Specification
- Correspondence
- Contract
- Internal Report
- Technical Datasheet
- Other approved document types

### Source File

A source file is the physical artefact found in the original corpus.

A logical document may be supported by one or more source files.

This distinction prevents duplicated, revised or renamed physical files from automatically being treated as separate business documents.

---

## 7. Source File vs Logical Document

The system deliberately separates physical source files from logical business documents.

Source files remain independently traceable, while the knowledge model can resolve multiple representations into one logical document where the evidence supports that conclusion.

This distinction separates physical storage from business identity.

The generalized processing layer can also create logical documents for document types that were not supported by the original deterministic parser.

All logical documents remain linked back to their originating source files.

---

## 8. Document Resolution Strategy

Document identity is determined using multiple signals.

### Filename Evidence

Structured filenames can provide an initial document identity signal.

### Content Evidence

Labelled fields and identifiers found inside document content are treated as stronger evidence when available.

### Conflict Handling

When filename evidence and document content disagree, the system does not silently discard either observation.

The stronger evidence can be used for logical document resolution while the disagreement is preserved as a conflict for review and provenance.

---

## 9. Entity Resolution Strategy

Entity resolution is intentionally conservative.

A wrong merge is more dangerous than an unresolved alias because an incorrect merge can silently corrupt downstream relationships.

The resolution process can use:

1. strong identifiers
2. normalized exact matches
3. known aliases
4. candidate scoring
5. folder evidence
6. email evidence
7. score margin against alternative candidates
8. human review when evidence is insufficient

An observation is not automatically treated as a canonical entity.

It must either contain a sufficiently reliable identifier or acquire supporting evidence through deterministic enrichment.

Different extraction methods are preserved independently.

Two observations with the same text value are not automatically collapsed if they came from different evidence sources.

They may later resolve to the same canonical entity while retaining their individual provenance.

---

## 10. Generalized Processing

The deterministic pipeline is strongest when the structure of the source documents is already understood.

The generalized processing layer extends the system to unfamiliar files without allowing AI to directly modify the canonical knowledge model.

The process is:

```text
Approved Schema
    ↓
AI Extraction
    ↓
Observed Entity Mentions
    ↓
Deterministic Evidence Enrichment
    ↓
Canonical Resolution
    ↓
Resolved / Unresolved State
```

AI extraction produces observations rather than canonical entities.

Deterministic evidence can then enrich those observations with reliable identifiers or contextual support.

Existing canonical resolvers determine whether the observation can be safely linked to the knowledge model.

If the available evidence is insufficient, the observation remains unresolved.

This separation is intentional:

- AI identifies semantic content
- deterministic evidence enriches observations
- canonical resolvers decide identity
- uncertainty remains visible

---

## 11. Schema Discovery and Review

The system can inspect a sample of unfamiliar source files and propose extensions to the active schema.

A proposal may include:

- new document types
- new entity types
- suggested attributes
- new relationship types
- detected ambiguities

AI-generated proposals are stored separately from the active schema.

They do not automatically change the production model.

The Schema Review interface allows a reviewer to inspect proposals and decide whether to:

- approve them
- reject them
- treat a proposed concept as an attribute instead of an entity
- approve or reject proposed relationship types

Only explicitly approved changes are applied to the active schema.

This makes schema evolution a governed process rather than allowing an AI model to silently redefine the knowledge model.

---

## 12. Human-in-the-Loop Resolution

The Resolution Review interface exposes ambiguous matches rather than hiding them.

Review information can include:

- observed alias
- candidate entity
- match score
- alternative candidate score
- score margin
- supporting evidence
- decision reason
- occurrence count
- source files
- known aliases

The system treats uncertainty as an explicit state rather than forcing every observation into a canonical entity.

Human review is also used during schema evolution.

Entity resolution review determines whether an observation should map to a canonical entity.

Schema review determines whether a document type, entity type or relationship should exist in the model at all.

Keeping these review stages separate prevents structural schema decisions from being confused with individual resolution decisions.

---

## 13. Relationship Model

The relationship vocabulary includes:

- HAS_PROJECT
- RELATES_TO_PROJECT
- RELATES_TO_COMPANY
- BILL_TO
- CUSTOMER
- SUPPLIER
- SHIP_TO
- ISSUED_BY
- SENDER
- RECIPIENT
- CC
- REFERENCES

Relationships are stored separately from entities.

They retain relationship type, confidence and status information.

This allows the system to model business structure without embedding every connection directly inside entity records.

---

## 14. Provenance

The system is designed so that resolved information can be traced back to its supporting evidence.

The model retains:

- source files
- entity mentions
- aliases
- extraction methods
- logical documents
- relationships
- conflicts
- confidence values

This allows the system to explain:

- why an entity exists
- which source produced an alias
- why an observation was resolved
- which document supports a relationship
- which extraction method produced an observation

Provenance is treated as part of the knowledge model rather than as an afterthought.

Generalized processing also distinguishes between deterministic observations and AI-derived observations.

Observations are not collapsed simply because their normalized values match.

Different evidence sources may independently support the same canonical entity.

---

## 15. Conflict Handling

Conflicting evidence is preserved.

Current conflict categories include:

### Extraction Issues

Files that cannot be read successfully or contain no extractable text.

### Unresolved Document References

Documents may contain explicit references to other documents that cannot be resolved into the logical document model.

### Filename / Content Conflicts

The identity suggested by the filename may disagree with the identity found inside the document content.

These issues are stored in a persistent conflict register.

This makes data-quality problems queryable and reproducible.

---

## 16. Data Quality

The system records processing issues rather than only printing them during execution.

Tracked categories include:

- extraction issues
- unresolved references
- filename/content conflicts
- unresolved entity observations

Corrupt files, empty files and files without extractable text are treated as data-quality conditions rather than as reasons for the entire pipeline to fail.

This allows the system to complete processing while keeping failures visible for later review.

---

## 17. Graph Explorer

The Graph Explorer provides focused views over the resolved knowledge model.

Available views include:

### Business Structure

Shows the connection between companies, projects and representative documents.

### Documents

Shows relationships involving logical documents.

### Communications

Shows correspondence and the people connected to it.

### Direct Relationships

Provides a focused one-hop inspection around a selected entity.

The graph intentionally limits node counts to avoid producing an unreadable global network.

---

## 18. Ask the Knowledge Model

The application includes a deterministic query interface over the resolved SQLite knowledge model.

It can search across:

- companies
- projects
- people
- documents

The interface can expose:

- entity summaries
- related projects
- related documents
- people involved
- references
- relationships
- conflicts
- provenance

The query interface operates over the structured model directly.

It does not re-read the source corpus for each query and does not rely on an LLM to perform entity resolution at query time.

---

## 19. Generalized Processing Interface

The Generalized Processing screen provides a focused view over the generalized extraction layer.

It displays:

- extracted mentions
- matched records
- unresolved records
- results by entity type
- extracted identifiers
- source files
- newly created logical documents

The page is designed to make the processing path understandable without exposing unnecessary implementation detail.

The processing stages are:

```text
Extract
    ↓
Enrich
    ↓
Match
    ↓
Store
```

Records without sufficient evidence remain unresolved and available for review.

---

## 20. Pipeline Order

The rebuild process currently follows this sequence:

1. Initialise or reset the derived database
2. Scan source files
3. Build initial logical documents
4. Verify document identities
5. Extract folder-based company and project mentions
6. Resolve canonical companies and projects
7. Extract people from email metadata
8. Resolve canonical people
9. Extract and resolve PDF company aliases
10. Optionally run generalized processing
11. Build relationships
12. Run final data-quality checks

The generalized processing stage follows:

```text
Selected Source Files
    ↓
Schema-Constrained AI Extraction
    ↓
Observed Mentions
    ↓
Deterministic Evidence Enrichment
    ↓
Canonical Resolution
    ↓
Logical Document Linking
```

Generalized processing is optional.

The deterministic baseline can rebuild the knowledge model without making OpenAI API calls.

This keeps the baseline independently reproducible and avoids unnecessary model usage.

---

## 21. Key Design Decisions

### Deterministic First

Canonical identity decisions remain deterministic wherever reliable identifiers or structured evidence are available.

AI extends extraction coverage but does not replace the canonical resolution layer.

This improves:

- reproducibility
- explainability
- debugging
- testability

### Do Not Trust Folder Structure Blindly

Folders contribute evidence but do not determine truth.

### Separate Observations from Canonical Entities

Observed values remain available as mentions and aliases.

Canonical entities are created or linked only when resolution rules support that decision.

### Separate AI Observations from Canonical Entities

AI extraction creates observations rather than canonical business objects.

This prevents the extraction model from making uncontrolled identity decisions.

### Preserve Ambiguity

Low-confidence or insufficiently supported observations remain unresolved.

### Preserve Conflicts

Conflicting evidence is stored rather than overwritten.

### Separate Source Files from Logical Documents

Physical storage and business identity are different concepts.

### Govern Schema Changes

AI-generated schema proposals remain isolated until reviewed and approved.

The active schema changes through explicit governance rather than automatic model output.

### Rich Model First

The knowledge model retains relationships, provenance, confidence and unresolved states even when downstream applications may eventually require simpler views.

---

## 22. Running the Project

Create and activate a Python environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

If generalized AI processing is required, create a local `.env` file containing:

```text
OPENAI_API_KEY=your_key_here
```

The `.env` file should not be committed to Git.

### Run the Pipeline

```bash
python pipeline.py
```

By default, the deterministic pipeline can rebuild the derived knowledge model without generalized AI processing.

Generalized source files can be supplied through the `generalized_source_ids` argument when required.

### Start the Streamlit Interface

```bash
streamlit run app.py
```

---

## 23. Limitations

The current implementation is intentionally scoped.

### OCR

Image-only and scanned PDFs without a usable text layer are currently surfaced as extraction issues.

A production system would add OCR or multimodal document extraction.

### Entity Resolution

Resolution policies are currently strongest for companies, projects and people with reliable identifiers.

Additional entity classes would require dedicated resolution policies.

### Relationship Validation

A detected reference is treated as observed evidence.

The system does not yet fully determine whether all referenced documents form a semantically valid business transaction chain.

Additional validation using dates, amounts and domain rules would strengthen this layer.

### Manual Review Workflow

The interface supports schema approval decisions and exposes entity-resolution candidates.

A production implementation would require a complete operational review workflow with persistent reviewer decisions and audit history.

### Schema Evolution

The system supports AI-assisted schema proposals and human approval.

Schema merging remains relatively lightweight.

A production implementation would require:

- formal schema versioning
- migration management
- backward compatibility rules
- stronger validation before activation

### Generalized AI Processing

The generalized layer currently runs on explicitly selected files rather than automatically across the entire corpus.

A production implementation would require:

- extraction caching
- change detection
- batching
- retry handling
- API cost controls
- incremental processing

### Incremental Updates

The current demo favours reproducible full rebuilds.

A production system would require efficient incremental ingestion and re-resolution.

---

## 24. Future Improvements

Potential next steps include:

### OCR and Multimodal Extraction

Add OCR or document vision support for scanned PDFs, handwriting and image-based files.

### Review Write-Back

Support persistent reviewer decisions including:

- approval
- rejection
- reassignment
- merge
- split
- audit history

### Stronger Relationship Validation

Use dates, amounts and domain rules to distinguish observed references from validated business relationships.

### Candidate Blocking

Reduce the search space before approximate entity matching for larger datasets.

### Incremental Graph Recalculation

Recompute only affected entities and relationships when new evidence arrives.

### AI Extraction Caching

Avoid repeated model calls for unchanged source files using file fingerprints and processing status.

### Schema Versioning

Track active schema versions and migrations so structural changes remain reproducible.

### Regression Testing

Maintain fixed test cases and expected resolution outcomes to identify behavioural changes after updates to parsing or resolution logic.

### Generalized Relationship Extraction

Extend schema-constrained extraction beyond entities and documents to relationship candidates while retaining deterministic validation before persistence.

### Natural-Language Query Layer

An LLM could be added as an optional interpretation layer over the already-resolved structured model.

It would not be responsible for uncontrolled entity resolution or database writes.

---

## 25. Final Note

The main goal of Elgoog is not maximum extraction coverage.

It is to demonstrate how fragmented enterprise data can be transformed into a structured, evidence-backed and reviewable knowledge model without hiding uncertainty.

The operating principle is:

> Extract broadly.

> Resolve conservatively.

> Preserve the evidence.

When the structure is unfamiliar, AI can help discover and extract it, but the evidence still determines what becomes part of the canonical model.