# AGENT Guidelines for `automite`

These instructions apply to the entire repository rooted at `C:\Developer\automite`.

## Project Overview

- Primary language: Python (desktop automation / screen interaction).
- Entry point: `main.py` (PyQt overlay and global hotkeys).
- Supporting automation script: `src/click.py` (OpenCV-based clicking).
- Documentation lives in `docs/` (see `docs/tasks.md` for modernization roadmap).
- Virtual environment lives in `.venv/` and should be treated as opaque.

## Directories and File Conventions

- `main.py`: Keep as the primary executable entry point. New application logic should go into modules under `src/` and be imported here, not implemented inline unless very small.
- `src/`: Place reusable Python modules and automation helpers here. Prefer small, focused modules over very large files.
- `assets/`: Image assets used for template matching and UI. Do not rename, move, or re-encode assets unless the change is clearly required and all references are updated.
- `docs/`: Add or update documentation when user-visible behavior or workflows change.
- Do not modify `.venv/` or `.idea/` content; treat them as environment/editor artifacts.

## Coding Style (Python)

- Follow standard Python style (PEP 8) and keep changes minimal and focused on the requested task.
- Prefer descriptive variable and function names; avoid single-letter names except for very local indices or coordinates.
- Use functions and small classes to keep logic testable and composable; avoid large monolithic blocks in `main.py`.
- Prefer `logging` for diagnostics and internal traces; reserve `print` for user-facing or debugging output that is explicitly desired.
- When changing or adding behavior, prefer refactoring existing code over duplicating logic.

## Behavior for Automated Agents

- Make the smallest change that fully addresses the request; avoid broad refactors or reformatting unrelated code.
- Preserve existing behavior unless a change is explicitly requested or clearly fixes a bug.
- When introducing new dependencies, prefer standard library first; avoid adding heavy third-party libraries without clear justification.
- Do not add or modify license headers unless explicitly requested.
- Avoid editing binary/image assets directly; if new assets are required, document the expected filename, format, and purpose in `docs/` rather than generating them.

## Testing and Running

- Assume the project is run directly via `python main.py` from the repository root.
- If you add non-trivial logic, consider structuring it so that it can be imported and unit-tested from under `src/` even if a test suite does not yet exist.
- Do not introduce new test frameworks or CI configuration without an explicit request; instead, align with any future decisions recorded in `docs/tasks.md`.

## Documentation Expectations

- When you change user-visible behavior, update or create documentation under `docs/` (or docstrings) to reflect the new behavior.
- Keep documentation concise and task-focused, mirroring the style in `docs/tasks.md`.

## Safety & Environment

- Assume Python 3.x and a local desktop environment with PyQt5, OpenCV, and numpy available (often via a virtual environment), but keep code portable across Windows, macOS, and Linux where feasible.
- Treat this as desktop automation: default to conservative behavior and avoid adding code that clicks or types outside the intended game/target context unless explicitly requested.
- Do not add background services, remote control features, or network calls without an explicit user request.

## UX Invariants

- Preserve the core overlay behavior: it should dim the background, show instructions, and allow quitting via `ESC` and `Q` unless the user explicitly asks to change that.
- Keep user-facing text simple and informative; avoid noisy pop-ups or intrusive dialogs.
- Keep logging informative but avoid overly verbose logging in tight loops or high-frequency events, especially in screen-capture or click routines.

## Refactoring, Dependencies, and Configuration

- Refactor only within the scope of the current task; avoid large structural changes, global renames, or moving many files unless explicitly requested.
- Prefer reusing existing dependencies (PyQt5, OpenCV, numpy, pynput, pyautogui) and the Python standard library before introducing new third-party libraries.
- Keep paths, thresholds, and similar “magic numbers” as module-level constants rather than scattering literals; if you introduce new configuration, group it clearly and document any user-facing effects.
