import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from SRC.config_loader import get_entity_types


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============================================================
# ACTIVE ENTITY SCHEMA
# ============================================================

def get_active_entity_types():
    """
    Return entity types currently approved in schema.yaml.
    """

    return get_entity_types()


# ============================================================
# EXTRACTION SPECIFICATION
# ============================================================

def build_entity_extraction_spec(
    text: str,
):
    """
    Build an extraction specification from the active schema.
    """

    entity_types = get_active_entity_types()

    schema_items = []

    for entity_name, config in entity_types.items():

        suggested_fields = config.get(
            "suggested_fields",
            config.get(
                "fields",
                [],
            ),
        )

        schema_items.append(
            {
                "entity_type": entity_name,
                "suggested_fields": suggested_fields,
            }
        )

    return {
        "text": text,
        "entity_schema": schema_items,
    }


# ============================================================
# OPENAI ENTITY EXTRACTION
# ============================================================

def extract_entities_with_ai(
    text: str,
):
    """
    Extract entity mentions using only entity types approved
    in schema.yaml.

    Important:
    - This extracts observations/mentions only.
    - It does NOT merge entities.
    - It does NOT create canonical identities.
    """

    if not text or not text.strip():
        return {
            "entities": []
        }

    extraction_spec = (
        build_entity_extraction_spec(
            text
        )
    )

    entity_schema = extraction_spec[
        "entity_schema"
    ]

    if not entity_schema:
        return {
            "entities": [],
            "warning":
                "No active entity types are defined in schema.yaml",
        }

    system_prompt = """
You are an entity mention extraction component in an
evidence-backed knowledge modelling system.

You must extract observations from the supplied document text.

Important rules:

1. Only use entity types explicitly supplied in the active schema.
2. Do not invent unsupported entities.
3. Do not merge similar names.
4. Do not decide whether two mentions refer to the same real-world entity.
5. Preserve the exact observed name where possible.
6. Extract attributes only when they are explicitly supported by the text.
7. Do not infer missing values.
8. Preserve ambiguity instead of guessing.
9. Every extracted entity must include evidence from the source text.
10. Return JSON only.

An extracted entity is an observed mention, not a canonical record.
"""

    user_prompt = f"""
ACTIVE ENTITY SCHEMA:

{json.dumps(
    entity_schema,
    indent=2,
)}

DOCUMENT TEXT:

{text[:12000]}


Return JSON using exactly this structure:

{{
  "entities": [
    {{
      "entity_type": "one approved entity type",
      "observed_name": "exact observed name or identifier",
      "attributes": {{
        "field_name": "explicitly observed value"
      }},
      "evidence": "short supporting text from the document",
      "confidence": 0.0
    }}
  ],
  "ambiguities": []
}}

Confidence must be between 0 and 1.

If something is unclear, put the issue in "ambiguities"
instead of guessing.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    raw_output = response.output_text

    try:
        result = json.loads(
            raw_output
        )

    except json.JSONDecodeError:

        return {
            "entities": [],
            "ambiguities": [],
            "error":
                "Model returned invalid JSON",
            "raw_output":
                raw_output,
        }

    return result


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    sample_text = """
    Falcon Aerospace Components Ltd

    Contact: Olivia Sullivan
    VAT Number: IE1234567A

    Project: JOB-2026-0026
    """

    result = extract_entities_with_ai(
        sample_text
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )