from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_PATH = (
    PROJECT_ROOT
    / "config"
    / "schema.yaml"
)


def load_schema():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema config not found: {SCHEMA_PATH}"
        )

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


def get_document_types():
    schema = load_schema()

    return schema.get(
        "document_types",
        {},
    )


def get_entity_types():
    schema = load_schema()

    return schema.get(
        "entity_types",
        {},
    )


def get_relationship_types():
    schema = load_schema()

    return schema.get(
        "relationship_types",
        {},
    )