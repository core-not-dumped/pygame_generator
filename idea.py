import json
from ollama import chat

from utils import *
from prompts import *
from params import *

def generate_game_ideas(model: str = "qwen2.5-coder:7b") -> list[dict]:
    prompt = IDEATION_PROMPT.replace(
        "__user_direction__",
        user_direction
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON generator. Return valid JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.7,
            "top_p": 0.9,
        },
    )

    raw_text = response["message"]["content"]
    clean_text = clean_raw_text(raw_text)

    try:
        ideas = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON:\n{raw_text}") from e

    if not isinstance(ideas, list):
        raise ValueError("Expected a JSON array.")

    return ideas