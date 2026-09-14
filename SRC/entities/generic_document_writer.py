import sqlite3

from SRC.database import DATABASE_PATH


def find_existing_document_link(
    source_file_id: int,
):
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            ds.document_id
        FROM document_sources ds
        WHERE ds.source_file_id = ?
        LIMIT 1
        """,
        (
            source_file_id,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    return row


def create_logical_document_from_ai(
    source_file_id: int,
    observed_name: str,
    attributes: dict,
    confidence: float | None = None,
):
    """
    Create a logical document only when the source file
    is not already linked to an existing logical document.

    AI evidence is used to populate the logical document,
    but unsupported fields remain empty.
    """

    existing = find_existing_document_link(
        source_file_id
    )

    if existing:
        return {
            "status": "existing_document",
            "document_id": existing[0],
        }

    document_type = (
        attributes.get("document_type")
        or "other"
    )

    document_number = (
        attributes.get("document_number")
    )

    title = (
        attributes.get("title")
    )

    document_date = (
        attributes.get("date")
        or attributes.get("document_date")
    )

    # If AI only produced a generic phrase such as
    # "this letter", do not treat that as a formal title.
    if (
        not title
        and observed_name
        and observed_name.lower()
        not in {
            "this letter",
            "letter",
            "document",
            "report",
        }
    ):
        title = observed_name

    # Prefer document number as canonical key.
    # Otherwise fall back to a source-specific key.
    if document_number:
        canonical_key = (
            f"{document_type}:"
            f"{document_number}"
        )
    else:
        canonical_key = (
            f"source:{source_file_id}:"
            f"{document_type}"
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            document_type,
            document_number,
            title,
            document_date,
            canonical_key,
            extraction_confidence,
            resolution_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            document_type,
            document_number,
            title,
            document_date,
            canonical_key,
            confidence,
            "resolved_from_ai_evidence",
        ),
    )

    document_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO document_sources (
            document_id,
            source_file_id,
            source_role
        )
        VALUES (?, ?, ?)
        """,
        (
            document_id,
            source_file_id,
            "ai_discovered_representation",
        ),
    )

    connection.commit()
    connection.close()

    return {
        "status": "created",
        "document_id": document_id,
    }


def write_ai_documents(
    source_file_id: int,
    extraction_result: dict,
):
    """
    Process AI-extracted document mentions.

    Only creates logical documents when no logical document
    already exists for the same source file.
    """

    entities = extraction_result.get(
        "entities",
        [],
    )

    results = []

    for entity in entities:

        entity_type = entity.get(
            "entity_type"
        )

        if entity_type != "document":
            continue

        observed_name = entity.get(
            "observed_name"
        )

        attributes = entity.get(
            "attributes",
            {},
        )

        confidence = entity.get(
            "confidence"
        )

        result = (
            create_logical_document_from_ai(
                source_file_id=source_file_id,
                observed_name=observed_name,
                attributes=attributes,
                confidence=confidence,
            )
        )

        results.append(
            result
        )

    return results