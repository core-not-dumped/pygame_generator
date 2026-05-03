# Pygame Code Generation Agent

This project is an experimental AI agent that automatically generates simple Pygame games.

The agent uses a local LLM through Ollama to generate game ideas, select the best candidate, create a detailed game specification, plan the required functions, generate Python source files, validate the code, repair errors, and run the final game in a headless test environment.

## Workflow

1. Generate multiple Pygame game ideas.
2. Score each idea based on simplicity, playability, originality, and implementation difficulty.
3. Select the best game candidate.
4. Generate a detailed game specification.
5. Analyze the game specification and create a function plan.
6. Generate shared global constants and data structures.
7. Generate individual Python files for each planned function.
8. Generate `main.py` to combine all generated functions.
9. Save the generated files into a game-specific folder.
10. Run `main.py` with `subprocess` in headless Pygame mode.
11. Treat timeout as success if the game keeps running without crashing.
12. Repair runtime errors using traceback output.

## Main Features

- Local LLM-based code generation with Ollama
- Automatic Pygame game idea generation
- Function planning and file generation
- Multi-file project generation
- Syntax validation
- Runtime testing with subprocess
- Headless Pygame testing
- Automatic error repair
- Infinite repair loop detection
- Single-file fallback generation

## Requirements

- Python 3.10+
- Pygame
- Ollama
- qwen2.5-coder or another code-generation model

## Example Model

```bash
ollama pull qwen2.5-coder:7b