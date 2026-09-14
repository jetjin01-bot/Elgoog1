import json
import os
import random

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from SRC.Ingestion.extraction.content_extractor import extract_content

load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
You are helping design a generalised knowledge extraction system.

Your task is to inspect sample document text and propose a schema.

You should identify:
1. likely document types
2. likely entity types
3. useful fields for each entity/document type
4. likely relationship types

Important rules:
- Do not invent types unless supported by the samples.
- Preserve ambiguity where appropriate.
- Prefer reusable/general schema concepts.
- Do not resolve or merge entities.
- Return JSON only.
"""

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROPOSED_SCHEMA_PATH = (
    PROJECT_ROOT
    / "config"
    / "proposed_schema.json"
)

def save_proposed_schema(
    schema: dict,
):
    PROPOSED_SCHEMA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        PROPOSED_SCHEMA_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            schema,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Proposed schema saved to: "
        f"{PROPOSED_SCHEMA_PATH}"
    )

def discover_schema(sample_texts: list[str]):
    """
    Send sample document text to OpenAI
    and return a proposed schema.
    """

    combined_samples = []

    for index, text in enumerate(sample_texts, start=1):
        combined_samples.append(
            f"""
--- SAMPLE {index} ---
{text[:5000]}
"""
        )

    user_prompt = f"""
Review the following sample documents and propose a schema.

Return JSON in this structure:

{{
  "document_types": {{
    "example_type": {{
      "identifiers": [],
      "suggested_fields": []
    }}
  }},
  "entity_types": {{
    "example_entity": {{
      "suggested_fields": []
    }}
  }},
  "relationship_types": {{
    "EXAMPLE_RELATIONSHIP": {{
      "source": "entity_type",
      "target": "entity_type",
      "description": ""
    }}
  }},
  "ambiguities": []
}}

Samples:

{''.join(combined_samples)}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    raw_output = response.output_text

    try:
        return json.loads(raw_output)

    except json.JSONDecodeError:
        return {
            "error": "Model did not return valid JSON",
            "raw_output": raw_output,
        }


if __name__ == "__main__":

    DATASET_ROOT = Path(
        os.getenv(
            "DATASET_ROOT",
            "data/raw",
        )
    )


    def sample_dataset_files(
            root: Path,
            sample_size: int = 15,
    ):
        supported_extensions = {
            ".pdf",
            ".txt",
            ".eml",
        }

        files = [
            path
            for path in root.rglob("*")
            if (
                    path.is_file()
                    and path.suffix.lower()
                    in supported_extensions
            )
        ]

        if len(files) <= sample_size:
            return files

        return random.sample(
            files,
            sample_size,
        )


    def extract_sample_texts(
            file_paths,
    ):
        samples = []

        for file_path in file_paths:

            try:
                content = extract_content(
                    file_path
                )

                text = content.get(
                    "text",
                    "",
                )

                if not text.strip():
                    continue

                samples.append(
                    f"""
    FILE: {file_path.name}
    PATH: {file_path}

    {text[:5000]}
    """
                )

            except Exception as exc:
                print(
                    f"Skipping {file_path}: {exc}"
                )

        return samples


    if __name__ == "__main__":
        sampled_files = sample_dataset_files(
            DATASET_ROOT,
            sample_size=15,
        )

        print(
            f"Sampled files: "
            f"{len(sampled_files)}"
        )

        sample_texts = extract_sample_texts(
            sampled_files
        )

        print(
            f"Usable text samples: "
            f"{len(sample_texts)}"
        )

        result = discover_schema(
            sample_texts
        )

        save_proposed_schema(
            result
        )

        print(
            json.dumps(
                result,
                indent=2,
            )
        )