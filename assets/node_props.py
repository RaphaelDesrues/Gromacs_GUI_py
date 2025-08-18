# Handle the properties of the node
# Display and update the node properties

from Qt import QtWidgets # type: ignore


class NodeProperties(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # # Initializes the list widget to display the properties
        # self.widget = QtWidgets.QListWidget()
        self.layout = QtWidgets.QFormLayout()
        # Says that NodeProperties is now a widegt
        # Layout is an internal organisator
        self.setLayout(self.layout)
        self.current_node = None


    def show_properties(self, node):
        self.current_node = node
        # Efface tous les widgets précédents
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if not node:
            return

        print("DEBUG1", node.properties()) # All inherent properties + custom ones
        print("DEBUG2", node.get_property("TestParams")) # Only the property with that name
        # Get among all properties only the custom ones
        # for prop_name, prop_value in node.properties().get('custom', {}).items():
        #     print("DEBUG3", prop_name, prop_value)
        #     # Display a props in a QtWidgets Label and add a row
        #     # Non-editable for now
        #     label = QtWidgets.QLabel(str(prop_value))
        #     self.layout.addRow(prop_name, label)

        for prop_name, prop_value in node.properties().get('custom', {}).items():
            edit = QtWidgets.QLineEdit(str(prop_value))   # QLineEdit modifiable
            edit.setProperty("prop_name", prop_name)      # on stocke le nom de la propriété dans le widget
            edit.editingFinished.connect(self._on_edit_finished)  # callback pour maj la prop dans le node
            self.layout.addRow(prop_name, edit)


    def _on_edit_finished(self):
        edit = self.sender()
        prop_name = edit.property("prop_name")
        new_value = edit.text()
        if self.current_node:
            self.current_node.set_property(prop_name, new_value)

    
