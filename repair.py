from ollama import chat
import json
import subprocess
import sys

from utils import *
from prompts import *

def check_python_syntax(code: str, file_name: str = "<generated>") -> tuple[bool, str]:
    try:
        compile(code, file_name, "exec")
        return True, ""
    except SyntaxError as e:
        error_message = (
            f"SyntaxError in {file_name}\n"
            f"Line {e.lineno}, Column {e.offset}\n"
            f"Error: {e.msg}\n"
            f"Text: {e.text}"
        )
        return False, error_message

def repair_python_code(
    code: str,
    file_name: str,
    error_message: str,
    model: str = "qwen2.5-coder:7b",
) -> str:
    prompt = (
        CODE_REPAIR_PROMPT
        .replace("__file_name__", file_name)
        .replace("__error_message__", error_message)
        .replace("__code__", code)
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python code repair tool. "
                    "Return valid Python code only. "
                    "No markdown. No explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.0,
            "top_p": 0.7,
        },
    )

    raw_text = response["message"]["content"]
    return clean_raw_text(raw_text)


def run_main_file(
    folder_path: str,
    timeout: int = 5,
    headless: bool = True,
) -> tuple[bool, str]:
    """
    main.py를 실행해보고 에러를 수집한다.

    Returns
    -------
    tuple[bool, str]
        ok:
            True면 에러 없이 timeout까지 실행됨.
            False면 실행 중 에러 발생.
        output:
            stdout + stderr 내용.
    """

    main_path = os.path.join(folder_path, "main.py")

    if not os.path.exists(main_path):
        raise FileNotFoundError(f"main.py not found: {main_path}")

    env = os.environ.copy()

    if headless:
        # pygame 창 없이 테스트하기 위한 설정
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"

    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=folder_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        output = ""

        if result.stdout:
            output += "[STDOUT]\n" + result.stdout + "\n"

        if result.stderr:
            output += "[STDERR]\n" + result.stderr + "\n"

        if result.returncode == 0:
            return True, output

        return False, output

    except subprocess.TimeoutExpired as e:
        output = ""

        stdout = e.stdout
        stderr = e.stderr

        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        if stdout:
            output += "[STDOUT]\n" + stdout + "\n"

        if stderr:
            output += "[STDERR]\n" + stderr + "\n"

        return True, output + f"\n[INFO] main.py ran for {timeout} seconds without crashing."


def extract_error_file_from_traceback(error_output: str, folder_path: str) -> str | None:
    """
    traceback에서 generated project 내부의 마지막 .py 파일을 찾는다.
    보통 가장 아래쪽 파일이 실제 수정 대상일 가능성이 높다.
    """

    pattern = r'File "([^"]+\.py)"'
    matches = re.findall(pattern, error_output)

    if not matches:
        return None

    folder_abs = os.path.abspath(folder_path)

    candidate_files = []

    for path in matches:
        path_abs = os.path.abspath(path)

        if path_abs.startswith(folder_abs):
            candidate_files.append(path_abs)

    if not candidate_files:
        return None

    # traceback상 마지막 프로젝트 파일이 보통 문제 위치
    return candidate_files[-1]


def repair_runtime_error_file(
    function_plan: dict,
    project_files: dict[str, str],
    target_file_name: str,
    target_file_code: str,
    error_output: str,
    model: str = "qwen2.5-coder:7b",
) -> str:
    prompt = (
        RUNTIME_REPAIR_PROMPT
        .replace(
            "__function_plan__",
            json.dumps(function_plan, indent=2, ensure_ascii=False),
        )
        .replace("__target_file_name__", target_file_name)
        .replace("__target_file_code__", target_file_code)
        .replace("__error_output__", error_output)
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python code repair tool. "
                    "Return valid Python code only. "
                    "No markdown. No explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.0,
            "top_p": 0.7,
        },
    )

    return clean_raw_text(response["message"]["content"])


def strong_change_runtime_error_file(
    function_plan: dict,
    project_files: dict[str, str],
    target_file_name: str,
    target_file_code: str,
    error_output: str,
    model: str = "qwen2.5-coder:7b",
) -> str:
    """
    Runtime 에러가 반복되거나 LLM이 같은 코드를 계속 반환할 때 사용하는
    강한 수정 함수.

    Parameters
    ----------
    function_plan:
        analyze_required_functions()로 만든 함수 설계 dict.
    project_files:
        {"main.py": "...", "globals.py": "..."} 형태의 전체 프로젝트 파일 코드.
    target_file_name:
        수정할 파일 이름. 예: "main.py", "update_player.py"
    target_file_code:
        수정할 대상 파일의 현재 코드.
    error_output:
        main.py 실행 결과 나온 traceback / stderr.
    model:
        Ollama model name.

    Returns
    -------
    str
        수정된 전체 Python 파일 코드.
    """

    shortened_project_file_list = list(project_files.keys())

    prompt = (
        STRONG_RUNTIME_REPAIR_PROMPT
        .replace(
            "__function_plan__",
            json.dumps(function_plan, indent=2, ensure_ascii=False),
        )
        .replace(
            "__project_file_list__",
            json.dumps(shortened_project_file_list, indent=2, ensure_ascii=False),
        )
        .replace("__target_file_name__", target_file_name)
        .replace("__target_file_code__", target_file_code)
        .replace("__error_output__", error_output)
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict Python/Pygame code repair tool. "
                    "Return only raw Python code. "
                    "No markdown. No explanations. "
                    "You must make a real change."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        options={
            "temperature": 0.3,
            "top_p": 0.9,
        },
    )

    repaired_code = clean_raw_text(
        response["message"]["content"]
    )

    return repaired_code