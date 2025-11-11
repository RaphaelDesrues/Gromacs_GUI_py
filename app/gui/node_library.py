import logging
from Qt import QtWidgets, QtCore # type: ignore


class NodeLibrary():
    """NodeLibrary is a class that manages a list of node types and displays them in a QListWidget.
    
    Attributes:
        node_types (list): A list of node types to be displayed in the widget.
        widget (QListWidget): The widget that displays the node types in icon mode.
    
    Methods:
        populate_list(): Populates the QListWidget with the names of the node classes.
    """
    def __init__(self, node_types=None):

        # List of nodes
        self.node_types = node_types or []

        # Creates an instance of QtListWidget for the list
        self.widget = QtWidgets.QListWidget()

        # Improve styling for node list
        self.widget = QtWidgets.QListWidget()
        self.widget.setViewMode(QtWidgets.QListView.IconMode)
        self.widget.setResizeMode(QtWidgets.QListView.Adjust)
        self.widget.setSpacing(10)
        self.widget.setMovement(QtWidgets.QListView.Static)
        self.widget.setUniformItemSizes(True)
        self.widget.setIconSize(QtCore.QSize(48, 48))
        self.widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Fill the node list with the pre-implemented nodes
        self.populate_list()


    def populate_list(self):
        """Populate the list widget with node class names.
        
        This method clears the existing items in the list widget and populates it with
        the names of the node classes defined in `self.node_types`. Each item in the
        list is associated with its corresponding node class for later retrieval.
        
        It handles exceptions that may occur during the addition of items to the list,
        logging any errors encountered.
        
        Raises:
            Exception: If an error occurs while adding a node class to the list.
        """
        self.widget.clear() # Initialize / Empty the list
        for node_class in self.node_types:
            try:
                # Create item witht the node_class name and point toward the class in the main_window
                item = QtWidgets.QListWidgetItem(node_class.__name__)
                item.setData(QtCore.Qt.UserRole, node_class)
                self.widget.addItem(item)
            except Exception:
                logging.exception("Failed to add node class to library: %r", node_class)
                continue
