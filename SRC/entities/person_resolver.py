import sqlite3

from SRC.database import DATABASE_PATH


def normalize_email(email):
    if not email:
        return None

    return email.strip().lower()


def normalize_name(name):
    if not name:
        return None

    return " ".join(
        name.strip().split()
    )


def resolve_people():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    # ========================================================
    # 1. LOAD UNRESOLVED PERSON MENTIONS WITH IDENTIFIERS
    # ========================================================

    cursor.execute(
        """
        SELECT
            id,
            observed_value,
            identifier_value,
            confidence,
            source_file_id
        FROM entity_mentions
        WHERE entity_type = 'person'
          AND resolution_status = 'unresolved'
          AND identifier_value IS NOT NULL
          AND TRIM(identifier_value) != ''
        ORDER BY id
        """
    )

    mentions = cursor.fetchall()

    processed_count = 0
    linked_existing_count = 0
    created_count = 0
    alias_created_count = 0

    # ========================================================
    # 2. RESOLVE EACH PERSON
    # ========================================================

    for (
        mention_id,
        observed_name,
        identifier_value,
        confidence,
        source_file_id,
    ) in mentions:

        processed_count += 1

        email = normalize_email(
            identifier_value
        )

        canonical_name = normalize_name(
            observed_name
        )

        if not email:
            continue

        # ----------------------------------------------------
        # First check whether this person already exists
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                canonical_name
            FROM people
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
            """,
            (
                email,
            ),
        )

        existing_person = cursor.fetchone()

        if existing_person:

            person_id = existing_person[0]

            cursor.execute(
                """
                UPDATE entity_mentions
                SET
                    resolved_entity_id = ?,
                    resolution_status = 'resolved'
                WHERE id = ?
                """,
                (
                    person_id,
                    mention_id,
                ),
            )

            linked_existing_count += 1

        else:

            # ------------------------------------------------
            # No canonical person exists yet
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO people (
                    canonical_name,
                    email,
                    resolution_status,
                    confidence
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    canonical_name or email,
                    email,
                    "resolved",
                    confidence,
                ),
            )

            person_id = cursor.lastrowid

            cursor.execute(
                """
                UPDATE entity_mentions
                SET
                    resolved_entity_id = ?,
                    resolution_status = 'resolved'
                WHERE id = ?
                """,
                (
                    person_id,
                    mention_id,
                ),
            )

            created_count += 1

        # ----------------------------------------------------
        # Add alias only if we have a meaningful observed name
        # and the same alias does not already exist
        # ----------------------------------------------------

        if canonical_name:

            normalized_alias = (
                canonical_name
                .strip()
                .lower()
            )

            cursor.execute(
                """
                SELECT id
                FROM aliases
                WHERE entity_type = 'person'
                  AND entity_id = ?
                  AND normalized_alias = ?
                LIMIT 1
                """,
                (
                    person_id,
                    normalized_alias,
                ),
            )

            existing_alias = cursor.fetchone()

            if not existing_alias:

                cursor.execute(
                    """
                    INSERT INTO aliases (
                        entity_type,
                        entity_id,
                        alias,
                        normalized_alias,
                        source_file_id,
                        confidence,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "person",
                        person_id,
                        canonical_name,
                        normalized_alias,
                        source_file_id,
                        confidence,
                        "observed",
                    ),
                )

                alias_created_count += 1

    connection.commit()
    connection.close()

    print("\nPerson resolution complete.")
    print(
        f"Unresolved person mentions processed: {processed_count}"
    )
    print(
        f"Linked to existing people:            {linked_existing_count}"
    )
    print(
        f"New canonical people created:         {created_count}"
    )
    print(
        f"New aliases created:                  {alias_created_count}"
    )


if __name__ == "__main__":
    resolve_people()