import cv2
import numpy as np
from PyQt5.QtGui import QGuiApplication
import time

# Path to the reference image (e.g. "button.png")
template_path = "../assets/Battle_button.png"  # Battle button image
retry_button_path = "../assets/Retry_button.png" # Retry button image
upgrade_bar_path = "../assets/upgrade_bar.png" # Upgrade bar image
gem_claim_path = "../assets/gem_claim.png" # gem claim image
floating_gem_path = "../assets/floating_gem.png.png" # floating gem image

# This should probably be found some other way.
health_hack_path = "../assets/health_hack_path.png" # health hack image

# Load the template
template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
if template is None:
    raise FileNotFoundError(f"Template image not found at {template_path}")
w, h = template.shape[::-1]

# Initialize a minimal Qt application (no event loop needed for grabbing screen)
app = QGuiApplication.instance() or QGuiApplication([])

SCALES = [1.0, 0.9, 0.8, 1.1, 1.2]
YELLOW_MASTER_RGB = (41, 34, 44)

def capture_screen():
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        print("No primary screen available for screenshot")
        return None, None, None, None
    pixmap = screen.grabWindow(0)
    image = pixmap.toImage()
    image = image.convertToFormat(4)
    width = image.width()
    height = image.height()
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    screenshot = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return screenshot, bgr, width, height

def find_best_match(screenshot, template_img):
    th, tw = template_img.shape[:2]
    best_val = -1
    best_pt = None
    best_wh = None
    for scale in SCALES:
        try:
            if scale == 1.0:
                tpl = template_img
            else:
                new_w = max(1, int(tw * scale))
                new_h = max(1, int(th * scale))
                tpl = cv2.resize(
                    template_img,
                    (new_w, new_h),
                    interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC,
                )
            res = cv2.matchTemplate(screenshot, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_val:
                best_val = max_val
                best_pt = max_loc
                best_wh = tpl.shape[::-1]
        except Exception:
            pass
    return best_val, best_pt, best_wh

def log_click_color(bgr, x, y, width, height):
    if 0 <= x < width and 0 <= y < height:
        b, g, r = bgr[y, x]
        rgb = (int(r), int(g), int(b))
        print(f"Click target color (RGB): {rgb}")
        if rgb == YELLOW_MASTER_RGB:
            print("IT'S YELLOW MASTER!")

def click_at(center_x, center_y):
    try:
        from PyQt5.QtGui import QCursor
        from PyQt5.QtCore import QPoint
        old_pos = QCursor.pos()
        QCursor.setPos(QPoint(center_x, center_y))
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetCursorPos(center_x, center_y)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        QCursor.setPos(old_pos)
        user32.SetCursorPos(old_pos.x(), old_pos.y())
    except Exception:
        try:
            import pyautogui
            old_pos = pyautogui.position()
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.click()
            pyautogui.moveTo(old_pos.x, old_pos.y, duration=0)
        except Exception as e:
            print(f"Failed to click: {e}")

def find_and_click(template_img, threshold=0.7):
    global w, h
    # Re-capture screen each call
    screenshot, bgr, width, height = capture_screen()
    if screenshot is None:
        return False
    best_val, best_pt, best_wh = find_best_match(screenshot, template_img)

    if best_val >= threshold and best_pt is not None and best_wh is not None:
        x, y = best_pt
        tw2, th2 = best_wh
        center_x = int(x + tw2 / 2)
        center_y = int(y + th2 / 2)
        print(f"Found at ({center_x}, {center_y}) with score {best_val:.3f}")
        log_click_color(bgr, center_x, center_y, width, height)
        click_at(center_x, center_y)
        return True
    else:
        print(f"No match found. Best score: {best_val:.3f}")
        return False

def local_imread(filename):
    read_file = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    if read_file is None:
        print(f"template not found at {filename}")
    return read_file

# Load templates
retry_template = local_imread(retry_button_path)
upgrade_bar_template = local_imread(upgrade_bar_path)
health_hack_template = local_imread(health_hack_path)
gem_claim_template = local_imread(gem_claim_path)

# Loop with a delay, looking for the retry button
try:
    while True:
        if retry_template is not None:
            print("Checking for Retry button...")
            found = find_and_click(retry_template, threshold=0.7)
            if found:
                time.sleep(2)
                print("Checking for upgrade bar button...")
                find_and_click(upgrade_bar_template, threshold=0.6)
                time.sleep(1)
                print("Clicked Retry, and upgrade bar button.")
        if health_hack_template is not None:
            print("Checking for running elements to click...")
            find_and_click(health_hack_template, threshold=0.7)
            time.sleep(0.1)
            # check for gem claim
            find_and_click(gem_claim_template, threshold=0.7)
        time.sleep(3)
except KeyboardInterrupt:
    print("Stopped by user.")
