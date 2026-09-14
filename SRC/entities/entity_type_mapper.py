ENTITY_TYPE_MAP = {
    "organisation": "company",
    "organization": "company",
    "company": "company",

    "job_or_project": "project",
    "project": "project",
    "job": "project",

    "person": "person",

    "document": "document",
}


def map_entity_type(
    entity_type: str | None,
):
    """
    Map generalized schema entity names onto the
    canonical entity types used by the existing system.

    Unknown types are preserved rather than discarded.
    """

    if not entity_type:
        return None

    normalized_type = (
        entity_type
        .strip()
        .lower()
    )

    return ENTITY_TYPE_MAP.get(
        normalized_type,
        normalized_type,
    )