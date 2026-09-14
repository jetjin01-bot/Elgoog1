from SRC.entities.company_resolver import resolve_companies
from SRC.entities.project_resolver import resolve_projects
from SRC.entities.person_resolver import resolve_people


def run_generic_resolution():
    """
    Route generalized AI-extracted mentions into the existing
    deterministic canonical resolution layer.

    AI extraction produces observed mentions only.
    Canonical resolution remains deterministic.
    """

    results = {}

    print(
        "Running company resolution..."
    )

    company_result = resolve_companies()

    results[
        "company"
    ] = company_result


    print(
        "Running project resolution..."
    )

    project_result = resolve_projects()

    results[
        "project"
    ] = project_result


    print(
        "Running person resolution..."
    )

    person_result = resolve_people()

    results[
        "person"
    ] = person_result


    print(
        "Generic resolution routing complete."
    )

    return results


if __name__ == "__main__":

    results = run_generic_resolution()

    print(
        results
    )