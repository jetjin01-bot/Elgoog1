import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROPOSED_SCHEMA_PATH = (
    PROJECT_ROOT
    / "config"
    / "proposed_schema.json"
)


# ============================================================
# HEURISTICS
# ============================================================

ATTRIBUTE_LIKE_NAMES = {
    "address",
    "technical_parameter",
    "contractual_term",
    "finding_or_metric",
}

LIKELY_ENTITY_NAMES = {
    "person",
    "organisation",
    "company",
    "project",
    "job_or_project",
    "product_or_equipment",
    "document",
}

CONTEXT_DEPENDENT_NAMES = {
    "line_item",
    "service",
    "site_visit",
}


def load_proposed_schema():
    with open(
        PROPOSED_SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def classify_entity_candidate(
    entity_name: str,
    entity_config: dict,
):
    """
    Classify a proposed entity type into a review category.

    This does NOT automatically accept or reject anything.
    It only assigns a review recommendation.
    """

    normalized_name = (
        entity_name
        .strip()
        .lower()
    )

    if normalized_name in LIKELY_ENTITY_NAMES:
        return {
            "classification": "likely_entity",
            "review_required": False,
            "reason":
                "Represents a potentially independent object "
                "with its own identity or lifecycle.",
        }

    if normalized_name in ATTRIBUTE_LIKE_NAMES:
        return {
            "classification": "likely_attribute",
            "review_required": True,
            "reason":
                "May be better represented as a field or "
                "structured attribute rather than a canonical entity.",
        }

    if normalized_name in CONTEXT_DEPENDENT_NAMES:
        return {
            "classification": "context_dependent",
            "review_required": True,
            "reason":
                "Could be an entity in some domains, but could also "
                "be embedded within another entity or document.",
        }

    suggested_fields = entity_config.get(
        "suggested_fields",
        [],
    )

    # Generic heuristic:
    # if AI proposes several stable fields, it may deserve entity status.
    if len(suggested_fields) >= 3:
        return {
            "classification": "possible_entity",
            "review_required": True,
            "reason":
                "Has multiple proposed fields and may represent "
                "a structured object, but requires review.",
        }

    return {
        "classification": "needs_review",
        "review_required": True,
        "reason":
            "Insufficient evidence to determine whether this should "
            "be a canonical entity or an attribute.",
    }


def validate_entities(
    proposed_schema: dict,
):
    entity_types = proposed_schema.get(
        "entity_types",
        {},
    )

    results = {}

    for entity_name, entity_config in entity_types.items():

        results[entity_name] = (
            classify_entity_candidate(
                entity_name,
                entity_config,
            )
        )

    return results


def validate_relationships(
    proposed_schema: dict,
):
    relationships = proposed_schema.get(
        "relationship_types",
        {},
    )

    entity_types = set(
        proposed_schema.get(
            "entity_types",
            {},
        ).keys()
    )

    document_types = set(
        proposed_schema.get(
            "document_types",
            {},
        ).keys()
    )

    known_nodes = (
        entity_types
        | document_types
        | {"document"}
    )

    results = {}

    for relationship_name, config in relationships.items():

        source = config.get(
            "source"
        )

        target = config.get(
            "target"
        )

        issues = []

        if source and source not in known_nodes:
            issues.append(
                f"Unknown source type: {source}"
            )

        if target and target not in known_nodes:
            issues.append(
                f"Unknown target type: {target}"
            )

        results[
            relationship_name
        ] = {
            "valid_structure":
                len(issues) == 0,

            "review_required":
                len(issues) > 0,

            "issues":
                issues,
        }

    return results


def validate_schema():
    proposed = load_proposed_schema()

    entity_validation = (
        validate_entities(
            proposed
        )
    )

    relationship_validation = (
        validate_relationships(
            proposed
        )
    )

    return {
        "entity_validation":
            entity_validation,

        "relationship_validation":
            relationship_validation,

        "ambiguities":
            proposed.get(
                "ambiguities",
                [],
            ),
    }


def print_validation(
    validation: dict,
):
    print(
        "\n"
        "======================================"
    )

    print(
        "SCHEMA VALIDATION"
    )

    print(
        "======================================"
    )

    print(
        "\n[entity candidates]"
    )

    for (
        entity_name,
        result,
    ) in (
        validation[
            "entity_validation"
        ].items()
    ):

        print(
            f"\n{entity_name}"
        )

        print(
            "Classification:",
            result[
                "classification"
            ],
        )

        print(
            "Review required:",
            result[
                "review_required"
            ],
        )

        print(
            "Reason:",
            result[
                "reason"
            ],
        )

    print(
        "\n[relationship validation]"
    )

    for (
        relationship_name,
        result,
    ) in (
        validation[
            "relationship_validation"
        ].items()
    ):

        print(
            f"\n{relationship_name}"
        )

        print(
            "Valid structure:",
            result[
                "valid_structure"
            ],
        )

        if result["issues"]:
            print(
                "Issues:",
                result["issues"],
            )

    print(
        "\n[ambiguities]"
    )

    ambiguities = validation.get(
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

    validation = validate_schema()

    print_validation(
        validation
    )