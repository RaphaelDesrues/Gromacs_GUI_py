from Qt import QtWidgets # type: ignore
from app.gui.main_window import MainWindow

def main():
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
