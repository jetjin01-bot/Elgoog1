from SRC.data_quality import audit_extractions

from SRC.database import (
    DATABASE_PATH,
    initialize_database,
)

from SRC.Ingestion.Scanner import scan_dataset
from SRC.Ingestion.documents.document_builder import build_documents
from SRC.Ingestion.documents.pdf_document_resolver import (
    build_verified_pdf_documents,
)
from SRC.Ingestion.extraction.batch_verifier import (
    verify_filename_inferred_pdfs,
)

from SRC.entities.mention_extractor import (
    extract_folder_mentions,
)
from SRC.entities.email_person_extractor import (
    extract_email_person_mentions,
)
from SRC.entities.company_mention_extractor import (
    extract_pdf_company_mentions,
)

from SRC.entities.company_resolver import (
    resolve_companies,
)
from SRC.entities.project_resolver import (
    resolve_projects,
)
from SRC.entities.person_resolver import (
    resolve_people,
)
from SRC.entities.company_resolution_engine import (
    resolve_company_mentions,
)

from SRC.entities.generic_entity_pipeline import (
    process_specific_source_files,
)
from SRC.entities.mention_enricher import (
    enrich_project_mentions,
    enrich_person_mentions,
)
from SRC.entities.document_mention_linker import (
    link_ai_document_mentions,
)

from SRC.relationships.relationship_builder import (
    build_company_project_relationships,
    build_document_project_relationships,
    build_document_company_relationships,
    build_email_documents_and_relationships,
    build_document_reference_relationships,
)


def run_generalized_processing(
    source_file_ids: list[int],
):
    """
    Run generalized AI extraction only for explicitly
    selected source files.

    AI extraction creates observed mentions.
    Deterministic enrichment and resolution are then used
    to link those observations into the canonical model.
    """

    if not source_file_ids:
        print(
            "\nNo source files selected for generalized processing."
        )
        return

    print(
        "\nRunning generalized processing..."
    )

    results = process_specific_source_files(
        source_file_ids
    )

    processed = sum(
        1
        for result in results
        if result.get("status") == "processed"
    )

    skipped = sum(
        1
        for result in results
        if result.get("status") == "skipped"
    )

    errors = sum(
        1
        for result in results
        if result.get("status") == "error"
    )

    print(
        f"Processed: {processed}"
    )
    print(
        f"Skipped:   {skipped}"
    )
    print(
        f"Errors:    {errors}"
    )

    # --------------------------------------------------------
    # Add deterministic supporting evidence
    # --------------------------------------------------------

    print(
        "\nEnriching generalized mentions..."
    )

    enrich_project_mentions()
    enrich_person_mentions()

    # --------------------------------------------------------
    # Canonical resolution
    # --------------------------------------------------------

    print(
        "\nResolving generalized mentions..."
    )

    resolve_companies()
    resolve_projects()
    resolve_people()

    # --------------------------------------------------------
    # Link AI document mentions into logical documents
    # --------------------------------------------------------

    print(
        "\nLinking generalized documents..."
    )

    link_ai_document_mentions()


def run_pipeline(
    reset_database: bool = True,
    generalized_source_ids: list[int] | None = None,
):

    print("=" * 80)
    print("ENTITY RESOLUTION PIPELINE")
    print("=" * 80)

    # ========================================================
    # DATABASE
    # ========================================================

    if reset_database and DATABASE_PATH.exists():

        print(
            "\nResetting existing knowledge database..."
        )

        DATABASE_PATH.unlink()

    print(
        "\n[1/12] Initialising database..."
    )

    initialize_database()

    # ========================================================
    # SOURCE INGESTION
    # ========================================================

    print(
        "\n[2/12] Scanning source files..."
    )

    scan_dataset()

    # ========================================================
    # LOGICAL DOCUMENTS
    # ========================================================

    print(
        "\n[3/12] Building logical documents..."
    )

    build_documents()

    # ========================================================
    # DOCUMENT VERIFICATION
    # ========================================================

    print(
        "\n[4/12] Verifying document identities..."
    )

    verify_filename_inferred_pdfs()
    build_verified_pdf_documents()

    # ========================================================
    # TRUSTED FOLDER MENTIONS
    # ========================================================

    print(
        "\n[5/12] Extracting folder entity mentions..."
    )

    extract_folder_mentions()

    # ========================================================
    # CANONICAL COMPANIES + PROJECTS
    # ========================================================

    print(
        "\n[6/12] Resolving companies and projects..."
    )

    resolve_companies()
    resolve_projects()

    # ========================================================
    # EMAIL PERSON MENTIONS
    # ========================================================

    print(
        "\n[7/12] Extracting email person mentions..."
    )

    extract_email_person_mentions()

    # ========================================================
    # CANONICAL PEOPLE
    # ========================================================

    print(
        "\n[8/12] Resolving people..."
    )

    resolve_people()

    # ========================================================
    # CONTENT-DERIVED COMPANY MENTIONS
    # ========================================================

    print(
        "\n[9/12] Extracting and resolving PDF company mentions..."
    )

    extract_pdf_company_mentions()
    resolve_company_mentions()

    # ========================================================
    # GENERALIZED PROCESSING
    # ========================================================

    print(
        "\n[10/12] Generalized processing..."
    )

    if generalized_source_ids:

        run_generalized_processing(
            generalized_source_ids
        )

    else:

        print(
            "Skipped. No generalized source files were selected."
        )

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    print(
        "\n[11/12] Building relationships..."
    )

    build_company_project_relationships()
    build_document_project_relationships()
    build_document_company_relationships()
    build_email_documents_and_relationships()
    build_document_reference_relationships()

    # ========================================================
    # FINAL DATA QUALITY
    # ========================================================

    print(
        "\n[12/12] Running final data quality checks..."
    )

    audit_extractions()

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()