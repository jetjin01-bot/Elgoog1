import re
import sqlite3

from SRC.database import DATABASE_PATH


PROJECT_FOLDER_PATTERN = re.compile(
    r"(JOB-\d{4}-\d{4})\s+(.+)",
    re.IGNORECASE,
)


def extract_project_from_folder_context(
    file_path: str,
):
    """
    Extract project reference and project name from a source path.

    Example:
    .../JOB-2026-0008 Robotic Cell Commissioning/...

    returns:
    {
        "job_reference": "JOB-2026-0008",
        "project_name": "Robotic Cell Commissioning"
    }
    """

    if not file_path:
        return None

    path_parts = (
        file_path
        .replace("\\", "/")
        .split("/")
    )

    for part in path_parts:

        match = PROJECT_FOLDER_PATTERN.match(
            part.strip()
        )

        if match:

            return {
                "job_reference":
                    match.group(1).upper(),

                "project_name":
                    match.group(2).strip(),
            }

    return None


def normalize_text(
    value: str | None,
):
    if not value:
        return None

    return " ".join(
        value
        .strip()
        .lower()
        .split()
    )


def enrich_project_mentions():
    """
    Enrich unresolved AI project mentions using project context
    already present in the source file path.

    Folder context is treated as supporting evidence,
    not as absolute truth.
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
            em.identifier_value,
            sf.file_path
        FROM entity_mentions em
        JOIN source_files sf
          ON sf.id = em.source_file_id
        WHERE em.entity_type = 'project'
          AND em.extraction_method = 'ai_schema_extraction'
          AND em.resolution_status = 'unresolved'
        ORDER BY em.id
        """
    )

    rows = cursor.fetchall()

    enriched_count = 0
    skipped_count = 0

    for (
        mention_id,
        observed_value,
        identifier_value,
        file_path,
    ) in rows:

        # Already has an identifier.
        if identifier_value:
            skipped_count += 1
            continue

        folder_project = (
            extract_project_from_folder_context(
                file_path
            )
        )

        if not folder_project:
            skipped_count += 1
            continue

        observed_normalized = normalize_text(
            observed_value
        )

        folder_name_normalized = normalize_text(
            folder_project[
                "project_name"
            ]
        )

        # Conservative rule:
        # Only enrich when the project name extracted by AI
        # matches the project name present in the folder context.
        if (
            observed_normalized
            != folder_name_normalized
        ):
            skipped_count += 1
            continue

        cursor.execute(
            """
            UPDATE entity_mentions
            SET identifier_value = ?
            WHERE id = ?
            """,
            (
                folder_project[
                    "job_reference"
                ],
                mention_id,
            ),
        )

        enriched_count += 1

    connection.commit()
    connection.close()

    print(
        "=" * 70
    )

    print(
        "PROJECT MENTION ENRICHMENT"
    )

    print(
        "=" * 70
    )

    print(
        f"Project mentions checked: {len(rows)}"
    )

    print(
        f"Identifiers enriched:     {enriched_count}"
    )

    print(
        f"Skipped:                  {skipped_count}"
    )

def enrich_person_mentions():
    """
    Enrich unresolved AI person mentions using existing
    deterministic person mentions from the same source file.

    A match is only accepted when the names are compatible
    and the deterministic mention already has an email identifier.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            ai.id,
            ai.observed_value,
            ai.source_file_id
        FROM entity_mentions ai
        WHERE ai.entity_type = 'person'
          AND ai.extraction_method = 'ai_schema_extraction'
          AND ai.resolution_status = 'unresolved'
          AND (
              ai.identifier_value IS NULL
              OR TRIM(ai.identifier_value) = ''
          )
        ORDER BY ai.id
        """
    )

    ai_rows = cursor.fetchall()

    enriched_count = 0
    skipped_count = 0

    for (
        mention_id,
        observed_value,
        source_file_id,
    ) in ai_rows:

        cursor.execute(
            """
            SELECT
                observed_value,
                identifier_value
            FROM entity_mentions
            WHERE source_file_id = ?
              AND entity_type = 'person'
              AND extraction_method != 'ai_schema_extraction'
              AND identifier_value IS NOT NULL
              AND TRIM(identifier_value) != ''
            """,
            (
                source_file_id,
            ),
        )

        candidates = cursor.fetchall()

        if not candidates:
            skipped_count += 1
            continue

        ai_name = normalize_text(
            observed_value
        )

        matched_email = None

        for (
            candidate_name,
            candidate_email,
        ) in candidates:

            candidate_normalized = normalize_text(
                candidate_name
            )

            # Exact normalized match
            if ai_name == candidate_normalized:
                matched_email = candidate_email
                break

            # Conservative partial-name support.
            # Example:
            # "Mohammed" vs "Mohammed Okafor"
            if (
                ai_name
                and candidate_normalized
                and (
                    candidate_normalized.startswith(
                        ai_name + " "
                    )
                    or ai_name.startswith(
                        candidate_normalized + " "
                    )
                )
            ):
                matched_email = candidate_email
                break

        if not matched_email:
            skipped_count += 1
            continue

        cursor.execute(
            """
            UPDATE entity_mentions
            SET identifier_value = ?
            WHERE id = ?
            """,
            (
                matched_email,
                mention_id,
            ),
        )

        enriched_count += 1

    connection.commit()
    connection.close()

    print(
        "=" * 70
    )

    print(
        "PERSON MENTION ENRICHMENT"
    )

    print(
        "=" * 70
    )

    print(
        f"Person mentions checked: {len(ai_rows)}"
    )

    print(
        f"Identifiers enriched:    {enriched_count}"
    )

    print(
        f"Skipped:                 {skipped_count}"
    )

if __name__ == "__main__":
    enrich_project_mentions()
    enrich_person_mentions()