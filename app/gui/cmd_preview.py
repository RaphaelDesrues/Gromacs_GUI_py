import logging
from Qt import QtWidgets, QtCore, QtGui   #type: ignore


class CmdPreview(QtWidgets.QWidget):

    def __init__(self, node_graph):
        super().__init__()
        self.node_graph = node_graph
        self.layout = QtWidgets.QVBoxLayout(self)
        # self.text = QtWidgets.QPlainTextEdit()
        # self.text.setReadOnly(True)
        self.text = QtWidgets.QTextEdit(readOnly=True)
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.text.setFont(font)
        self.text.setPlainText("Select a Node for Preview")
        self.text.setMinimumHeight(50) 
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.text)


    def update_preview(self, text):
        try:
            # print("TEST", " ".join(["gmx", node.__identifier__, text]))
            self.text.setPlainText(text or "Select a Node for Preview")
            self.text.setAlignment(QtCore.Qt.AlignCenter)
        except Exception:
            logging.exception("Failed to update preview")
            self.text.setPlainText("Preview unavailable")
            self.text.setAlignment(QtCore.Qt.AlignCenter)
