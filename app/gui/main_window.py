from genericpath import exists
import inspect
from itertools import product
from sqlite3 import connect
from Qt import QtWidgets, QtCore, QtGui # type: ignore
from NodeGraphQt import NodeGraph, BaseNode # type: ignore

from app.gui.node_library import NodeLibrary
from app.nodes import node_types
from app.gui.control_panel import ControlPanel
from app.gui.cmd_preview import CmdPreview
from app.assets.my_prop_bin import MyPropertiesBin


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        
        # -------------------------
        # Initialize main windows
        # -------------------------
        super().__init__()
        self.setWindowTitle("Gromacs Node Workflow")
        self.resize(1000, 800)

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
        self.control_panel.select_one_btn.clicked.connect(self.control_panel.selected_node)
        self.control_panel.select_many_btn.clicked.connect(self.control_panel.selected_nodes)
        self.control_panel.select_all_btn.clicked.connect(self.control_panel.select_all_nodes)
        
        # Generate scripts (bash, python)
        self.control_panel.generate_bash_script_btn.clicked.connect(self.control_panel.generate_bash_script)
        self.control_panel.generate_python_script_btn.clicked.connect(self.control_panel.generate_python_script)
        
        # Run GROMACS locally
        self.control_panel.run_gromacs_ui.clicked.connect(self.control_panel.run_gromacs_from_ui)

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
        main_splitter.setOrientation(QtCore.Qt.Horizontal)
        
        # Left: list
        main_splitter.addWidget(self.node_list.widget)

        # Center: vertical splitter
        center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
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
        
        # for p in node.input_ports():
        #     try:
        #         print(f"ACCEPTS {p.name()} ->", node.accepted_port_types(p))
        #     except Exception as e:
        #         print("accepted_port_types failed:", e)


    def _show_props(self, node):
        self.props_bin.show()
        self.props_bin.add_node(node)


    def _on_port_connected(self, port_a, port_b):
        """
        Called by NodeGraphQt when two ports get connected.
        Normalize (src=output, dst=input), then copy properties
        according to OUT_PORT/IN_PORT mapping (by port_type).
        """
        # for attr in dir(port_a):
        #     if not attr.startswith('__'):
        #         try:
        #             print(f"{attr} = {getattr(port_a, attr)}")
        #         except Exception:
        #             pass

        # 1) Normalize: ensure src is an output and dst is an input
        src, dst = port_a, port_b
        if src.type_() == "in" and dst.type_() == "out":
            src, dst = dst, src
            print("Switched ports order")

        print("Port type: IN", dst.type_(), " OUT", src.type_())
        print("Port name: ", src.name())
        print("Port type custom: ", src.port_type)

        # 2) Read port types (custom attributes you set on your ports)
        src_type = getattr(src, "port_type", None)
        dst_type = getattr(dst, "port_type", None)

        # 3) Read the mapping "port_type -> property name" declared on each node
        src_map = getattr(src.node(), "OUT_PORT", {})
        dst_map = getattr(dst.node(), "IN_PORT",  {})

        # 4) Pick property names and copy value once
        src_prop = src_map.get(src_type)
        dst_prop = dst_map.get(dst_type)
        print('test', src_prop, dst_prop)

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
        # menu_prop_name = property name in the menu != property name to add
        # prop_value = item of the menu = property label to add

        # We process only the properties in the menu
        if menu_prop_name != "Add_Props" or not prop_value:
            self._propagate_props(node, menu_prop_name, prop_value)

        # Retrieve name and value from the dict
        try:
            name, value = node.PREDEFINED_PROPS[prop_value]
        except Exception:
            print(f"[WARN] Key '{prop_value}' not in PREDEFINED_PROPS of {node}")
            return

        # Avoid duplicates
        node_props = node.properties().get("custom", {})
        if name in node_props:
            print(f"[INFO] Property '{name}' already exists in {node}, pass")
            # node.set_property("Add_Props", None)
            return

        # Add the proprety using MyBaseNode.add_text_input
        node.add_text_input(name=name, label=prop_value, text=value)
        node.hide_widget(name=name, push_undo=False)
        print("[INFO] Property added")

        # Check
        # props_after = node.properties().get("custom", {})
        # ok = props_after.get(prop_value, None)
        # print(f"[CHECK] '{prop_value}' enregistré =", repr(ok))

        # Reset the menu
        node.set_property("Add_Props", None)

        # Refresh the property bin
        try:
            self.props_bin.remove_node(node)
            self.props_bin.add_node(node)
        except Exception as e:
            print("[WARN] Refresh props_bin:", e)

        # Refresh the preview
        if hasattr(self, "update_preview"):
            # self.update_preview()
            self.cmd_preview.update_preview(self.control_panel.fill_all_cmd(), node)

        # Debug signal
        # print("=== property_changed ===")
        # print("Node:", node)
        # print("name:", menu_prop_name)
        # print("name:", name)
        # print("value:", value)
        # print("========================")


    def _propagate_props(self, node, menu_prop_name, prop_value):
        print("NODE:", node)
        print("PROP_NAME:", menu_prop_name)

        src_outputs = node.outputs()
        dst_nodes = node.connected_output_nodes()

        if not any(dst_nodes.values()):
            return

        for connected_nodes in dst_nodes.values():
            for connected_node in connected_nodes:
                for port_out, port_in in product(src_outputs.values(), connected_node.inputs().values()):
                    print("TEST", port_out, port_in)
                    self._on_port_connected(port_out, port_in)


