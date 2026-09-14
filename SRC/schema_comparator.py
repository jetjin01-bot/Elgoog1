import json
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ACTIVE_SCHEMA_PATH = (
    PROJECT_ROOT
    / "config"
    / "schema.yaml"
)

PROPOSED_SCHEMA_PATH = (
    PROJECT_ROOT
    / "config"
    / "proposed_schema.json"
)


def load_active_schema():
    with open(
        ACTIVE_SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file) or {}


def load_proposed_schema():
    with open(
        PROPOSED_SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def compare_section(
    active_section: dict,
    proposed_section: dict,
):
    active_keys = set(
        active_section.keys()
    )

    proposed_keys = set(
        proposed_section.keys()
    )

    added = sorted(
        proposed_keys - active_keys
    )

    missing = sorted(
        active_keys - proposed_keys
    )

    shared = sorted(
        active_keys & proposed_keys
    )

    changed = []

    unchanged = []

    for key in shared:

        if (
            active_section.get(key)
            ==
            proposed_section.get(key)
        ):
            unchanged.append(
                key
            )

        else:
            changed.append(
                key
            )

    return {
        "added": added,
        "missing_from_proposal": missing,
        "changed": changed,
        "unchanged": unchanged,
    }


def compare_schemas():
    active = load_active_schema()
    proposed = load_proposed_schema()

    document_comparison = (
        compare_section(
            active.get(
                "document_types",
                {},
            ),
            proposed.get(
                "document_types",
                {},
            ),
        )
    )

    entity_comparison = (
        compare_section(
            active.get(
                "entity_types",
                {},
            ),
            proposed.get(
                "entity_types",
                {},
            ),
        )
    )

    relationship_comparison = (
        compare_section(
            active.get(
                "relationship_types",
                {},
            ),
            proposed.get(
                "relationship_types",
                {},
            ),
        )
    )

    ambiguities = proposed.get(
        "ambiguities",
        [],
    )

    return {
        "document_types":
            document_comparison,

        "entity_types":
            entity_comparison,

        "relationship_types":
            relationship_comparison,

        "ambiguities":
            ambiguities,
    }


def print_comparison(
    comparison: dict,
):
    print(
        "\n"
        "======================================"
    )

    print(
        "SCHEMA COMPARISON"
    )

    print(
        "======================================"
    )

    for section_name in [
        "document_types",
        "entity_types",
        "relationship_types",
    ]:

        section = comparison[
            section_name
        ]

        print(
            f"\n[{section_name}]"
        )

        print(
            "Added:",
            section["added"],
        )

        print(
            "Changed:",
            section["changed"],
        )

        print(
            "Missing from proposal:",
            section[
                "missing_from_proposal"
            ],
        )

        print(
            "Unchanged:",
            section["unchanged"],
        )

    print(
        "\n[ambiguities]"
    )

    ambiguities = comparison.get(
        "ambiguities",
        [],
    )

    if ambiguities:

        for index, ambiguity in enumerate(
            ambiguities,
            start=1,
        ):
            print(
                f"{index}. {ambiguity}"
            )

    else:
        print(
            "None"
        )


if __name__ == "__main__":

    comparison = compare_schemas()

    print_comparison(
        comparison
    )