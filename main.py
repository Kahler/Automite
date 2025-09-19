import platform, subprocess, time, sys
import pywinctl as pwc
import pyautogui as pag

# Optional OpenCV-based image click
try:
    import cv2, numpy as np, mss
    HAS_CV = True
except Exception:
    HAS_CV = False

pag.FAILSAFE = True   # move mouse to top-left to abort
pag.PAUSE = 0.05      # tiny delay between actions

def launch_editor():
    system = platform.system()
    if system == "Windows":
        return subprocess.Popen(["notepad.exe"])
    elif system == "Darwin":
        return subprocess.Popen(["open", "-a", "TextEdit"])
    else:
        # Try a few common editors on Linux
        for cmd in (["gedit"], ["xed"], ["kate"], ["mousepad"]):
            try:
                return subprocess.Popen(cmd)
            except FileNotFoundError:
                continue
        raise RuntimeError("No GUI editor found. Install gedit/xed/kate/mousepad.")

def wait_for_window(title_substrings, timeout=15, app_hint: str | None = None):
    """Wait for any window whose title contains provided substrings."""
    system = platform.system()
    deadline = time.time() + timeout
    extra_titles: list[str] = []
    while time.time() < deadline:
        search_titles = list(title_substrings) + extra_titles
        if system == "Darwin" and app_hint:
            fallback_titles = _macos_window_titles(app_hint)
            new_titles = [t for t in fallback_titles if t and t not in search_titles]
            if new_titles:
                search_titles.extend(new_titles)
                extra_titles.extend([t for t in new_titles if t not in extra_titles])
        for t in search_titles:
            wins = find_windows_with_title(t, case_sensitive=False)
            if wins:
                w = wins[0]
                if not w.isVisible:  # pywinctl tracks visibility
                    try:
                        w.restore()
                    except Exception:
                        pass
                try:
                    w.activate()
                except Exception:
                    pass
                return w
        time.sleep(0.2)
    raise TimeoutError(f"Window not found for titles: {title_substrings}")

def find_windows_with_title(title: str, case_sensitive: bool = False) -> list:
    """Return window handles whose titles contain the requested substring."""
    try:
        windows = list(pwc.getWindowsWithTitle(title, caseSensitive=case_sensitive))
    except TypeError:
        windows = list(pwc.getWindowsWithTitle(title))
    except AttributeError:
        windows = []

    if not windows:
        target = title if case_sensitive else title.lower()
        for window in pwc.getAllWindows():
            window_title = window.title or ""
            comparable = window_title if case_sensitive else window_title.lower()
            if target in comparable:
                windows.append(window)
    return windows


def get_matching_window_titles(
    title: str,
    case_sensitive: bool = False,
    app_name: str | None = None,
) -> list[str]:
    """Return unique window titles matching the requested substring."""
    windows = find_windows_with_title(title, case_sensitive=case_sensitive)
    titles = sorted({w.title for w in windows if getattr(w, "title", None)})
    if titles:
        return titles

    if platform.system() == "Darwin":
        candidate = app_name or title
        fallback_titles = _macos_window_titles(candidate)
        if fallback_titles:
            return sorted({t for t in fallback_titles if t})

    return []


def _macos_window_titles(app_name: str) -> list[str]:
    """Collect window titles for a macOS application via AppleScript."""
    escaped_name = app_name.replace('"', '\"')
    script = f"""
    set targetName to "{escaped_name}"
    tell application "System Events"
        set appTitles to {{}}
        repeat with proc in (application processes whose name contains targetName)
            repeat with w in windows of proc
                try
                    set end of appTitles to (name of w as text)
                end try
            end repeat
        end repeat
        return appTitles
    end tell
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"AppleScript lookup failed for {app_name!r}:", exc, file=sys.stderr)
        return []

    output = result.stdout.strip()
    if not output:
        return []

    normalised = output.replace("\r", "\n")
    return [line.strip() for line in normalised.split("\n") if line.strip()]



def is_window_open(title: str, case_sensitive: bool = False) -> bool:
    """Return True when a window containing the title substring is visible."""
    return bool(get_matching_window_titles(title, case_sensitive=case_sensitive, app_name=title))

def click_image_on_screen(template_path, confidence=0.92):
    if not HAS_CV:
        raise RuntimeError("OpenCV/mss not installed. `pip install opencv-python mss`")
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[0]))[:, :, :3]  # drop alpha
    template = cv2.imread(template_path)
    if template is None:
        raise FileNotFoundError(template_path)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < confidence:
        raise RuntimeError(f"Template not found (score={max_val:.3f} < {confidence})")
    th, tw = template.shape[:2]
    center = (max_loc[0] + tw // 2, max_loc[1] + th // 2)
    pag.moveTo(center[0], center[1], duration=0.1)
    pag.click()
    return max_val

def main():
    pycharm_titles = get_matching_window_titles("PyCharm", app_name="PyCharm")
    if pycharm_titles:
        print("PyCharm window detected:", pycharm_titles)
    else:
        print("No PyCharm window detected.")

    proc = launch_editor()
    system = platform.system()
    titles = {
        "Windows": ["Notepad"],
        "Darwin": ["TextEdit"],
        "Linux":  ["gedit", "Text Editor", "Kate", "Mousepad"],
    }.get(system, [""])
    app_hint = "TextEdit" if system == "Darwin" else None
    try:
        w = wait_for_window(titles, app_hint=app_hint)
    except TimeoutError as exc:
        print(f"Window not found for titles {titles}: {exc}", file=sys.stderr)
        return

    # Position and size
    try:
        w.moveTo(100, 100)
        w.resizeTo(1000, 700)
        w.activate()
    except Exception as e:
        print("Window move/resize failed:", e, file=sys.stderr)

    time.sleep(0.3)
    pag.typewrite("Hello from cross-platform Python automation! 🚀", interval=0.02)
    pag.hotkey("ctrl", "s") if system == "Windows" else pag.hotkey("command", "s")

    # Optional: click a toolbar button by image (put a PNG next to the script)
    # try:
    #     score = click_image_on_screen("bold_button.png", confidence=0.9)
    #     print("Clicked image match with score:", score)
    # except Exception as e:
    #     print("Image click skipped:", e)

    # Keep the editor open for a bit
    time.sleep(1)

if __name__ == "__main__":
    main()
