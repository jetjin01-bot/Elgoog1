import sqlite3

from SRC.database import DATABASE_PATH
from SRC.entities.entity_type_mapper import map_entity_type


AI_EXTRACTION_METHOD = "ai_schema_extraction"


def normalize_value(
    value: str | None,
):
    """
    Lightweight normalization for observed mention values.

    This does not perform entity resolution.
    """

    if not value:
        return None

    return " ".join(
        value
        .strip()
        .lower()
        .split()
    )


def find_existing_mention(
    source_file_id: int,
    entity_type: str,
    normalized_value: str,
    extraction_method: str,
):
    """
    Check for an existing observation from the same source
    and the same extraction method.

    Observations from different extraction methods are kept
    separately because they represent independent provenance.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            identifier_value
        FROM entity_mentions
        WHERE source_file_id = ?
          AND entity_type = ?
          AND normalized_value = ?
          AND extraction_method = ?
        LIMIT 1
        """,
        (
            source_file_id,
            entity_type,
            normalized_value,
            extraction_method,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    return row


def insert_entity_mention(
    source_file_id: int,
    entity_type: str,
    observed_value: str,
    confidence: float | None = None,
    role: str | None = None,
    identifier_value: str | None = None,
):
    """
    Store an observed entity mention extracted from a source file.

    Important:
    - Does not create a canonical entity.
    - Does not merge observations from different extraction methods.
    - Prevents duplicate AI observations from repeated processing.
    - Leaves new mentions unresolved until the resolution stage.
    """

    normalized_value = normalize_value(
        observed_value
    )

    if not normalized_value:
        return None

    existing = find_existing_mention(
        source_file_id=source_file_id,
        entity_type=entity_type,
        normalized_value=normalized_value,
        extraction_method=AI_EXTRACTION_METHOD,
    )

    # --------------------------------------------------------
    # Same AI observation already exists
    # --------------------------------------------------------

    if existing:

        existing_id = existing[0]
        existing_identifier = existing[1]

        # If a later extraction provides a useful identifier,
        # enrich the existing AI observation rather than
        # creating a duplicate.
        if (
            not existing_identifier
            and identifier_value
        ):
            connection = sqlite3.connect(
                DATABASE_PATH
            )

            connection.execute(
                """
                UPDATE entity_mentions
                SET identifier_value = ?
                WHERE id = ?
                """,
                (
                    identifier_value,
                    existing_id,
                ),
            )

            connection.commit()
            connection.close()

        return None

    # --------------------------------------------------------
    # New AI observation
    # --------------------------------------------------------

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO entity_mentions (
            entity_type,
            observed_value,
            normalized_value,
            identifier_value,
            source_file_id,
            role,
            extraction_method,
            confidence,
            resolution_status,
            resolved_entity_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entity_type,
            observed_value,
            normalized_value,
            identifier_value,
            source_file_id,
            role,
            AI_EXTRACTION_METHOD,
            confidence,
            "unresolved",
            None,
        ),
    )

    mention_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return mention_id


def write_ai_entities(
    source_file_id: int,
    extraction_result: dict,
):
    """
    Write AI-extracted observations into entity_mentions.

    Returns IDs for newly inserted mention records.
    """

    entities = extraction_result.get(
        "entities",
        [],
    )

    mention_ids = []

    for entity in entities:

        entity_type = map_entity_type(
            entity.get(
                "entity_type"
            )
        )

        observed_value = entity.get(
            "observed_name"
        )

        confidence = entity.get(
            "confidence"
        )

        attributes = entity.get(
            "attributes",
            {},
        )

        if not entity_type:
            continue

        if not observed_value:
            continue

        identifier_value = None

        # ----------------------------------------------------
        # Safe identifiers already present in AI extraction
        # ----------------------------------------------------

        if entity_type == "person":

            identifier_value = (
                attributes.get(
                    "email_address"
                )
                or attributes.get(
                    "email"
                )
            )

        elif entity_type == "project":

            identifier_value = (
                attributes.get(
                    "job_reference"
                )
                or attributes.get(
                    "project_number"
                )
            )

        elif entity_type == "document":

            identifier_value = (
                attributes.get(
                    "document_number"
                )
            )

        mention_id = insert_entity_mention(
            source_file_id=source_file_id,
            entity_type=entity_type,
            observed_value=observed_value,
            confidence=confidence,
            identifier_value=identifier_value,
        )

        if mention_id is not None:

            mention_ids.append(
                mention_id
            )

    return mention_ids