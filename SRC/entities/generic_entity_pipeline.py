import sqlite3
from pathlib import Path

from SRC.database import DATABASE_PATH
from SRC.Ingestion.extraction.content_extractor import extract_content
from SRC.entities.generic_entity_extractor import extract_entities_with_ai
from SRC.entities.generic_entity_writer import write_ai_entities
from SRC.entities.generic_document_writer import write_ai_documents


def process_source_file_with_ai(
    source_file_id: int,
    file_path,
):
    try:
        content = extract_content(
            file_path
        )

        text = content.get(
            "text",
            "",
        )

        if not text.strip():
            return {
                "source_file_id": source_file_id,
                "status": "skipped",
                "reason": "no_extractable_text",
                "mentions_created": 0,
                "documents_created": 0,
            }

        extraction_result = extract_entities_with_ai(
            text
        )

        mention_ids = write_ai_entities(
            source_file_id=source_file_id,
            extraction_result=extraction_result,
        )

        document_results = write_ai_documents(
            source_file_id=source_file_id,
            extraction_result=extraction_result,
        )

        return {
            "source_file_id": source_file_id,
            "status": "processed",
            "mentions_created": len(
                mention_ids
            ),
            "documents_created": sum(
                1
                for result in document_results
                if result.get("status") == "created"
            ),
            "ambiguities": extraction_result.get(
                "ambiguities",
                [],
            ),
        }

    except Exception as exc:
        return {
            "source_file_id": source_file_id,
            "status": "error",
            "error": (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
            "mentions_created": 0,
            "documents_created": 0,
        }


def process_sample_files(
    limit: int = 5,
):
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    rows = connection.execute(
        """
        SELECT
            id,
            file_path
        FROM source_files
        WHERE ingestion_status = 'scanned'
          AND LOWER(extension) IN (
              '.pdf',
              '.txt',
              '.eml'
          )
          AND filename NOT LIKE '~$%'
          AND filename NOT LIKE 'corrupt_%'
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (
            limit,
        ),
    ).fetchall()

    connection.close()

    results = []

    for source_file_id, file_path in rows:

        print(
            f"Processing source file "
            f"{source_file_id}: "
            f"{file_path}"
        )

        result = process_source_file_with_ai(
            source_file_id=source_file_id,
            file_path=Path(file_path),
        )

        results.append(
            result
        )

        print(
            result
        )

    return results


def process_specific_source_files(
    source_file_ids: list[int],
):
    if not source_file_ids:
        return []

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    placeholders = ",".join(
        "?"
        for _ in source_file_ids
    )

    rows = connection.execute(
        f"""
        SELECT
            id,
            file_path
        FROM source_files
        WHERE id IN ({placeholders})
        """,
        source_file_ids,
    ).fetchall()

    connection.close()

    results = []

    for source_file_id, file_path in rows:

        print(
            f"Processing source file "
            f"{source_file_id}: "
            f"{file_path}"
        )

        result = process_source_file_with_ai(
            source_file_id=source_file_id,
            file_path=Path(file_path),
        )

        results.append(
            result
        )

        print(
            result
        )

    return results