import re
from pathlib import Path

from SRC.config_loader import get_document_types
from SRC.Ingestion.extraction.content_extractor import extract_content


# ============================================================
# CONFIG HELPERS
# ============================================================

def get_document_type_config(document_type: str):
    document_types = get_document_types()

    return document_types.get(
        document_type,
        {},
    )


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type_from_config(text: str):
    """
    Infer the document type using identifiers defined in
    config/schema.yaml.

    Conservative behaviour:
    - one matching type -> return it
    - multiple matching types -> ambiguous -> return None
    - no match -> return None
    """

    if not text:
        return None

    document_types = get_document_types()

    text_lower = text.lower()

    matches = []

    for document_type, config in document_types.items():

        identifiers = config.get(
            "identifiers",
            [],
        )

        for identifier in identifiers:

            if identifier.lower() in text_lower:

                matches.append(
                    document_type
                )

                break

    matches = list(
        dict.fromkeys(matches)
    )

    if len(matches) == 1:
        return matches[0]

    return None


# ============================================================
# DOCUMENT NUMBER NORMALISATION
# ============================================================

def normalize_document_number(
    value: str,
    document_type: str,
):
    """
    Normalize a document number using the prefix configured
    for that document type.
    """

    if not value:
        return value

    config = get_document_type_config(
        document_type
    )

    primary_number = config.get(
        "primary_number",
        {},
    )

    prefix = primary_number.get(
        "prefix"
    )

    value = (
        value
        .upper()
        .replace(" ", "-")
        .strip()
    )

    if not prefix:
        return value

    match = re.search(
        rf"{re.escape(prefix)}-?(\d+)",
        value,
        re.IGNORECASE,
    )

    if not match:
        return value

    return (
        f"{prefix.upper()}-"
        f"{match.group(1)}"
    )


# ============================================================
# PRIMARY DOCUMENT IDENTITY
# ============================================================

def extract_primary_document_identity(
    text: str,
    expected_type: str | None = None,
):
    """
    Extract the document's own primary identity using the
    document rules defined in schema.yaml.

    Important:
    if expected_type exists, only rules for that type are used.
    This prevents references to other document types from being
    mistaken for the identity of the current document.
    """

    if not text:
        return None

    document_types = get_document_types()

    # ========================================================
    # CASE 1
    # Expected document type already exists.
    # ========================================================

    if (
        expected_type
        and expected_type in document_types
    ):

        config = document_types[
            expected_type
        ]

        primary_number = config.get(
            "primary_number",
            {},
        )

        primary_regex = (
            primary_number.get(
                "regex"
            )
        )

        # ----------------------------------------------------
        # Strong labelled primary field
        # ----------------------------------------------------

        if primary_regex:

            pattern = re.compile(
                primary_regex,
                re.IGNORECASE,
            )

            match = pattern.search(
                text
            )

            if match:

                return {
                    "document_type":
                        expected_type,

                    "document_number":
                        normalize_document_number(
                            match.group(1),
                            expected_type,
                        ),

                    "confidence":
                        0.99,

                    "method":
                        "labelled_primary_field",
                }

        # ----------------------------------------------------
        # Same-type fallback
        # ----------------------------------------------------

        fallback_regex = config.get(
            "fallback_regex"
        )

        if fallback_regex:

            fallback_pattern = re.compile(
                fallback_regex,
                re.IGNORECASE,
            )

            match = fallback_pattern.search(
                text
            )

            if match:

                prefix = (
                    primary_number.get(
                        "prefix"
                    )
                )

                raw_number = (
                    match.group(1)
                )

                if prefix:

                    document_number = (
                        f"{prefix.upper()}-"
                        f"{raw_number}"
                    )

                else:

                    document_number = (
                        raw_number
                    )

                return {
                    "document_type":
                        expected_type,

                    "document_number":
                        document_number,

                    "confidence":
                        0.80,

                    "method":
                        "same_type_fallback",
                }

        return None

    # ========================================================
    # CASE 2
    # No expected type.
    #
    # Search across configured document types.
    # ========================================================

    matches = []

    for (
        document_type,
        config,
    ) in document_types.items():

        primary_number = config.get(
            "primary_number",
            {},
        )

        primary_regex = (
            primary_number.get(
                "regex"
            )
        )

        if not primary_regex:
            continue

        pattern = re.compile(
            primary_regex,
            re.IGNORECASE,
        )

        match = pattern.search(
            text
        )

        if match:

            matches.append(
                {
                    "document_type":
                        document_type,

                    "document_number":
                        normalize_document_number(
                            match.group(1),
                            document_type,
                        ),

                    "confidence":
                        0.95,

                    "method":
                        "labelled_primary_field_without_prior",
                }
            )

    # Conservative:
    # only return identity if exactly one type matched.
    if len(matches) == 1:
        return matches[0]

    return None


# ============================================================
# DOCUMENT PARSER
# ============================================================

def parse_document(
    file_path: Path,
    expected_type: str | None = None,
):
    """
    Extract document content and infer logical identity.

    Evidence order:

    1. Existing prior evidence, such as filename identity
    2. Config-based document classification
    3. Config-driven labelled identity extraction
    4. Config-driven same-type fallback
    """

    content = extract_content(
        file_path
    )

    text = content.get(
        "text",
        "",
    )

    # --------------------------------------------------------
    # Generic schema-driven classification
    # --------------------------------------------------------

    config_detected_type = (
        detect_document_type_from_config(
            text
        )
    )

    # Existing deterministic evidence remains stronger
    # than generic classification.
    effective_type = (
        expected_type
        or config_detected_type
    )

    # --------------------------------------------------------
    # Config-driven identity extraction
    # --------------------------------------------------------

    identity = (
        extract_primary_document_identity(
            text,
            expected_type=effective_type,
        )
    )

    return {
        "file_path":
            str(file_path),

        "filename":
            file_path.name,

        "content":
            content,

        "expected_type":
            expected_type,

        "config_detected_type":
            config_detected_type,

        "effective_type":
            effective_type,

        "identity":
            identity,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":
    print(
        "Config-driven document parser ready."
    )