import logging
from Qt import QtWidgets # type: ignore
from app.gui.main_window import MainWindow

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    app = QtWidgets.QApplication([])
    # Shadow theme
    # try:
    #     import qdarktheme
    #     qdarktheme.setup_theme("dark")
    # except Exception:
    #     pass
    win = MainWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
