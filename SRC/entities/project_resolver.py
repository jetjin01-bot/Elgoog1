import sqlite3
import re

from SRC.database import DATABASE_PATH


PROJECT_PATTERN = re.compile(
    r"^(JOB-\d{4}-\d+)\s+(.+)$",
    re.IGNORECASE,
)


def resolve_projects():
    conn = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = conn.cursor()

    # --------------------------------------------------------
    # Only process unresolved project mentions.
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            id,
            observed_value,
            identifier_value
        FROM entity_mentions
        WHERE entity_type = 'project'
          AND resolution_status = 'unresolved'
        ORDER BY id
    """)

    rows = cursor.fetchall()

    groups = {}

    # --------------------------------------------------------
    # Build groups by job number.
    # --------------------------------------------------------

    for (
        mention_id,
        observed_value,
        identifier_value,
    ) in rows:

        job_number = None
        project_name = None

        # ----------------------------------------------------
        # First preference:
        # explicit identifier_value from enrichment.
        # ----------------------------------------------------

        if identifier_value:
            job_number = (
                identifier_value
                .strip()
                .upper()
            )

            project_name = (
                observed_value.strip()
                if observed_value
                else None
            )

        # ----------------------------------------------------
        # Fallback:
        # parse old deterministic mention format.
        # ----------------------------------------------------

        else:
            match = PROJECT_PATTERN.match(
                observed_value
            )

            if not match:
                continue

            job_number = (
                match.group(1)
                .upper()
            )

            project_name = (
                match.group(2)
                .strip()
            )

        groups.setdefault(
            job_number,
            {
                "project_names": [],
                "mentions": [],
            }
        )

        if project_name:
            groups[
                job_number
            ][
                "project_names"
            ].append(
                project_name
            )

        groups[
            job_number
        ][
            "mentions"
        ].append(
            mention_id
        )

    project_count = 0
    resolved_count = 0

    # --------------------------------------------------------
    # Resolve each job-number group.
    # --------------------------------------------------------

    for job_number, data in groups.items():

        # ----------------------------------------------------
        # First check whether canonical project already exists.
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                canonical_name
            FROM projects
            WHERE job_number = ?
            LIMIT 1
        """, (
            job_number,
        ))

        existing = cursor.fetchone()

        if existing:
            project_id = existing[0]

        else:
            # -----------------------------------------------
            # No existing canonical project.
            #
            # Only create one if we have a meaningful name.
            # -----------------------------------------------

            if not data[
                "project_names"
            ]:
                continue

            frequency = {}

            for name in data[
                "project_names"
            ]:
                frequency[name] = (
                    frequency.get(
                        name,
                        0,
                    )
                    + 1
                )

            canonical_name = max(
                frequency,
                key=frequency.get,
            )

            cursor.execute("""
                INSERT INTO projects (
                    job_number,
                    canonical_name,
                    resolution_status,
                    confidence
                )
                VALUES (?, ?, ?, ?)
            """, (
                job_number,
                canonical_name,
                "resolved_deterministically",
                0.99,
            ))

            project_id = (
                cursor.lastrowid
            )

            project_count += 1

        # ----------------------------------------------------
        # Link mentions to canonical project.
        # ----------------------------------------------------

        for mention_id in data[
            "mentions"
        ]:

            cursor.execute("""
                UPDATE entity_mentions
                SET
                    resolution_status = 'resolved',
                    resolved_entity_id = ?
                WHERE id = ?
            """, (
                project_id,
                mention_id,
            ))

            resolved_count += 1

    conn.commit()
    conn.close()

    print(
        "=" * 70
    )

    print(
        "PROJECT RESOLUTION"
    )

    print(
        "=" * 70
    )

    print(
        f"Project mentions processed: {len(rows)}"
    )

    print(
        f"Project mentions resolved:  {resolved_count}"
    )

    print(
        f"Canonical projects created: {project_count}"
    )