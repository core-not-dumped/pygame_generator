import json
from prompts import *
from ollama import chat

from utils import *


def validate_function_plan(plan: dict) -> None:
    required_top_keys = [
        "project_title",
        "architecture_summary",
        "global_constants",
        "data_structures",
        "functions",
    ]

    for key in required_top_keys:
        if key not in plan:
            raise ValueError(f"Function plan is missing required key: {key}")

    if not isinstance(plan["functions"], list):
        raise ValueError("'functions' must be a list.")

    if len(plan["functions"]) == 0:
        raise ValueError("'functions' must not be empty.")

    function_names = set()

    for idx, func in enumerate(plan["functions"]):
        required_function_keys = [
            "name",
            "category",
            "purpose",
            "parameters",
            "returns",
            "uses",
            "called_by",
            "implementation_notes",
            "order",
        ]

        for key in required_function_keys:
            if key not in func:
                raise ValueError(f"Function at index {idx} is missing key: {key}")

        name = func["name"]

        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Function at index {idx} has invalid name.")

        if name in function_names:
            raise ValueError(f"Duplicate function name found: {name}")

        function_names.add(name)


def analyze_required_functions(
    game_spec: dict | str,
    model: str = "qwen2.5-coder:7b",
) -> dict:
    """
    Analyze a detailed game specification and return a JSON function plan
    for step-by-step pygame implementation.

    Parameters
    ----------
    game_spec:
        Detailed game specification as dict or JSON string.
    model:
        Ollama model name.

    Returns
    -------
    dict:
        Function architecture plan.
    """

    if isinstance(game_spec, dict):
        game_spec_text = json.dumps(game_spec, indent=2, ensure_ascii=False)
    elif isinstance(game_spec, str):
        game_spec_text = game_spec
    else:
        raise TypeError("game_spec must be either dict or JSON string.")

    prompt = FUNCTION_ANALYSIS_PROMPT.replace(
        "__game_spec__",
        game_spec_text,
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. "
                    "Return valid JSON only. "
                    "Do not include markdown or explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
            "top_p": 0.8,
        },
    )

    raw_text = response["message"]["content"]
    clean_text = clean_raw_text(raw_text)

    try:
        function_plan = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON:\n{raw_text}"
        ) from e

    if not isinstance(function_plan, dict):
        raise ValueError("Expected a JSON object for function plan.")

    validate_function_plan(function_plan)

    return function_plan



def validate_globals_code_basic(code: str) -> None:
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Generated globals.py code is empty.")

    forbidden_markers = [
        "```",
        "Here is",
        "Here's",
        "Explanation",
    ]

    for marker in forbidden_markers:
        if marker in code:
            raise ValueError(
                f"Generated globals.py contains forbidden text: {marker}"
            )

    try:
        compile(code, "globals.py", "exec")
    except SyntaxError as e:
        raise ValueError(
            f"Generated globals.py has invalid Python syntax:\n{code}"
        ) from e


def generate_globals_code(
    function_plan: dict,
    model: str = "qwen2.5-coder:7b",
) -> str:
    function_plan_text = json.dumps(
        function_plan,
        indent=2,
        ensure_ascii=False,
    )

    prompt = GLOBALS_CODE_PROMPT.replace(
        "__function_plan__",
        function_plan_text,
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python code generator. "
                    "Return valid Python code only. "
                    "Do not include markdown or explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
            "top_p": 0.8,
        },
    )

    raw_text = response["message"]["content"]
    code = clean_raw_text(raw_text)

    validate_globals_code_basic(code)

    return code


def generate_single_function_file_code(
    function_plan: dict,
    function_spec: dict,
    model: str = "qwen2.5-coder:7b",
) -> str:
    function_name = function_spec["name"]

    global_constants_text = json.dumps(
        function_plan.get("global_constants", []),
        indent=2,
        ensure_ascii=False,
    )

    data_structures_text = json.dumps(
        function_plan.get("data_structures", []),
        indent=2,
        ensure_ascii=False,
    )

    function_spec_text = json.dumps(
        function_spec,
        indent=2,
        ensure_ascii=False,
    )

    all_function_names = [
        func["name"]
        for func in function_plan.get("functions", [])
        if isinstance(func, dict) and "name" in func
    ]

    all_function_names_text = json.dumps(
        all_function_names,
        indent=2,
        ensure_ascii=False,
    )

    prompt = (
        SINGLE_FUNCTION_FILE_PROMPT
        .replace("__function_name__", function_name)
        .replace("__global_constants__", global_constants_text)
        .replace("__data_structures__", data_structures_text)
        .replace("__function_spec__", function_spec_text)
        .replace("__all_function_names__", all_function_names_text)
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python code generator. "
                    "Return valid Python code only. "
                    "Do not include markdown or explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
            "top_p": 0.8,
        },
    )

    raw_text = response["message"]["content"]
    code = clean_raw_text(raw_text)

    return code


def generate_main_code(
    best_candidate: dict | str,
    function_plan: dict,
    model: str = "qwen2.5-coder:7b",
) -> str:
    """
    Generate complete main.py code from best_candidate and function_plan.

    Parameters
    ----------
    best_candidate:
        Detailed game specification as dict or JSON string.
    function_plan:
        Function architecture plan generated by analyze_required_functions().
    model:
        Ollama model name.

    Returns
    -------
    str:
        Complete Python source code for main.py.
    """

    if isinstance(best_candidate, dict):
        best_candidate_text = json.dumps(
            best_candidate,
            indent=2,
            ensure_ascii=False,
        )
    elif isinstance(best_candidate, str):
        best_candidate_text = best_candidate
    else:
        raise TypeError("best_candidate must be either dict or JSON string.")

    function_plan_text = json.dumps(
        function_plan,
        indent=2,
        ensure_ascii=False,
    )

    prompt = (
        MAIN_CODE_PROMPT
        .replace("__best_candidate__", best_candidate_text)
        .replace("__function_plan__", function_plan_text)
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python code generator. "
                    "Return valid Python code only. "
                    "Do not include markdown or explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.2,
            "top_p": 0.8,
        },
    )

    raw_text = response["message"]["content"]
    code = clean_raw_text(raw_text)

    return code