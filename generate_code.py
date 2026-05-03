import json
from ollama import chat
import os

from utils import *
from prompts import *
from repair import *
from idea import *
from generate_func import *

def calculate_score(candidate: dict) -> float:
    return (
        + candidate["prototype_clarity"] * 0.40
        + candidate["market_fit"] * 0.25
        + candidate["visual_simplicity"] * 0.35
    )


def select_best_candidate(candidates: list[dict]) -> dict:
    scored = []

    for candidate in candidates:
        total_score = calculate_score(candidate)
        scored.append(total_score)

    best_idx = scored.index(max(scored))
    return candidates[best_idx]


def generate_detailed_game_spec(selected_candidate: dict, model: str = "qwen2.5-coder:7b") -> dict:
    selected_candidate_json = json.dumps(
        selected_candidate,
        ensure_ascii=False,
        indent=2,
    )

    prompt = BUILDUP_PROMPT.replace(
        "__SELECTED_CANDIDATE_JSON__",
        selected_candidate_json
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON game design spec generator. Return valid JSON only.",
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

    raw_text = response["message"]["content"]
    clean_text = clean_raw_text(raw_text)

    try:
        spec = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON:\n{raw_text}") from e

    return spec


if __name__ == "__main__":
    
    # get best candidate
    ideas = generate_game_ideas() # list[dict]
    for idea in ideas:  print(idea["title"], calculate_score(idea))
    best_candidate = select_best_candidate(ideas) # dict
    best_candidate = generate_detailed_game_spec(best_candidate) # dict
    game_title = re.sub(r'[\\/:*?"<>|]', "", best_candidate["title"])
    game_dir = f'./generated_games/{game_title}'
    os.mkdir(game_dir)
    save_json_dict(best_candidate, game_dir + '/best_candidate.json')
    best_candidate = json.dumps(best_candidate, indent=2, ensure_ascii=False)
    print('best candidate process finished !')
    # print("Best candidate:")
    # print(best_candidate)

    # get detail about game
    best_candidate = generate_detailed_game_spec(best_candidate)
    function_plan = analyze_required_functions(best_candidate) # dict
    save_json_dict(function_plan, game_dir + '/function_plan.json')
    for func in function_plan["functions"]: print(func["name"]) # print function names
    print('function plan process finished !')
    # print("Function plan:")
    # print(function_plan)

    # generate globals
    globals_code = generate_globals_code(function_plan)
    save_py_file(globals_code, game_dir + '/globals.py')

    # generate functions
    for func in function_plan["functions"]:
        func_name = func["name"]
        if func_name == 'main':  continue
        func_code = generate_single_function_file_code(function_plan, func)
        for trial in range(repair_attempts):
            ok, error = check_python_syntax(func_code)
            if ok:  break
            print(f'repair {func_name} {trial+1}/{repair_attempts}')
            func_code = repair_python_code(func_code, f'{func_name}.py', error)
        save_py_file(func_code, game_dir + f'/{func_name}.py')
        print(f"{func_name} generated !")

    # generate main function
    main_code = generate_main_code(best_candidate, function_plan)
    for trial in range(repair_attempts):
        ok, error = check_python_syntax(main_code)
        if ok: break
        print(f'repair main {trial+1}/{repair_attempts}')
        main_code = repair_python_code(main_code, f'main.py', error)
    save_py_file(main_code, game_dir + f'/main.py')
    print("main function generated !")

    loop_num = 0
    errors = []
    before_error_file_name = ""
    while True:
        ok, error = run_main_file(game_dir)
        if ok:
            print('no error exit generate code..')
            break
        loop_num += 1
        error_file_name = extract_error_file_from_traceback(error, game_dir)
        error_file_name = os.path.basename(error_file_name)
        if error_file_name != before_error_file_name:   errors = [error]
        else:                                           errors.append(error)
        error_message = ""
        for i, item in enumerate(errors, start=1):   error_message += f"trial {i}: {item}"
        file_code_dict = read_project_py_files(game_dir)
        
        if len(errors) >= 3:
            repaired_code = strong_change_runtime_error_file(
                function_plan,
                file_code_dict,
                error_file_name,
                file_code_dict[error_file_name],
                error_message
            )
            errors = [errors[-1]]
        else:
            repaired_code = repair_runtime_error_file(
                function_plan,
                file_code_dict,
                error_file_name,
                file_code_dict[error_file_name],
                error_message
            )
        save_py_file(repaired_code, game_dir + f'/{error_file_name}')
        print(error_message)
        print(error_file_name)
        print(f'{loop_num} times loop..')

        before_error_file_name = error_file_name