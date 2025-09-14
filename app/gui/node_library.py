# Contains the list of the available nodes (defined in node_types.py)
# 1. Display the nodes
# 2. Handle the double-clic on nodes -> 
import logging
from Qt import QtWidgets, QtCore # type: ignore


class NodeLibrary():
        
    def __init__(self, node_types=None):
        
        # List of nodes
        self.node_types = node_types or []

        # Creates an instance of QtListWidget for the list
        self.widget = QtWidgets.QListWidget()

        # Fill the node list with the pre-implemented nodes
        self.populate_list()


    def populate_list(self):
        '''
        Add to the widget list all the node class
        '''
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
