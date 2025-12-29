import sys, threading, logging
from PyQt5.QtCore import Qt, QRect, QPoint, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QGuiApplication

from pynput import keyboard

class HotkeyBridge(QObject):
    quitRequested = pyqtSignal()

def start_global_hotkeys(bridge: HotkeyBridge):
    logging.info('Starting global hotkeys listener')
    # Runs in a non-Qt thread. Emit signals back into the Qt thread.
    def on_press(key):
        try:
            logging.info(f'Key pressed: {key}')
            if isinstance(key, keyboard.KeyCode) and key.char and key.char.lower() == 'q':
                bridge.quitRequested.emit()
        except AttributeError:
            pass  # non-char keys
        # You can add more: e.g., ESC to quit
        if key == keyboard.Key.esc:
            logging.info('ESC pressed: quitting')
            bridge.quitRequested.emit()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # non-blocking
    return listener

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        logging.info('Window flags set to Frameless + StayOnTop + Window (not Tool) to accept input reliably')
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        union = None
        for screen in QGuiApplication.screens():
            union = screen.geometry() if union is None else union.united(screen.geometry())
        self.setGeometry(union)
        logging.info(f'Overlay geometry set to union of screens: {union}')

        self.dragging = False
        self.start = QPoint()
        self.end = QPoint()
        self.rect_color = QColor(0, 150, 255, 180)
        self.fill_color = QColor(0, 150, 255, 50)
        self.setCursor(Qt.CrossCursor)

        self.setFocusPolicy(Qt.StrongFocus)
        self.raise_()
        self.activateWindow()
        logging.info('Overlay shown; raised and activated')
        self.show()

    def mousePressEvent(self, e):
        logging.info(f'mousePressEvent: button={e.button()} globalPos={e.globalPos()} localPos={e.pos()}')
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.start = e.globalPos()
            self.end = e.globalPos()
            self.update()

    def mouseMoveEvent(self, e):
        if self.dragging:
            logging.info(f'mouseMoveEvent while dragging: globalPos={e.globalPos()} localPos={e.pos()}')
        if self.dragging:
            self.end = e.globalPos()
            self.update()

    def mouseReleaseEvent(self, e):
        logging.info(f'mouseReleaseEvent: button={e.button()} globalPos={e.globalPos()} localPos={e.pos()} dragging={self.dragging}')
        if e.button() == Qt.LeftButton:
            self.dragging = False
            self.end = e.globalPos()
            self.update()
            logging.info(f'end draw: start {self.start}, end {self.end}')
            print(f"end draw: start{self.start}, end:{self.end}")

    def enterEvent(self, e):
        logging.info('enterEvent: mouse entered overlay')

    def leaveEvent(self, e):
        logging.info('leaveEvent: mouse left overlay')

    def focusInEvent(self, e):
        logging.info('focusInEvent: overlay focused')

    def focusOutEvent(self, e):
        logging.info('focusOutEvent: overlay lost focus')

    def paintEvent(self, _):
        # draw dim background and selection rect; log rect
        if self.start != self.end:
            r = QRect(self.mapFromGlobal(self.start), self.mapFromGlobal(self.end)).normalized()
            logging.info(f'paintEvent: drawing rect {r}')
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        # Always paint dim background so instructions are visible
        p.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self.start == self.end:
            # draw instruction text even when idle
            p.setPen(QPen(QColor(255, 255, 255, 220), 1))
            p.drawText(10, 30, 'Drag with left mouse to select. Press ESC or Q to quit.')
            return
        r = QRect(self.mapFromGlobal(self.start), self.mapFromGlobal(self.end)).normalized()
        p.fillRect(r, self.fill_color)
        p.setPen(QPen(self.rect_color, 2))
        p.drawRect(r)
        # Instruction text
        p.setPen(QPen(QColor(255, 255, 255, 220), 1))
        p.drawText(10, 30, 'Drag with left mouse to select. Press ESC or Q to quit.')

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('automite.log', mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info('Application starting')
    app = QApplication(sys.argv)
    try:
        screens = QGuiApplication.screens()
        for i, s in enumerate(screens):
            logging.info(f'Screen {i}: name={getattr(s, "name", lambda: "")()} geometry={s.geometry()}')
    except Exception as ex:
        logging.exception(f'Failed to enumerate screens: {ex}')
    overlay = Overlay()

    bridge = HotkeyBridge()
    def on_quit():
        logging.info('Quit requested via hotkey')
        app.quit()
    bridge.quitRequested.connect(on_quit)

    # Start global hotkeys
    listener = start_global_hotkeys(bridge)

    # Run Qt event loop
    logging.info('Entering Qt event loop')
    exit_code = app.exec_()
    logging.info(f'Qt event loop exited with code {exit_code}')

    # Clean up listener on exit
    try:
        listener.stop()
        logging.info('Global hotkeys listener stopped')
    except Exception as ex:
        logging.exception(f'Error stopping listener: {ex}')
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
