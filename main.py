import logging
from Qt import QtWidgets # type: ignore
from app.gui.main_window import MainWindow

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    app = QtWidgets.QApplication([])

    # Load the main style sheet
    with open("styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    # Shadow theme
    # try:
    #     import qdarktheme
    #     qdarktheme.setup_theme("dark")
    # except Exception:
    #     pass
    
    win = MainWindow()
    win.showMaximized()
    app.exec_()

if __name__ == "__main__":
    main()
