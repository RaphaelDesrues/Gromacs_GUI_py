import inspect
from Qt import QtWidgets, QtCore, QtGui # type: ignore
from NodeGraphQt import NodeGraph, BaseNode, PropertiesBinWidget # type: ignore

from app.gui.node_library import NodeLibrary
from app.nodes import node_types
from app.gui.control_panel import ControlPanel
from app.gui.custom_widgets import FileLinkProperty


class MyPropertiesBinWidget(PropertiesBinWidget):
    def create_property_editor(self, node):
        editor = super().create_property_editor(node)

        tab_windows = getattr(editor, "_NodePropEditorWidget__tab_windows", None)
        if not tab_windows:
            return editor

        if "Properties" not in tab_windows:
            try:
                editor.add_tab("Properties")
            except Exception:
                pass
        prop_container = tab_windows.get("Properties")
        if prop_container is None:
            return editor

        file_prop = FileLinkProperty(prop_container)
        file_prop.set_name("file_link")
        try:
            cur = node.get_property("file_link")
        except Exception:
            cur = ""
        file_prop.set_value(cur if cur is not None else "")

        try:
            prop_container.add_widget(
                name="file_link",
                widget=file_prop,
                value=file_prop.get_value(),
                label="file link",
                tooltip="Select a file path"
            )
        except Exception:
            prop_container.add_widget("file_link", file_prop)

        # relayer vers l'éditeur (comme la lib le fait)
        if hasattr(editor, "_on_property_changed"):
            file_prop.value_changed.connect(lambda name, v: editor._on_property_changed(name, v))

        return editor
  


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        # Initializes main window
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

        # Create the right list panel
        self.node_list = NodeLibrary(node_types_list)

        # Create the left properties panel
        # self.node_props = NodeProperties() # Handmade props panel
        self.props_bin = PropertiesBinWidget(node_graph=self.node_graph)
        # self.props_bin = MyPropertiesBinWidget(node_graph=self.node_graph)


        self.control_panel = ControlPanel(self.node_graph)


        # Connect double click to node creation
        self.node_list.widget.itemDoubleClicked.connect(self.add_node_on_click)

        # Connect graph node to their properties
        self.node_graph.node_double_clicked.connect(self.show_props)

        # Connect control panel buttons
        # Select only the first node
        # self.control_panel.select_one_btn.clicked.connect(self.control_panel.selected_node)
        self.control_panel.select_one_btn.clicked.connect(self.control_panel.gen_gro_cmd)
        # Select all the selected nodes
        self.control_panel.select_many_btn.clicked.connect(self.control_panel.selected_nodes)
        # Select all nodes 
        self.control_panel.select_all_btn.clicked.connect(self.control_panel.select_all_nodes)
        # Generate bash script
        self.control_panel.generate_bash_script_btn.clicked.connect(self.control_panel.generate_bash_script)
        # Generate python script
        self.control_panel.generate_python_script_btn.clicked.connect(self.control_panel.generate_python_script)
        # Run GROMACS
        self.control_panel.run_gromacs_ui.clicked.connect(self.control_panel.run_gromacs_from_ui)

        # Delete node
        QtWidgets.QShortcut(
            QtGui.QKeySequence.Delete,  # Suppr key
            self,
            activated=lambda: self.node_graph.delete_nodes(self.node_graph.selected_nodes())
        )

        # Set the main window layout
        self._init_ui()



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

        if src_prop and dst_prop:
            try:
                val = src.node().get_property(src_prop)
                dst.node().set_property(dst_prop, val)  # updates model + UI signals
            except Exception:
                pass

    def _init_ui(self):
        main_splitter = QtWidgets.QSplitter()
        main_splitter.setOrientation(QtCore.Qt.Horizontal)
        
        # Left: list
        main_splitter.addWidget(self.node_list.widget)

        # Center: Vertical Split - Up
        center_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        center_splitter.addWidget(self.node_graph.widget)

        # Center: Vertical Split - Down (already a widget)
        center_splitter.addWidget(self.control_panel)

        # Add center_splitter to main_splitter
        main_splitter.addWidget(center_splitter)

        # Left: Props
        main_splitter.addWidget(self.props_bin)

        # Resize
        main_splitter.setSizes([150, 700, 250])
        center_splitter.setSizes([600, 150])
        self.setCentralWidget(main_splitter)


    def add_node_on_click(self, item):
        node_class = item.data(QtCore.Qt.UserRole) # Retrieves the class of the selected node
        node = self.node_graph.create_node(
            f"{node_class.__identifier__}.{node_class.__name__}",
            name=f"{node_class.NODE_NAME}",
            pos=[200, 200])
        
        for p in node.input_ports():
            try:
                print(f"ACCEPTS {p.name()} ->", node.accepted_port_types(p))
            except Exception as e:
                print("accepted_port_types failed:", e)

    def show_props(self, node):
        self.props_bin.show()
        self.props_bin.add_node(node)


