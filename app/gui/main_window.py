import inspect
import logging

from Qt import QtWidgets, QtCore, QtGui # type: ignore
from NodeGraphQt import NodeGraph, BaseNode # type: ignore

from app.gui import ui_state
from app.gui.node_library import NodeLibrary
from app.nodes import node_types
from app.gui.control_panel import ControlPanel
from app.gui.cmd_preview import CmdPreview
from app.assets.my_prop_bin import MyPropertiesBin
from app.gui.ui_state import UiStateManager
import json, pathlib, os


class MainWindow(QtWidgets.QMainWindow):

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
        self.control_panel = ControlPanel(self.node_graph)

        # Add command preview
        self.cmd_preview = CmdPreview(self.node_graph)
        
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
        # self.control_panel.select_one_btn.clicked.connect(self._display_preview)
        self.node_graph.node_selected.connect(self._display_preview)
        
        # Select one, multiple or all nodes
        self.control_panel.select_one_btn.clicked.connect(self._save_ui)
        self.control_panel.select_many_btn.clicked.connect(self._load_ui)
        # self.control_panel.select_all_btn.clicked.connect(self.control_panel.select_all_nodes)
        
        # Generate scripts (bash, python)
        # self.control_panel.generate_bash_script_btn.clicked.connect(self.control_panel.generate_bash_script)
        # self.control_panel.generate_python_script_btn.clicked.connect(self.control_panel.generate_python_script)
        
        # Run GROMACS locally
        # self.control_panel.run_gromacs_ui.clicked.connect(self.control_panel.run_gromacs_from_ui)

        # Add additional properties to nodes
        self.node_graph.property_changed.connect(self._on_prop_changed)


        # -------------------------
        # Add shortcuts
        # -------------------------
        # Delete node
        QtWidgets.QShortcut(
            QtGui.QKeySequence.Delete,  # Suppr key
            self,
            activated=lambda: self.node_graph.delete_nodes(self.node_graph.selected_nodes())
        )


    def _init_ui(self):
        main_splitter = QtWidgets.QSplitter()
        main_splitter.setObjectName("main_splitter")
        # print("MAIN8SPLLITER", main_splitter.objectName())
        main_splitter.setOrientation(QtCore.Qt.Horizontal)
        
        # Left: list
        main_splitter.addWidget(self.node_list.widget)

        # Center: vertical splitter
        center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        center_splitter.setObjectName("center_tabs")
        center_splitter.addWidget(self.node_graph.widget)     # Up
        center_splitter.addWidget(self.cmd_preview)           # Preview of node command
        center_splitter.addWidget(self.control_panel)         # Down

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
                dst.node().set_property(dst_prop, val)  # updates model + UI signals
            except Exception:
                pass


    def _display_preview(self, node):
        text  = self.control_panel.fill_one_cmd(node)
        self.cmd_preview.update_preview(text)
    

    def _on_prop_changed(self, node, menu_prop_name, prop_value):
        # Process only the properties in the menu
        try:
            if menu_prop_name != "Add_Props" or not prop_value:
                # If not adding a new property, delegate the propagation logic
                self._propagate_props(node, menu_prop_name, prop_value)
        except Exception:
            logging.exception("Propagation failed in _on_prop_changed")

        # Retrieve name and value from the dict
        try:
            name, value = node.PREDEFINED_PROPS[prop_value]
        except KeyError:
            # Triggered when 'prop_value' is not a key in PREDEFINED_PROPS.
            logging.warning("Key '%s' no in PREDEFINED_PROPS of '%s'", prop_value, node)
            return

        # Avoid duplicates
        try:
            node_props = node.properties().get("custom", {})
            if name in node_props:
                logging.info("Property '%s' already exists in %s, skipping", name, node)
                # node.set_property("Add_Props", None)
                return
            # Add the proprety using MyBaseNode.add_text_input
            node.add_text_input(name=name, label=prop_value, text=value)
            node.hide_widget(name=name, push_undo=False)
            logging.info("Property added: %s on %s", name, node)

            # Reset the menu
            node.set_property("Add_Props", None)
        except Exception:
            logging.exception("Failed to add or setup property '%s' on %s", name, node)
            return

        # Refresh the property bin
        try:
            self.props_bin.remove_node(node)
            self.props_bin.add_node(node)
        except Exception as e:
            logging.warning("Refresh props_bin failed for %s: %s", node, e)


        # Refresh the preview
        try:
            if hasattr(self, "update_preview"):
                # self.update_preview()
                self.cmd_preview.update_preview(self.control_panel.fill_all_cmd(), node)
        except Exception:
            logging.exception("Failed to update preview after property change")


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


    def _save_ui(self):
        logging.info("Saving UI state + NodeGraph session...")
        path = pathlib.Path("/home/rapha/file_bundle.json")
        
        # 1) Save graph
        # Use serialize instead of save_session here because we need to modify the json 
        graph_data = self.node_graph.serialize_session()
        # self.node_graph.save_session(path)

        graph_data.get("graph", {}).pop("accept_connection_types", None)
        graph_data.get("graph", {}).pop("reject_connection_types", None)
        for n in graph_data.get("nodes", {}).values():
            n.pop("accept_connection_types", None)
            n.pop("reject_connection_types", None)

        # 2) Save UI state
        ui_data = self.ui_state.capture(self)
        bundle = {"graph": graph_data, "ui": ui_data}
        path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        logging.info("UI state saved at %s", path)


    def _load_ui(self):
        path = pathlib.Path("/home/rapha/file_bundle.json")
        logging.info("Loading UI state + NodeGraph session from: %s", path)
        data = json.loads(path.read_text(encoding="utf-8"))
        
        # 1) Load graph
        self.node_graph.clear_session()
        self.node_graph.deserialize_session(data["graph"])

        # 2) Load UI
        self.ui_state.restore(self, data["ui"])
        logging.info("UI state loaded")



