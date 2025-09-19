# Repository Guidelines

## Project Structure & Module Organization
Automite currently centers on `main.py`, which orchestrates cross-platform desktop automation. Keep supporting assets (e.g., toolbar screenshots for image matching) inside an `assets/` folder at the repository root and reference them by relative path. Place future modules under `automite/` and mirror that structure under `tests/` to keep automation helpers and their coverage aligned.

## Build, Test, and Development Commands
Use Python 3.10+. Create a virtual environment with `python3 -m venv .venv` and activate it (`source .venv/bin/activate` on macOS/Linux, `.venv\\Scripts\\activate` on Windows). Install runtime dependencies via `pip install pyautogui pywinctl mss opencv-python numpy`. Run the automation locally with `python3 main.py`. When adding developer tools, capture them in `requirements-dev.txt` and document any OS-level packages the automation expects.

## Coding Style & Naming Conventions
Follow PEP 8 for Python formatting, with black-compatible 88-character lines and 4-space indentation. Use descriptive snake_case for functions and lower_snake_case module names; reserve CapWords for classes. Prefer type hints on public call surfaces, and keep platform-specific logic behind helper functions such as `launch_editor()` to preserve clarity. Run `ruff check .` or `black .` before submitting if available in your toolchain.

## Testing Guidelines
Adopt `pytest` for new tests. Store them in `tests/test_<feature>.py`, mirroring module names. When feasible, isolate GUI-dependent routines behind adapters so they can be mocked in unit tests. For full-stack automation flows, add smoke scripts under `scripts/` that can be triggered manually. Target at least a smoke test per supported platform and document any skipped cases.

## Commit & Pull Request Guidelines
Write Conventional Commit messages (`feat:`, `fix:`, `chore:`) summarizing the user-facing impact. Each pull request should describe the motivation, list covered platforms, and note how the automation was validated (e.g., “Validated on macOS Sonoma”). Include screenshots or screen recordings when UI automation changes cursor paths or window assumptions. Link to related issues and call out follow-up work in a checklist.

## Automation Agent Notes
This project requires an interactive desktop session—do not run in headless CI without a virtual display. Keep `pag.FAILSAFE` enabled and mention any intentional overrides. Before merging, confirm that window titles referenced in `wait_for_window()` are still accurate for the target platform.
