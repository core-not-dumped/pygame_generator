import re
from pathlib import Path
import os
import json

def clean_raw_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Remove leading language label like "python"
    text = re.sub(r"^\s*python\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*json\s*\n", "", text, flags=re.IGNORECASE)

    return text


def safe_dir_name(name: str) -> str:
    name = name.lower().strip()

    # Replace Windows-invalid filename characters with underscore
    name = re.sub(r'[<>:"/\\|?*]', "_", name)

    # Replace spaces and repeated underscores
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)

    # Remove leading/trailing dots, spaces, underscores
    name = name.strip(" ._")

    return name or "generated_game"


def read_project_py_files(folder_path: str) -> dict[str, str]:
    files = {}

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".py"):
            continue

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            files[file_name] = f.read()

    return files


def save_generated_game(code: str, title: str) -> Path:
    game_name = safe_dir_name(title)
    output_dir = Path("generated_games") / game_name
    output_dir.mkdir(parents=True, exist_ok=True)

    main_path = output_dir / "main.py"
    main_path.write_text(code, encoding="utf-8")

    return main_path


def save_json_dict(data: dict, file_path: str) -> None:
    folder = os.path.dirname(file_path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_py_file(code: str, file_name: str) -> str:
    if not isinstance(code, str) or not code.strip():
        raise ValueError("code must be a non-empty string.")

    if not file_name.endswith(".py"):
        file_name += ".py"

    folder = os.path.dirname(file_name)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)

    return file_name