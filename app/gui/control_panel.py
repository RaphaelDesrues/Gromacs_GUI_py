from Qt import QtWidgets, QtCore # type: ignore
import os, logging, pathlib, json, tempfile
from app.gui.process_runner import ProcessRunner


def fill_one_cmd(node):
    node_props = node.properties().get("custom", {})
    cmd_tmp = " ".join(f"{name} {value}" for name, value in node_props.items() if name != "Add optional property")
    return cmd_tmp


def fill_cmd(nodes=None, preview=False):

    # For preview: display props of selected node
    if preview and nodes is not None:
        cmd_tmp = fill_one_cmd(nodes)
        cmd = " ".join(["gmx", nodes.__identifier__, cmd_tmp])
        return cmd

    # Return gmx_cmd of multiple nodes or all_nodes
    cmds = []
    # Spatially organises the script as the node from left to right
    all_nodes = sorted(nodes, key=lambda n: n.pos()[0])

    for node in all_nodes:
        cmd_tmp = fill_one_cmd(node)
        cmds.append(" ".join(["gmx", node.__identifier__, cmd_tmp]))
    return cmds


class ControlPanel(QtWidgets.QWidget):
    """ControlPanel is a QWidget that provides a user interface for managing a node graph.
    
    Attributes:
        node_graph (NodeGraph): The node graph that this control panel interacts with.
        ui_state (UIState): The current state of the user interface.
        layout (QVBoxLayout): The layout manager for arranging widgets vertically.
        select_all_btn (QPushButton): Button to select all nodes in the node graph.
        generate_bash_script_btn (QPushButton): Button to generate a Bash script from the node graph.
        generate_python_script_btn (QPushButton): Button to generate a Python script from the node graph.
        save_session (QPushButton): Button to save the current session of the UI and node graph.
        load_session (QPushButton): Button to load a previously saved session of the UI and node graph.
        refresh_session (QPushButton): Button to refresh the current session of the UI and node graph.
    
    Methods:
        select_all_nodes(): Returns a list of all nodes in the node graph.
        _save_ui(): Saves the current UI state and node graph session to a JSON file.
        _load_ui(): Loads a UI state and node graph session from a JSON file.
        _refresh_ui(): Saves the current UI state and then loads it back.
        generate_bash_script(): Generates a Bash script based on the current node graph.
        generate_python_script(): Generates a Python script based on the current node graph.
    """
    def __init__(self, node_graph, ui_state):
        super().__init__()
        self.node_graph = node_graph
        self.ui_state = ui_state
        self.layout = QtWidgets.QVBoxLayout(self)
        self.select_all_btn = QtWidgets.QPushButton("Select all nodes")
        self.generate_bash_script_btn = QtWidgets.QPushButton("Generate Bash Script")
        self.generate_python_script_btn = QtWidgets.QPushButton("Generate Python Script")
        self.save_session = QtWidgets.QPushButton("Save session (UI + NodeGraph)")
        self.load_session = QtWidgets.QPushButton("Load session (UI + NodeGraph)")
        self.refresh_session = QtWidgets.QPushButton("Refresh session (UI + NodeGraph)")

        self.layout.addWidget(self.select_all_btn)
        self.layout.addWidget(self.generate_bash_script_btn)
        self.layout.addWidget(self.generate_python_script_btn)
        self.layout.addWidget(self.save_session)
        self.layout.addWidget(self.load_session)
        self.layout.addWidget(self.refresh_session)

        self.setVisible(True)
        self.update()
        QtCore.QTimer.singleShot(100, self.repaint)

    def select_all_nodes(self):
        """Retrieves all nodes from the node graph.
        
        Returns:
            list: A list containing all nodes in the node graph.
        """
        all_nodes = self.node_graph.all_nodes()
        return all_nodes

    def _save_ui(self, save_path=None):
        """Saves the current UI state and NodeGraph session to a specified file.
        
        This method allows the user to save the current state of the UI and the NodeGraph session either to a user-defined path or through a file dialog. It serializes the session data, cleans up temporary properties, and writes the data to a JSON file.
        
        Args:
            save_path (str, optional): The path where the UI state and session should be saved. If not provided, a file dialog will be opened for the user to select a save location.
        
        Raises:
            Exception: If there is an error during the serialization of the session or while saving the file.
        """
        if save_path:
            path = pathlib.Path(save_path)
            logging.info("Refresh UI - Save")
        
        else:
            logging.info("Saving UI state + NodeGraph session...")

            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                parent=self,
                caption="Save session",
                directory=os.getcwd(),
                filter="JSON Files (*.json);;All Files (*)",
            )
            if not path:
                logging.warning("Could not save the session into a json file")
                return

            path = pathlib.Path(path)

        # 1) Save graph
        # Use serialize instead of save_session here because we need to modify the json
        try:
            # temporarily hide any transient menu to prevent NodeGraphQt error
            for node in self.node_graph.all_nodes():
                if "Add optional property" in node.properties().get("custom", {}):
                    node.set_property("Add optional property", None)
        except Exception:
            logging.warning("Failed to clean temporary Add_Props before serialize")
        
        # Safe serialization
        try:
            graph_data = self.node_graph.serialize_session()
        except Exception as e:
            logging.exception(f"Failed to serialize session safely: {e}")
            return
        
        for n in graph_data.get("nodes", {}).values():
            n.pop("accept_connection_types", None)
            n.pop("reject_connection_types", None)

        graph_data.get("graph", {}).pop("accept_connection_types", None)
        graph_data.get("graph", {}).pop("reject_connection_types", None)
        for n in graph_data.get("nodes", {}).values():
            n.pop("accept_connection_types", None)
            n.pop("reject_connection_types", None)

        # 2) Save UI state
        ui_data = self.ui_state.capture(self.window())

        # 3) Save custom_props in specific json key
        added_by_name = {}

        # 3.1) Collect optional props (by FLAG) present in custom
        for node in self.node_graph.all_nodes():
            optional_flags = set(getattr(node, "OPTIONAL_PROPS", {}).keys())
            custom_src = node.properties().get("custom", {})

            # We only move the optional flags present in custom
            moved = {k: v for k, v in custom_src.items() if k in optional_flags}
            if moved:
                added_by_name[node.name()] = moved

        # 3.2) Write add_custom and purge custom to avoid deserialize errors
        for node_dict in graph_data.get("nodes", {}).values():
            name = node_dict.get("name")
            moved = added_by_name.get(name)
            if not moved:

                # At least we purge the menu key is present
                custom_json = node_dict.setdefault("custom", {})
                custom_json.pop("Add optional property", None)
                custom_json.pop("Add optional property", None)
                continue

            node_dict["add_custom"] = moved

            custom_json = node_dict.setdefault("custom", {})
            # Delete the moved optional flags 
            for k in moved.keys():
                custom_json.pop(k, None)

            # Delete the additional property menu in the json
            custom_json.pop("Add optional property", None)
            custom_json.pop("Add optional property", None)

        bundle = {"graph": graph_data, "ui": ui_data}
        path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        logging.info("UI state saved at %s", path)

    def _load_ui(self, save_path=None):
        """Load the user interface (UI) state from a specified session file or prompt the user to select one.
        
        This method attempts to load the UI state and node graph session from a JSON file. If a save path is provided, it will load from that path; otherwise, it will open a file dialog for the user to select a session file. The method also restores any custom properties for nodes in the graph and updates the UI state accordingly.
        
        Args:
            save_path (str, optional): The path to the session file to load. If not provided, a file dialog will be opened.
        
        Raises:
            Exception: If there is an error during the loading process, including issues with deserializing the session or restoring UI state.
        
        Logging:
            Logs information about the loading process, warnings for missing nodes, and exceptions if any errors occur.
        """
        if save_path:
            path = pathlib.Path(save_path)
            logging.info("Refresh UI - Load")
        else:
            path_str, _ = QtWidgets.QFileDialog.getOpenFileName(
                parent=self,
                caption="Load session file",
                directory=os.getcwd(),
                filter="JSON Files (*.json);;All Files (*)",
            )
            if not path_str:
                logging.warning("Could not find session file to load")
                return
            path = pathlib.Path(path_str)
            logging.info(f"Loading UI state + NodeGraph session from: {path}")

        # Load json
        data = json.loads(path.read_text(encoding="utf-8"))
        graph_data = data.get("graph", {})

        # 1) Deserialize the node graph safely
        try:
            self.node_graph.deserialize_session(graph_data)
        except Exception:
            logging.exception("Failed to load UI session")
            return

        # 2) Restore optional properties stored in 'add_custom'
        for node_dict in graph_data.get("nodes", {}).values():
            node_name = node_dict.get("name")
            add_customs = node_dict.get("add_custom", {})

            if not add_customs:
                continue

            node = self.node_graph.get_node_by_name(node_name)
            if not node:
                logging.warning(f"Node '{node_name}' not found while loading add_custom")
                continue

            for flag, value in add_customs.items():
                try:
                    # Combine all possible props (BASE + OPTIONAL)
                    base = getattr(node, "BASE_PROPS", {})
                    opt = getattr(node, "OPTIONAL_PROPS", {})
                    all_props = {**base, **opt}  # flag -> (label, default)

                    # Retrieve label + default value
                    label, default_val = all_props.get(flag, (flag, ""))

                    # Create widget according to type
                    if isinstance(default_val, list):
                        node.add_combo_menu(name=flag, label=label, items=default_val)
                    else:
                        node.add_text_input(name=flag, label=label, text=value)

                    # Hide widget and reset Add optional property dropdown
                    node.hide_widget(name=flag, push_undo=False)
                    node.set_property("Add optional property", None)

                    logging.info(f"Restored custom property '{flag}' for node '{node_name}'")

                except Exception:
                    logging.exception(f"Failed to restore property '{flag}' on node '{node_name}'")

        # 3) Restore the UI layout and state
        try:
            self.ui_state.restore(self.parent(), data.get("ui", {}))
        except Exception:
            logging.exception("Failed to restore UI state")

        # 4) Bring the main window to focus
        main_window = self.window()
        main_window.showNormal()
        main_window.setWindowState(main_window.windowState() | QtCore.Qt.WindowMaximized)
        main_window.raise_()
        main_window.activateWindow()

        logging.info("UI state loaded successfully")

        # 5)  Force refresh ControlPanel layout
        try:
            self.setVisible(True)
            self.updateGeometry()
            self.repaint()
        except Exception:
            logging.exception("Failed to refresh ControlPanel UI after load")

    def _refresh_ui(self):
        """Refreshes the user interface by saving and loading the UI state.
        
        This method creates a temporary JSON file to store the current UI state, 
        saves the UI to this file, and then loads the UI from the file. The 
        temporary file is deleted after the operation.
        
        Args:
            None
        
        Returns:
            None
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            save_path = tmp.name
            self._save_ui(save_path=save_path)
            self._load_ui(save_path=save_path)
            os.remove(save_path)


    def generate_bash_script(self):
        """Generates a Bash script to run GROMACS commands.
        
        This method creates a Bash script named `run_gromacs.sh` that contains
        commands generated from the nodes in the node graph. The script is
        formatted for execution in a Bash environment.
        
        The generated script includes a shebang line and the commands are
        joined with double newlines for readability. Once the script is created,
        a message is printed to indicate the location of the generated file.
        
        Attributes:
            node_graph (NodeGraph): An object containing all nodes for command
            generation.
        
        Returns:
            None
        """
        script = []
        cmds = fill_cmd(nodes=self.node_graph.all_nodes())

        script.append("#!/bin/bash\n\n")
        script.append("\n\n".join(cmds))

        with open("run_gromacs.sh", "w") as f:
            f.write("".join(script))
            print(f"Bash script generated at {"run_gromacs.sh"}")


    def generate_python_script(self):
        """Generates a Python script to run GROMACS commands.
        
        This method creates a Python script named `run_gromacs.py` that includes
        the necessary commands to execute GROMACS simulations. The commands are
        generated based on the nodes in the node graph.
        
        The generated script imports the `subprocess` module and writes the
        commands to the file. After successfully creating the script, a message
        is printed to indicate the location of the generated file.
        
        Attributes:
            node_graph (NodeGraph): An object containing all nodes for command
            generation.
        
        Returns:
            None
        """
        script = []
        cmds = fill_cmd(nodes=self.node_graph.all_nodes())

        script.append("import subprocess\n\n")
        script.append("\n\n".join(cmds))

        with open("run_gromacs.py", "w") as f:
            f.write("".join(script))
            print(f"Python script generated at {"run_gromacs.py"}")




class GromacsPanel(QtWidgets.QWidget):
    """GromacsPanel is a QWidget that provides a user interface for running Gromacs commands on selected nodes in a node graph.
    
    Attributes:
        node_graph (NodeGraph): The graph containing nodes to be processed.
        process_runner (ProcessRunner): An instance responsible for executing commands.
        layout (QVBoxLayout): The layout manager for arranging widgets vertically.
        run_selected_nodes (QPushButton): Button to run the selected nodes.
        run_all (QPushButton): Button to run all nodes in the graph.
        stop_btn (QPushButton): Button to stop the currently running command.
        text (QPlainTextEdit): Text area for displaying command output and status messages.
    
    Methods:
        __init__(node_graph): Initializes the GromacsPanel with the given node graph.
        _update_preview(text): Updates the text area with the output of the command or a default message if no command is available.
    """
    def __init__(self, node_graph):
        super().__init__()
        self.node_graph = node_graph
        self.process_runner = ProcessRunner()
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.run_selected_nodes = QtWidgets.QPushButton("Run the selected nodes")
        self.run_all = QtWidgets.QPushButton("Run all nodes")
        self.stop_btn = QtWidgets.QPushButton("Stop the run")
        self.text = QtWidgets.QPlainTextEdit(readOnly=True)
        self.text.setPlainText("Waiting for a gromacs command to be executed...")
        self.text.setMinimumHeight(100)
        # No line wrap
        self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)


        self.layout.addWidget(self.run_selected_nodes)
        self.layout.addWidget(self.run_all)
        self.layout.addWidget(self.stop_btn)
        self.layout.addStretch(1)
        self.layout.addWidget(self.text)

        self.run_all.clicked.connect(lambda: self.process_runner.run(cmds=fill_cmd(nodes=node_graph.all_nodes())))
        self.stop_btn.clicked.connect(self.process_runner.stop)
        # self.run_selected_nodes.clicked.connect(self.process_runner._run_selected_nodes)
        # self.run_selected_nodes.clicked.connect(self.process_runner._run_all)
        # self.run_selected_nodes.clicked.connect(self.process_runner._stop_run)

        self.process_runner.command_started.connect(self._update_preview)
        self.process_runner.command_output.connect(self._update_preview)

    
    def _update_preview(self, text):
        """Updates the preview display with the given text.
        
        If the provided text is None or an empty string, it displays a default message.
        
        Args:
            text (str): The text to display in the preview. If None or empty, defaults to "No command to display".
        """
        # self.text.setPlainText(text or "No command to display")
        self.text.appendPlainText(text or "No command to display")