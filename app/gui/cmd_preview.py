import logging
from Qt import QtWidgets, QtCore, QtGui   #type: ignore


class CmdPreview(QtWidgets.QWidget):
    """CmdPreview is a QWidget that provides a user interface for previewing node information.
    
    This class initializes a text area that displays a message prompting the user to select a node for preview. It is designed to be used within a node graph application.
    
    Attributes:
        node_graph (NodeGraph): The node graph associated with this preview widget.
        layout (QVBoxLayout): The layout manager for arranging child widgets vertically.
        text (QTextEdit): The text edit widget used to display the preview text.
    
    Methods:
        update_preview(text):
            Update the preview text in the UI with the provided text or a default message.
    """
    def __init__(self, node_graph):
        super().__init__()
        self.setObjectName("CmdPreview") # For qss use
        self.node_graph = node_graph
        self.layout = QtWidgets.QVBoxLayout(self)
        # self.text = QtWidgets.QPlainTextEdit()
        # self.text.setReadOnly(True)
        self.text = QtWidgets.QTextEdit(readOnly=True)
        self.text.setObjectName("CmdPreviewText") # For qss use
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.text.setFont(font)
        self.text.setPlainText("Select a Node for Preview")
        self.text.setMinimumHeight(50) 
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.text)


    def update_preview(self, text):
        """Update the preview text in the UI.
        
        This method sets the text of a preview area to the provided text. If the provided text is empty or None, it defaults to a message prompting the user to select a node for preview. In case of any exceptions during the update process, it logs the error and sets the preview area to indicate that the preview is unavailable.
        
        Args:
            text (str): The text to display in the preview area.
        
        Returns:
            None
        """
        try:
            self.text.setPlainText(text or "Select a Node for Preview")
            self.text.setAlignment(QtCore.Qt.AlignCenter)
        except Exception:
            logging.exception("Failed to update preview")
            self.text.setPlainText("Preview unavailable")
            self.text.setAlignment(QtCore.Qt.AlignCenter)
