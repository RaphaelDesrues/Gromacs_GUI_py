import logging
from NodeGraphQt.custom_widgets.properties_bin.node_property_widgets import PropertiesBinWidget, NodePropEditorWidget #type: ignore
from NodeGraphQt import BaseNode # type: ignore
from Qt import QtCore, QtWidgets, QtGui # type: ignore
from itertools import product

# -----------------------------
# Custom BaseNode
# -----------------------------
class MyBaseNode(BaseNode):
    """MyBaseNode is a subclass of BaseNode that manages node properties and ports for a graphical interface.
    
    Attributes:
        NODE_TYPES (list): A list of supported node types.
        PORT_TYPES (list): A list of supported port types.
    
    Methods:
        __init__(): Initializes the MyBaseNode instance and sets up properties and ports.
        _add_text_input(name, label=None, text=""): Adds a text input property to the node.
        _add_base_props(): Adds base properties to the node.
        _add_optional_props(): Adds optional properties to the node if available.
        _hide_all_props(): Hides all custom properties from the node's interface.
        _add_ports(): Adds input and output ports to the node.
        _manage_accepts(): Manages the acceptance of port types for input ports.
        _auto_setup(): Automatically sets up the node by adding properties and ports.
    """

    NODE_TYPES = [
        "pdb2gmx.Pdb2gmx",
        "editconf.Editconf",
        "solvate.Solvate",
        "genion.Genion",
        "grompp.Grompp",
        "mdrun.Mdrun",
        "trjconv.Trjconv",
    ]

    PORT_TYPES = ["in", "out"]

    def __init__(self):
        super().__init__()
        self._prop_labels = {}
        self.all_ports = {}

        self._auto_setup()

    def _add_text_input(self, name, label=None, text=""):
        """Adds a text input field to the form.
        
        Args:
            name (str): The name of the text input field.
            label (str, optional): The label for the text input field. Defaults to None.
            text (str, optional): The initial text for the text input field. Defaults to an empty string.
        
        Returns:
            TextInput: The created text input field.
        """
        if label:
            self._prop_labels[name] = label
        return super().add_text_input(name=name, label=label, text=text)
    
    def _add_base_props(self):
        """Adds base properties to the user interface.
        
        This method iterates over the `BASE_PROPS` dictionary and adds either a combo menu or a text input 
        to the user interface based on the type of the property value. If the value is a list, a combo menu 
        is created; otherwise, a text input is added. Any exceptions raised during the addition of properties 
        are logged as warnings.
        
        Attributes:
            BASE_PROPS (dict): A dictionary containing base property names as keys and a tuple of 
                               (label, value) as values.
        
        Raises:
            Exception: Logs a warning if there is an error while adding a base property.
        """
        for k, v in self.BASE_PROPS.items():
            try:
                # Set up list if limited choices
                if isinstance(v[1], list):
                    self.add_combo_menu(name=k, label=v[0], items=v[1])
                # Else set up writabble zone
                else:
                    self._add_text_input(name=k, label=v[0], text=v[1])
            except Exception as e:
                logging.warning("Failed to add base prop %s: %s", k, e)

    def _add_optional_props(self):
        """Adds optional properties widget picker
        
        This method checks if the instance has the attribute `OPTIONAL_PROPS` and if it is not empty. 
        If so, it creates a mapping of optional property labels to their corresponding keys, 
        adds a combo menu for selecting optional properties, hides the widget, 
        and sets the initial property value to None.
        
        Attributes:
            OPTIONAL_PROPS (dict): A dictionary containing optional properties.
        
        Methods:
            add_combo_menu(name, label, items): Adds a combo menu to the widget.
            hide_widget(name, push_undo): Hides the specified widget.
            set_property(name, value): Sets the property of the widget.
        """
        if hasattr(self, "OPTIONAL_PROPS") and self.OPTIONAL_PROPS:
            self._opt_label_to_key = {v[0]: k for k, v in self.OPTIONAL_PROPS.items()}

            self.add_combo_menu(
                name="Add optional property",
                label="Add optional property",
                items=list(self._opt_label_to_key.keys())
            )
            self.hide_widget("Add optional property", push_undo=False)
            self.set_property("Add optional property", None)

    def _hide_all_props(self):
        """Hides all embedded custom properties, so they don't appear in the node itself
        
        This method iterates through the custom properties of the widget and calls
        the `hide_widget` method for each property, suppressing the undo functionality.
        If an error occurs during the process, a warning is logged.
        
        Raises:
            Exception: Logs a warning if an error occurs while hiding properties.
        """
        try:
            [
                self.hide_widget(k, push_undo=False)
                for k in self.properties().get("custom", {}).keys()
                if k != "Add optional property"
            ]
        except Exception as e:
            logging.warning("Failed to hide props: %s", e)

    def _add_ports(self):
        """Adds input and output ports to the current object.
        
        This method iterates over the defined input and output ports, creating and 
        adding them to the object's port collection. It handles any exceptions that 
        may occur during the addition of ports, logging a warning message if an 
        error is encountered.
        
        Attributes:
            IN_PORTS (dict): A dictionary containing input port definitions, where 
                             each key is an identifier and the value is a tuple 
                             containing the port name, port type, and additional info.
            OUT_PORTS (dict): A dictionary containing output port definitions, where 
                              each key is an identifier and the value is a tuple 
                              containing the port name and port type.
            all_ports (dict): A dictionary that stores all added ports, indexed by 
                              their names.
        
        Raises:
            Exception: Logs a warning if there is an error while adding input or 
                       output ports.
        """
        # Retrieves the port (IN/OUT) informations 
        try:
            for _, (name, port_type, _) in self.IN_PORTS.items():
                port = self.add_input(name)
                port.port_type = port_type
                self.all_ports[port.name()] = port
        except Exception as e:
            logging.warning("Failed to add in port: %s", e)

        try:
            for _, (name, port_type) in self.OUT_PORTS.items():
                port = self.add_output(name)
                port.port_type = port_type
                self.all_ports[port.name()] = port
        except Exception as e:
            logging.warning("Failed to add port: %s", e)

    # For each port, each type ("in", "out") and each node_type = identifier, one may use 'add_accept_port_type'
    def _manage_accepts(self):
        """Manage the acceptance of port types for each input port.
        
        This method iterates over the input ports defined in `self.IN_PORTS` and for each port, it generates combinations of accepted port names, port types, and node types. It then calls the `add_accept_port_type` method to register these combinations for the corresponding port.
        
        Args:
            self: The instance of the class that contains the method.
        
        Returns:
            None
        """
        for _, (name, _, accepts) in self.IN_PORTS.items():
            for port_name, port_type, node_type in product(accepts, self.PORT_TYPES, self.NODE_TYPES):
                self.add_accept_port_type(
                    self.all_ports[name],
                    dict(
                        port_name=port_name,
                        port_type=port_type,
                        node_type=node_type
                    ),
                )

    def _auto_setup(self):
        """Automatically sets up the properties and configurations for the instance of a node.
        
        This method performs a series of setup operations, including adding optional and base properties, hiding all properties, adding ports, and managing accepts. If any step in the setup process fails, a warning is logged with the node name and the exception message.
        
        Raises:
            Exception: If any of the setup operations fail, a warning is logged but the exception is not raised.
        """
        try:
            self._add_optional_props()
            self._add_base_props()
            self._hide_all_props()
            self._add_ports()
            self._manage_accepts()
        except Exception as e:
            logging.warning(f"Auto setup failed for {self.NODE_NAME}: {e}")

# -----------------------------
# Custom add_text_input
# -----------------------------
class MyPropEditor(NodePropEditorWidget):
    """MyPropEditor is a custom property editor widget that extends the NodePropEditorWidget. It is designed to read and manage properties of a node, including applying pretty labels, tagging custom properties, and attaching file picker actions to specific properties.
    
    Methods:
        _read_node(node):
            Reads the properties of the given node and updates the associated widgets with pretty labels and property roles.
    
        _browse_file(edit, prop_name):
            Opens a file dialog to select a file and updates the corresponding property of the node with the selected file path.
    
        _DoubleClickFilter:
            A helper class that filters double-click events on the property editor's widgets to trigger the file browsing functionality.
    """
    def _read_node(self, node):
        """Reads a node and applies various configurations to its associated widgets.
        
        This method retrieves properties from the given node and updates the corresponding widgets
        with pretty labels, custom property roles, and file picker actions. It handles exceptions
        during the process and logs any failures encountered.
        
        Args:
            node: The node object from which properties are read and widgets are updated.
        
        Returns:
            ports: The ports read from the node, as obtained from the superclass method.
        
        Raises:
            Exception: Logs any exceptions that occur during the processing of the node.
        """
        ports = super()._read_node(node)
        # Retrieve the labels in add_text_input
        mapping = getattr(node, "_prop_labels", {})

        for prop_name, pretty_label in mapping.items():
            try:
                w = self.get_widget(prop_name)
                if not w:
                    continue

                # Access internal grid that stores: QLabel, widget
                container = w.parent()
                grid = getattr(container, "_PropertiesContainer__layout", None)
                if not grid:
                    continue

                idx = grid.indexOf(w)
                if idx < 0:
                    continue

                r, c, rs, cs = grid.getItemPosition(idx)
                item = grid.itemAtPosition(r, 0)  # 0 = column label
                if item and item.widget():
                    item.widget().setText(pretty_label)
            except Exception:
                logging.exception("Failed to apply pretty label for %s on %s", prop_name, node)
        
        # Colors by role based on IN_PORT / OUT_PORT mapping
        try:
            in_flags = set((getattr(node, "IN_PORTS", {}) or {}).keys())
            out_flags = set((getattr(node, "OUT_PORTS", {}) or {}).keys())
            props = node.properties().get("custom", {})
            for name in props.keys():
                w = self.get_widget(name)
                if not w:
                    continue

                role = "in" if name in in_flags else ("out" if name in out_flags else "param")

                w.setProperty("propRole", role)

                # Force Qt to apply sytle
                style = w.style()
                if style:
                    style.unpolish(w)
                    style.polish(w)
                w.update()

        except Exception:
            logging.exception("Failed to tag custom properties for node %s", node)

        # Add file picker icon
        try:
            file_related_props = {"-f", "-o", "-p", "-c", "-n"} # Needs for more general way to handle them
            for prop_name in file_related_props:
                w = self.get_widget(prop_name)
                if not isinstance(w, QtWidgets.QLineEdit):
                    continue

                # Avoid duplicate icons
                if any(act.objectName() == f"{prop_name}_file_action" for act in w.actions()):
                    continue

                icon = QtGui.QIcon.fromTheme("folder-open")
                if icon.isNull():
                    tmp_btn = QtWidgets.QToolButton(w)
                    icon = tmp_btn.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon)
                    tmp_btn.deleteLater()

                action = w.addAction(icon, QtWidgets.QLineEdit.TrailingPosition)
                action.setObjectName(f"{prop_name}_file_action")
                action.setToolTip("Browse for a file")

                # Connect icon click to file dialog
                action.triggered.connect(lambda _, e=w, n=prop_name: self._browse_file(e, n))

                # Double-click to open dialog too
                w.installEventFilter(self._DoubleClickFilter(self, w, prop_name))
        except Exception:
            logging.exception("Failed to attach file picker actions")


        return ports

    def _browse_file(self, edit, prop_name):
        """Browse for a file and set the specified property with the selected file path.
        
        This method opens a file dialog for the user to select a file. If a file is selected, 
        it updates the provided edit widget with the file path and attempts to set the specified 
        property of the current node with the selected file path. If setting the property fails, 
        an exception is logged.
        
        Args:
            edit (QLineEdit): The edit widget where the selected file path will be displayed.
            prop_name (str): The name of the property to set with the selected file path.
        
        Returns:
            None
        """
        start_dir = edit.text() or ""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select file", start_dir, "All Files (*)"
        )
        if path:
            edit.setText(path)
            try:
                self.node().set_property(prop_name, path)
            except Exception:
                logging.exception("Failed to set property after file selection")

    class _DoubleClickFilter(QtCore.QObject):
        def __init__(self, parent, edit, prop_name):
            super().__init__(parent)
            self._parent = parent
            self._edit = edit
            self._prop_name = prop_name

        def eventFilter(self, obj, ev):
            if obj is self._edit and ev.type() == QtCore.QEvent.MouseButtonDblClick:
                self._parent._browse_file(self._edit, self._prop_name)
                return True
            return False


class MyPropertiesBin(PropertiesBinWidget):
    def create_property_editor(self, node):
        return MyPropEditor(node=node)
