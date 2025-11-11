import inspect
import logging

from Qt import QtWidgets, QtCore, QtGui # type: ignore
from NodeGraphQt import NodeGraph, BaseNode # type: ignore

# from app.gui import ui_state
from app.gui.node_library import NodeLibrary
from app.nodes import node_types
from app.gui.control_panel import ControlPanel, GromacsPanel, fill_cmd
from app.gui.cmd_preview import CmdPreview
from app.assets.my_prop_bin import MyPropertiesBin
from app.gui.ui_state import UiStateManager


class MainWindow(QtWidgets.QMainWindow):
    """MainWindow serves as the central controller of the node-based graphical workflow interface.  
    It manages the node graph, property panels, and control tools, coordinating the interaction 
    between nodes, their visual representations, and backend logic.

    This class extends `QtWidgets.QMainWindow` and acts as the primary GUI container that 
    integrates all major components of the workflow system, including the node canvas, 
    property editor, command preview, and control panels.

    Attributes:
        node_graph (NodeGraph):
            The main graph canvas handling node creation, connection management, and serialization.
        
        node_list (NodeLibrary):
            The library widget listing available node types for insertion into the graph.

        props_bin (MyPropertiesBin):
            The dynamic property editor showing editable parameters for the selected node.

        control_panel (ControlPanel):
            The panel providing workflow-level actions such as save/load, script generation, and refresh.

        cmd_preview (CmdPreview):
            Displays the generated command-line string that corresponds to the selected node’s configuration.

        gromacs_panel (GromacsPanel):
            Reserved extension panel for simulation-related tasks.

        ui_state (UiStateManager):
            Manages window layout, splitter geometry, and UI restoration between sessions.

    Methods:
        _init_ui():
            Assembles the main window layout, including the node graph canvas, property bin, 
            and bottom control tabs. Handles splitter proportions and visibility rules.

        _add_node_on_click(item):
            Triggered when a node is double-clicked from the node list. Creates and places 
            an instance of that node on the graph canvas.

        _show_props(node):
            Displays the property editor for the specified node on the right-hand side panel.

        _on_port_connected(port_a, port_b):
            Handles the event when two ports are connected.
            Normalizes direction (output → input) and propagates properties between nodes 
            based on declared port types and mappings in `IN_PORTS` / `OUT_PORTS`.

        _display_preview(node):
            Updates the live command preview corresponding to the currently selected or edited node.

        _on_prop_changed(node, menu_prop_name, prop_value):
            Handles property changes within a node.
            If the change comes from the optional property menu, dynamically adds the corresponding 
            input field or combo box; otherwise, propagates the value to connected nodes.

        _propagate_props(node, menu_prop_name, prop_value):
            Propagates the updated property value from one node to all connected nodes 
            by resolving matching input/output port definitions.

    Overall, MainWindow serves as the event hub for user interaction — linking UI widgets, 
    node logic, and real-time command generation into a cohesive workflow environment.
    """
    def __init__(self):

        # -------------------------
        # Initialize main windows
        # -------------------------
        super().__init__()
        self.setWindowTitle("Gromacs Node Workflow")
        self.resize(1000, 800)


        self.ui_state = UiStateManager(include_geometry=True, include_state=True)

        # Create core widgets
        # Create the central windows to manage nodes
        self.node_graph = NodeGraph()
        self.node_graph.port_connected.connect(self._on_port_connected)

        # Automatically retrieves all the class nodes
        # Attention detect only in it inherits from BaseNode
        node_types_list = [
            obj for name, obj in inspect.getmembers(node_types, inspect.isclass)
            if issubclass(obj, BaseNode)
            and obj is not BaseNode
            and obj.__module__ == node_types.__name__
        ]

        # Register the nodes in the graph canva
        for node in node_types_list:
            self.node_graph.register_node(node)


        # -------------------------
        # Create the main panel
        # -------------------------
        # Create the right list panel
        self.node_list = NodeLibrary(node_types_list)

        # Create the left properties panel
        self.props_bin = MyPropertiesBin(node_graph=self.node_graph)

        # Add control panel
        self.control_panel = ControlPanel(self.node_graph, self.ui_state)

        # Add command preview
        self.cmd_preview = CmdPreview(self.node_graph)

        # Add a gromacs panel (to be added later)
        self.gromacs_panel = GromacsPanel(self.node_graph)

        # Set the main window layout
        self._init_ui()


        # -------------------------
        # Add main window commands
        # -------------------------
        # Double click to add node to central panel
        self.node_list.widget.itemDoubleClicked.connect(self._add_node_on_click)

        # Double click on node to open custom porperties
        self.node_graph.node_double_clicked.connect(self._show_props)

        # Display and update preview if additional properties
        self.node_graph.node_selected.connect(self._display_preview)

        # Add additional properties to nodes
        self.node_graph.property_changed.connect(self._on_prop_changed)

        ## ControlPanel
        # Select all nodes
        self.control_panel.select_all_btn.clicked.connect(self.control_panel.select_all_nodes)

        # Generate scripts (bash, python)
        self.control_panel.generate_bash_script_btn.clicked.connect(self.control_panel.generate_bash_script)
        self.control_panel.generate_python_script_btn.clicked.connect(self.control_panel.generate_python_script)

        # Save and Load session (UI + NodeGraph)
        self.control_panel.save_session.clicked.connect(self.control_panel._save_ui)
        self.control_panel.load_session.clicked.connect(self.control_panel._load_ui)
        self.control_panel.refresh_session.clicked.connect(self.control_panel._refresh_ui)


        # -------------------------
        # Add shortcuts
        # -------------------------
        # Delete node
        QtWidgets.QShortcut(
            QtGui.QKeySequence.Delete,  # Suppr key
            self,
            activated=lambda: self.node_graph.delete_nodes(self.node_graph.selected_nodes())
        )

        QtWidgets.QShortcut(
            QtGui.QKeySequence.InsertParagraphSeparator,  # Enter key
            self,
            activated=lambda: self._display_preview()
        )


        # -------------------------
        # Add Menu Overview
        # -------------------------


    def _init_ui(self):
        main_splitter = QtWidgets.QSplitter()
        main_splitter.setObjectName("main_splitter")
        main_splitter.setOrientation(QtCore.Qt.Horizontal)

        # Left: list
        main_splitter.addWidget(self.node_list.widget)

        # Center: vertical splitter
        center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        center_splitter.setObjectName("center_tabs")
        center_splitter.addWidget(self.node_graph.widget)     # Up
        center_splitter.addWidget(self.cmd_preview)           # Preview of node command

        # Bottom: tabs area (Preview, Commands, Gromacs, ...)
        bottom_tabs = QtWidgets.QTabWidget()
        bottom_tabs.setObjectName("bottom_tabs")
        bottom_tabs.addTab(self.control_panel, "Controls")
        bottom_tabs.addTab(self.gromacs_panel, "GROMACS")
        center_splitter.addWidget(bottom_tabs)

        # Prevent collapse
        center_splitter.setCollapsible(0, False)
        center_splitter.setCollapsible(1, False)
        center_splitter.setCollapsible(2, False)

        # Reasonable proportions (3 widgets -> 3 sizes)
        # center_splitter.setSizes([650, 1, 300])

        # Stretch: graph takes more space, preview stays thin
        center_splitter.setStretchFactor(0, 15)
        center_splitter.setStretchFactor(1, 1)
        center_splitter.setStretchFactor(2, 4)

        # Add center splitter to main splitter
        main_splitter.addWidget(center_splitter)

        # Right: props
        main_splitter.addWidget(self.props_bin)

        # Global layout sizes (left / center / right)
        main_splitter.setSizes([200, 900, 320])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        main_splitter.setCollapsible(2, False)

        self.setCentralWidget(main_splitter)


    def _add_node_on_click(self, item):
        node_class = item.data(QtCore.Qt.UserRole) # Retrieves the class of the selected node
        node = self.node_graph.create_node(
            f"{node_class.__identifier__}.{node_class.__name__}",
            name=f"{node_class.NODE_NAME}",
            pos=[200, 200])


    def _show_props(self, node):
        self.props_bin.show()
        self.props_bin.add_node(node)


    def _on_port_connected(self, port_a, port_b): # Callback when two ports get connected
        """
        Called by NodeGraphQt when two ports get connected.
        Normalize (src=output, dst=input), then copy properties
        according to OUT_PORT/IN_PORT mapping (by port_type).
        """

        # Normalize: ensure src is an output and dst is an input
        try:
            src, dst = port_a, port_b
            if src.type_() == "in" and dst.type_() == "out":
                src, dst = dst, src
                logging.debug("Switched ports order")

            # Read port types (custom attributes you set on your ports)
            src_type = getattr(src, "port_type", None)
            dst_type = getattr(dst, "port_type", None)
            if not src_type or not dst_type:
                logging.debug("Missing port_type on ports; skip property propagation")
                return

            # Read the mapping "port_type -> property name" declared on each node
            src_map = getattr(src.node(), "OUT_PORT", {})
            dst_map = getattr(dst.node(), "IN_PORT",  {})

            # Pick property names and copy value once
            src_prop = src_map.get(src_type)
            dst_prop = dst_map.get(dst_type)
            if not src_prop or not dst_prop:
                logging.debug("No mapping for %s -> %s: skip property propagation", src_type, dst_type)

            # Copy value with safeguards so one bad node does not crash the UI
            try:
                val = src.node().get_property(src_prop)
                dst.node().set_property(dst_prop, val)
                logging.info("Propagated %s=%r from %s to %s", src_prop, val, src.node(), dst.node())
            except AttributeError as e: # If node lack expected methods/properties
                logging.warning("Attribute error during property copy: %s", e)
            except Exception: # Any unexpected error gets a full traceback
                logging.exception("Unexpected error while copying properties")

        except Exception:
            logging.exception("_on_port_connected failed")


        if src_prop and dst_prop:
            try:
                val = src.node().get_property(src_prop)
                dst.node().set_property(dst_prop, val)  
            except Exception:
                pass


    def _on_port_connected(self, port_a, port_b): # Callback when two ports get connected
        try:
            # Normalize: ensure src is an output and dst is an input
            src, dst = port_a, port_b
            if src.type_() == "in" and dst.type_() == "out":
                src, dst = dst, src
                logging.debug("Switched ports order (src/dst)")

            # Read port types (custom attributes you set on your ports)
            src_type = getattr(src, "port_type", None)
            dst_type = getattr(dst, "port_type", None)
            if not src_type or not dst_type:
                logging.debug("Missing port_type on ports; skip propagation")
                return

            # Map the IN_PORTS/OUT_PORTS declared on each node
            src_out_ports = getattr(src.node(), "OUT_PORTS", {}) or {}
            dst_in_ports = getattr(dst.node(), "IN_PORTS", {}) or {}

            dst_map = {port_type: flag for flag, (_name, port_type, *_rest) in dst_in_ports.items()}
            src_map = {port_type: flag for flag, (_name, port_type) in src_out_ports.items()}

            src_flag = src_map.get(src_type)
            dst_flag = dst_map.get(dst_type)
            if not src_flag or not dst_flag:
                logging.debug("No mapping for %s -> %s; skip propagation", src_type, dst_type)
                return

            try:
                val = src.node().get_property(src_flag)
            except Exception:
                logging.exception("Failed to read property '%s' from %s", src_flag, src.node())
                return

            try:
                dst.node().set_property(dst_flag, val)
                logging.info("Propagated %s=%r from %s to %s", dst_flag, val, src.node(), dst.node())
            except Exception:
                logging.exception("Failed to write property '%s' on %s", dst_flag, dst.node())

        except Exception: # Any unexpected error gets a full traceback
            logging.exception("_on_port_connected failed")


    def _display_preview(self, node):
        text = fill_cmd(nodes=node, preview=True)
        self.cmd_preview.update_preview(text)


    def _on_prop_changed(self, node, menu_prop_name, prop_value):
        # 1) If not optional_props → just propagate
        if menu_prop_name != "Add optional property" or not prop_value:
            try:
                self._propagate_props(node, menu_prop_name, prop_value)
            except Exception:
                logging.exception("Propagation failed in _on_prop_changed")
            return

        # 2) If optional_props selected → add the optional property
        try:
            label_to_key = getattr(node, "_opt_label_to_key", {})
            key = label_to_key.get(prop_value) 

            if not key or not hasattr(node, "OPTIONAL_PROPS"):
                logging.warning("Invalid optional prop selection: %r", prop_value)
                node.set_property("Add optional property", None)
                return

            label, default = node.OPTIONAL_PROPS[key]

            # Avoid double
            if key in node.properties().get("custom", {}):
                logging.info("Property '%s' already exists in %s, skipping", key, node)
                node.set_property("Add optional property", None)
                return

            # Add the correct widget
            if isinstance(default, (list, tuple)):
                node.add_combo_menu(name=key, label=label, items=default)
            else:
                node._add_text_input(name=key, label=label, text=default) # Use homemade _add_text_input
            
            node.hide_widget(key, push_undo=False)
            node.set_property("Added optional property", None)
            logging.info("Added optional property '%s' on %s", key, node)

            # Refresh the panel view
            self.props_bin.remove_node(node)
            self.props_bin.add_node(node)
            self._display_preview(node=node)

        except Exception:
            logging.exception("Failed to add or setup optional property '%s' on %s", prop_value, node)



    def _propagate_props(self, node, menu_prop_name, prop_value):

        try:
            src_dict = getattr(node, "OUT_PORT", {})
            src_prop_name = next((k for k, v in src_dict.items() if v == menu_prop_name), None)
            if not src_prop_name:
                logging.debug("No OUT_PORT mapping for menu '%s' on %s", menu_prop_name, node)
                return
        except Exception:
            logging.exception("Failed to resolve source mapping in _propagate_props")
            return

        # Retrieve all outputs of the source node
        try:
            src_outputs = node.outputs()
            if not isinstance(src_outputs, dict):
                logging.warning("node.outputs() should return a dict, got %r", type(src_outputs))
        except Exception:
            logging.exception("Failed to retrieve node outputs in _propagate_props")
            return

        # Iterate over each output port of the source node
        for port_name, port in src_outputs.items():
            try:
                dst_ports = port.connected_ports() # List of connected ports
            except Exception as e:
                logging.warning("connected_ports() failed on %s.%s: %s", node, port_name, e)
                continue

            # For every destination port connected to this source output
            for dst_port in dst_ports:
                # Retrieve corresponding node from the port
                try:
                    dst_node = dst_port.node()
                    dst_dict = getattr(dst_node, "IN_PORT", {})
                    dst_prop_name = dst_dict.get(src_prop_name)
                    if not dst_prop_name:
                        logging.debug("No IN_PORT mapping for '%s' on %s", src_prop_name, dst_node)
                        continue
                except Exception:
                    logging.exception("Failed to retrieve port of %s", dst_node)
                    continue

                try:
                    dst_node.set_property(dst_prop_name, prop_value)
                    logging.info("Propagated %s=%r -> %s", dst_prop_name, prop_value, dst_node)
                except AttributeError as e:
                    logging.warning("Destination node API error on %s: %s", dst_node, e)
                    continue
                except Exception:
                    logging.exception("Failed to set '%s' on %s", dst_prop_name, dst_node)
                    continue