import sqlite3

from SRC.database import DATABASE_PATH


def link_ai_document_mentions():
    """
    Link unresolved AI document mentions to logical documents
    already connected to the same source file.

    This does not create new logical documents.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            em.id,
            em.observed_value,
            em.source_file_id
        FROM entity_mentions em
        WHERE em.entity_type = 'document'
          AND em.extraction_method = 'ai_schema_extraction'
          AND em.resolution_status = 'unresolved'
        ORDER BY em.id
        """
    )

    mentions = cursor.fetchall()

    linked_count = 0
    ambiguous_count = 0
    no_match_count = 0

    for (
        mention_id,
        observed_value,
        source_file_id,
    ) in mentions:

        cursor.execute(
            """
            SELECT
                d.id,
                d.document_type,
                d.document_number,
                d.title
            FROM document_sources ds
            JOIN documents d
              ON d.id = ds.document_id
            WHERE ds.source_file_id = ?
            """,
            (
                source_file_id,
            ),
        )

        candidates = cursor.fetchall()

        if len(candidates) == 1:
            document_id = candidates[0][0]

            cursor.execute(
                """
                UPDATE entity_mentions
                SET
                    resolution_status = 'resolved',
                    resolved_entity_id = ?
                WHERE id = ?
                """,
                (
                    document_id,
                    mention_id,
                ),
            )

            linked_count += 1

        elif len(candidates) > 1:
            ambiguous_count += 1

        else:
            no_match_count += 1

    connection.commit()
    connection.close()

    print(
        "=" * 70
    )

    print(
        "DOCUMENT MENTION LINKING"
    )

    print(
        "=" * 70
    )

    print(
        f"Document mentions checked: {len(mentions)}"
    )

    print(
        f"Linked:                    {linked_count}"
    )

    print(
        f"Ambiguous:                 {ambiguous_count}"
    )

    print(
        f"No logical document found: {no_match_count}"
    )


if __name__ == "__main__":
    link_ai_document_mentions()