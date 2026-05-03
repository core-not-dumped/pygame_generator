IDEATION_PROMPT = """
You are an AI game ideation agent for rapid mobile hyper-casual game prototyping.

Your task is to generate 5 simple game concept candidates for a 2D Pygame prototype.

The concepts must be:
- Simple enough to implement in Pygame within a few files
- Easy to represent with simple procedural 2D assets
- Designed around clear mechanics such as collect, avoid, dodge, survive, shoot, chase, or timing
- Not dependent on complex physics, networking, multiplayer, 3D graphics, copyrighted characters, or external image assets
- Prefer high prototype_clarity and visual_simplicity
- Avoid vague concepts
- Avoid large RPG, strategy, simulation, puzzle systems, or story-heavy games
- Prefer ideas with implementation_difficulty >= 3

User direction:
__user_direction__

Return ONLY a valid JSON array.
Do not include markdown.
Do not include explanations outside the JSON.
Do not wrap the JSON in ```.

Each item must have exactly these fields:
- title: string, short English title
- genre: string, one of "collect_and_avoid", "runner", "survival", "shooter", "timing", "chase", etc.
- concept: string, one sentence
- core_loop: string, concise loop using arrows, e.g. "move → collect → avoid → score up → difficulty increases"
- why_fun: string, one sentence explaining the appeal
- implementation_difficulty: integer from 1 to 5, where 5 is easiest
- prototype_clarity: integer from 1 to 5, where 5 means the core idea is visually and mechanically clear
- market_fit: integer from 1 to 5, where 5 means strong hyper-casual fit
- visual_simplicity: integer from 1 to 5, where 5 means easy to draw using simple shapes
"""


BUILDUP_PROMPT = """
You are a senior game designer and technical planner for rapid 2D Pygame prototyping.

Your task is to expand the selected game candidate into a detailed implementation-ready game design spec.

Selected candidate JSON:
__SELECTED_CANDIDATE_JSON__

Create a detailed game design spec that can be directly used by a Python/Pygame code generation agent.

Strict rules:
- Return ONLY valid JSON.
- Do not include markdown.
- Do not wrap the output in ```json.
- Do not include explanations outside the JSON.
- Keep the game simple enough for a single-file Pygame prototype.
- Do not require external image files, audio files, fonts, APIs, networking, or 3D graphics.
- Use only simple shapes for visuals.
- Avoid copyrighted or trademarked names, characters, brands, and franchises.
- Make all mechanics concrete and implementable.

The output JSON must have exactly this structure:
{
  "title": "string",
  "genre": "string",
  "one_sentence_pitch": "string",
  "screen": {
    "width": 800,
    "height": 600,
    "fps": 60
  },
  "controls": {
    "left": "string",
    "right": "string",
    "up": "string",
    "down": "string",
    "action": "string",
    "restart": "string"
  },
  "player": {
    "name": "string",
    "shape": "rect|circle",
    "color": [0, 0, 0],
    "size": [width, height],
    "start_position": [x, y],
    "movement": "string",
    "speed": 0,
  },
  "optional_mechanics": {
    "uses_gravity": false,
    "gravity": null,
    "uses_jump": false,
    "jump_power": null,
    "can_double_jump": false,
    "uses_projectiles": false,
    "projectile_speed": null
  },
  "objects": [
    {
      "name": "string",
      "role": "platform|hazard|collectible|enemy|projectile",
      "shape": "rect|circle",
      "color": [0, 0, 0],
      "size": [width, height],
      "spawn_rule": "string",
      "movement_rule": "string",
      "collision_effect": "string"
    }
  ],
  "rules": [
    "concrete gameplay rule"
  ],
  "scoring": {
    "score_type": "survival_time|collectibles|kills|distance",
    "score_rule": "string"
  },
  "difficulty_scaling": {
    "rule": "string",
    "interval_seconds": 0
  },
  "game_states": {
    "start": "string",
    "playing": "string",
    "game_over": "string"
  },
  "win_condition": "string",
  "lose_condition": "string",
  "implementation_notes": [
    "specific technical instruction"
  ]
}

Important implementation requirements:
- The spec must make it obvious what classes or data structures are needed.
- The spec must specify how objects spawn, move, collide, and reset.
- The spec must specify how score changes.
- The spec must specify how the game restarts after game over.
- If the candidate mentions jumping or platforms, include gravity, velocity_y, platform collision, and falling death.
- If the candidate mentions falling rocks, include rock spawn positions, falling speed, respawn behavior, and collision damage.
- If the game is survival, score should usually be survival time in seconds.
"""


CODE_REVIEW_FIX_PROMPT = """
You are an expert Python Pygame code reviewer and fixer.

Review the given Pygame code and return an improved complete version.

Selected game concept JSON:
{selected_candidate_json}

Current code:
{current_code}

Review checklist:
- The code must define screen using pygame.display.set_mode.
- The code must have a working game loop.
- The code must handle pygame.QUIT.
- The code must draw all objects.
- The code must update objects every frame.
- The code must use pygame.Rect or colliderect for collision detection.
- The code must display score or survival time.
- The code must have a game-over state.
- The code must allow restart after game over.
- Objects that leave the screen must respawn or be removed safely.
- Do not remove items from a list while directly iterating over it.
- If a function modifies global variables, it must declare them with global.
- Do not use external image files, audio files, APIs, or assets.
- Do not leave TODO comments or incomplete functions.

Strict output rules:
- Return ONLY complete Python code.
- Do not include markdown.
- Do not wrap the code in ```python.
- Do not include explanations.
"""


FUNCTION_ANALYSIS_PROMPT = """
You are a senior Python/Pygame software architect.

Your task is to analyze the given game specification and design the functions needed to implement the game in Pygame.

Do NOT write full code.
Do NOT implement the game yet.
Only return a valid JSON object.

The output JSON must describe:
- required functions
- purpose of each function
- parameters
- return values
- dependencies between functions
- implementation order
- whether the function handles initialization, input, update, rendering, collision, state, UI, or utility logic

The game should be implemented as a single Python file using pygame.

Important rules:
1. Use clear snake_case function names.
2. Avoid too many tiny functions.
3. Prefer reusable functions.
4. Do not include main function.
5. Do not include main loop in implementation order.
5. Include functions for:
   - pygame initialization
   - asset/color/font setup
   - game state initialization
   - event handling
   - player update
   - object/enemy update if needed
   - collision detection
   - score/life/win/lose handling
   - drawing/rendering
   - restart/game over handling
7. Return JSON only. No markdown. No explanation.

Game specification:
__game_spec__

Return format:

{
  "project_title": "string",
  "architecture_summary": "string",
  "global_constants": [
    {
      "name": "string",
      "type": "string",
      "purpose": "string",
      "example_value": "string | number | boolean | array | object"
    }
  ],
  "data_structures": [
    {
      "name": "string",
      "type": "dict | list | pygame.Rect | class | tuple | other",
      "purpose": "string",
      "fields": [
        {
          "name": "string",
          "type": "string",
          "purpose": "string"
        }
      ]
    }
  ],
  "functions": [
    {
      "name": "string",
      "category": "initialization | input | update | rendering | collision | state | ui | utility",
      "purpose": "string",
      "parameters": [
        {
          "name": "string",
          "type": "string",
          "purpose": "string",
          "default": "optional string"
        }
      ],
      "returns": {
        "type": "string",
        "description": "string"
      },
      "uses": ["function_name"],
      "called_by": ["function_name"],
      "implementation_notes": [
        "string"
      ],
      "order": 1
    }
  ],
}
"""

GLOBALS_CODE_PROMPT = """
You are an expert Python/Pygame code generator.

Your task is to generate a single Python file named globals.py.

This globals.py file will be used by other generated pygame source files.

You must use the provided function plan, especially:
- global_constants
- data_structures

Generate clean, valid Python code only.

Rules:
1. Return Python code only.
2. Do not use markdown.
3. Do not wrap the code in ```python.
4. Do not include explanations.
5. Define global constants from global_constants.
6. Define useful default constants if they are missing, such as:
   - SCREEN_WIDTH
   - SCREEN_HEIGHT
   - SCREEN_SIZE
   - FPS
   - common colors (BLACK, WHITE, RED, GREEN, BLUE, YELLOW etc.)
7. For data_structures, create comments or lightweight helper factory functions if useful.
8. Do not create classes unless the function_plan explicitly requires them.
9. The code must be importable without running pygame.init().
10. Avoid side effects.
11. Do not create the main game loop here.
12. Make the file beginner-friendly and readable.

Function plan JSON:
__function_plan__
"""


SINGLE_FUNCTION_FILE_PROMPT = """
You are an expert Python/Pygame code generator.

Your task is to generate one complete Python file that contains exactly one target function.

You will receive:
1. Global constants from function_plan["global_constants"]
2. Data structures from function_plan["data_structures"]
3. One target function specification

Important rules:
1. Write the entire Python file content.
2. The file must contain exactly one main target function.
3. The target function name must be exactly: "__function_name__"
4. If you use any global constants or data structures from the function plan, you MUST import them using:
   from globals import *
5. Do not define unrelated functions.
6. Do not call the target function at the bottom of the file.
7. Do not include if __name__ == "__main__": unless the target function is main and the function spec explicitly requires it.
8. Return Python code only.
9. Do not use markdown.
10. Do not wrap the code in ```python.
11. Do not include explanations.
12. The code must be syntactically valid Python.
13. Use type hints when reasonable.
14. Include imports needed by this function.
15. Avoid side effects at import time.
16. If this function depends on other "planned functions", import them from their own files.
    Example:
    from update_player import update_player
17. Assume every planned function is saved in a file with the same name as the function.
    Example:
    function name: handle_events
    file name: handle_events.py
    import style: from handle_events import handle_events
18. Do not redefine functions that are listed in "uses". Import and call them instead.

Global constants:
__global_constants__

Data structures:
__data_structures__

Target function specification:
__function_spec__

All planned function names:
__all_function_names__

Generate the complete Python file now.
"""


MAIN_CODE_PROMPT = """
You are an expert Python/Pygame code generator.

Your task is to generate one complete Python file named main.py.

This main.py file must combine all previously generated function files into a runnable pygame game.

You will receive:
1. The detailed game specification
2. The function plan

Important rules:
1. Return Python code only.
2. Do not use markdown.
3. Do not wrap the code in ```python.
4. Do not include explanations.
5. Write the entire main.py file content.
6. main.py should import global constants using:
   from globals import *
7. main.py should import planned functions from their own files.
   Example:
   from init_pygame import init_pygame
   from handle_events import handle_events
8. Assume every planned function is saved in a file with the same name as the function.
   Example:
   function name: update_player
   file name: update_player.py
9. Do not redefine planned functions inside main.py.
10. main.py must define a function named exactly main.
11. main.py must include:
    if __name__ == "__main__":
        main()
12. The main function should follow function_plan["main_loop_flow"].
13. The main function should use function_plan["implementation_order"] where appropriate.
14. Do not import main from main.py.
15. If function_plan already includes a planned function named "main", do not import it. Implement main directly in this file.
16. The code must be syntactically valid Python.
17. The code should be beginner-friendly and readable.
18. Avoid side effects except running main under if __name__ == "__main__".
19. Make the final pygame program runnable as much as possible.
20. If there is ambiguity, make reasonable assumptions and keep the code simple.
21. Use pygame.quit() safely when the game exits.
22. Do not use external assets unless the game specification explicitly requires them.
23. If another function returns multiple values, unpack them reasonably based on its return description.
24. If another function mutates game_state in place, call it without expecting a return value.
25. If event handling function returns a boolean running flag, use it to control the loop.
26. If update or draw functions require common objects such as screen, clock, fonts, or game_state, pass them according to their function specification.

Detailed game specification JSON:
__best_candidate__

Function plan JSON:
__function_plan__

Generate the complete main.py file now.
"""


CODE_REPAIR_PROMPT = """
You are an expert Python/Pygame code repair assistant.

Your task is to fix the given Python file.

Rules:
1. Return the full corrected Python file.
2. Return Python code only.
3. Do not use markdown.
4. Do not wrap the code in ```python.
5. Do not include explanations.
6. Preserve the original intended behavior as much as possible.
7. Fix all syntax errors.
8. Fix missing imports if obvious.
9. Do not remove the target function unless necessary.
10. Do not add a pygame main loop unless this is main.py.
11. If this file uses global constants, use:
   from globals import *
12. The corrected code must be syntactically valid Python.

File name:
__file_name__

Error message:
__error_message__

Original code:
__code__

Return the corrected full Python file now.
"""


RUNTIME_REPAIR_PROMPT = """
You are an expert Python/Pygame runtime error repair assistant.

Your task is to fix one Python file from a generated multi-file pygame project.

The project structure is:
- globals.py contains global constants and shared simple data structures.
- each function is stored in its own .py file.
- main.py imports and combines all functions.
- do not merge files into one file.

Rules:
1. Return the full corrected content of the target file only.
2. Return Python code only (strict).
3. Do not use markdown.
4. Do not wrap the code in ```python.
5. Do not include explanations.
6. Fix the runtime error shown below.
7. Preserve the existing architecture.
8. Do not rename the target function.
9. If an error occurs because of an import, you may remove the import statement.
10. If constants are needed, use:
   from globals import *
11. If another function is needed, import it from its own file.
12. The corrected code must be valid Python.

Function plan JSON:
__function_plan__

Project files:
__project_files__

Target file name:
__target_file_name__

Target file code:
__target_file_code__

Runtime error output:
__error_output__

Return the corrected full target file now.
"""

STRONG_RUNTIME_REPAIR_PROMPT = """
You are an expert Python/Pygame runtime error repair assistant.

The previous repair attempt failed or returned the same code.
You MUST make a real change to fix the error.

Your task is to fix ONE target Python file from a generated pygame project.

Important:
- The project may be messy.
- Imports may be wrong.
- Function signatures may not match.
- Local modules may be broken.
- The current code may need simplification.

Rules:
1. Return only raw Python code.
2. Do not include markdown, explanations, or any text outside the code.
3. Return the full corrected content of the target file.
4. Do not return the same code.
5. Fix the runtime error shown below.
6. The corrected code must be syntactically valid Python.
7. If an import statement causes an error and the imported module is not required, remove that import statement.
8. If a local import is broken, either fix the import or inline the needed logic into this file.
9. If a function call has wrong arguments, change the call to match the actual function signature.
10. If a variable is undefined, define it, import it, or replace it with the correct existing variable.
11. If an asset file is missing, replace it with pygame shapes, colors, or default fonts.
12. If the current structure is too broken, prefer the simplest working solution.
13. Keep the target file runnable/importable.
14. If the target file is main.py, you may discard the multi-file structure and rewrite everything as one self-contained runnable main.py file without importing any local project files.
15. If the target file is not main.py, do not add if __name__ == "__main__": unless it already existed.
16. Do not leave unresolved references.
17. Do not leave TODO comments.
18. Do not use placeholder code.

Function plan JSON:
__function_plan__

Target file name:
__target_file_name__

Previous target file code:
__target_file_code__

Runtime error output:
__error_output__

Return the corrected full target file now.
"""