# Development Guidelines

## Core Philosophy
This codebase prioritizes **Stability**, **Readability**, and **Testability**. All changes must be verified against these standards.

## Architecture
- **Entity Component System (Lite):** Entities should separate Logic (Input/Physics) from Presentation (Drawing/Sounds).
- **State Management:** The game uses a strict State Machine (`src/main.py`). Do not handle game states (GameOver, Menu) inside Level logic.
- **Delta Time:** All movement and physics calculations must use `dt` (Delta Time) to ensure frame-rate independence.

## Coding Standards
1.  **Imports:**
    - Standard Library first (e.g., `math`, `random`).
    - Third Party second (e.g., `pygame`).
    - Local Application third.
    - **Never** assume a library function exists (e.g., `pygame.math.atan2` does not exist; use `math.atan2`).
2.  **Variables:**
    - Use `snake_case` for variables and functions.
    - Use `CAPITAL_CASE` for constants (`src/settings.py`).
3.  **Type Hints:** Use Python type hints for function arguments where complex types are involved.

## Verification Protocols
Before submitting ANY code, you must perform the following:

1.  **Static Analysis:** logic check for undefined variables or missing imports.
2.  **Unit Tests:** Run `python3 -m unittest discover tests` to verify core logic (Physics, Math, Shop).
3.  **Headless Runtime Test:** If you touch the Game Loop or Rendering, run a headless simulation (see `tests/test_headless.py`) to ensure no runtime crashes occur during state transitions.
4.  **Math Check:** Verify all vector math. Pygame Vectors are convenient but check if standard `math` is needed for trigonometry.

## Common Pitfalls
- **Input in Update Loops:** Do not instantiate new Joystick objects in `update()`. initialize them once in `main.py` and pass them down.
- **Float vs Int:** Pygame `Rect`s are integers. Use `pygame.math.Vector2` for position (float) and sync to `Rect` (int) only for rendering/collision.
