from typing import ReadOnly
from Qt import QtWidgets # type: ignore
from app.export.workflow_exporter import map_props, MAPPING
import subprocess
from app.gui.process_runner import ProcessRunner


def fill_one_cmd(node):
    node_props = node.properties().get("custom", {})
    cmd_tmp = " ".join(f"{name} {value}" for name, value in node_props.items() if name != "Add_Props")
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


# def gen_gro_cmd(self):
#     # Retrieve the class of the selected node
#     sel_node_cls = self.selected_node()

#     # Retrieve the custom properties
#     custom_props = sel_node_cls.properties().get('custom', {})

#     # Retrieve the associated raw gromacs command
#     raw_cmd  = MAPPING[sel_node_cls.__identifier__]

#     # Map the raw command with the custom props
#     gro_cmd = map_props(raw_cmd=raw_cmd, props=custom_props)
#     print("GROMACS COMMAND: ", gro_cmd)
#     # return gro_cmd



# def test_cmd(self):
#     print("\n===== TEST_CMD =====")
#     for node in self.node_graph.all_nodes():
#         print(f"Node: {node.name()} (id={node.id})")
#         # Propriétés custom
#         for pname, pval in node.properties().get("custom", {}).items():
#             print(f"  prop: {pname} = {pval}")

#         # Ports d'entrée
#         print("  inputs:")
#         for port in node.input_ports():
#             links = [f"{cp.node().name()}.{cp.name()}" for cp in port.connected_ports()]
#             if links:
#                 for l in links:
#                     print(f"    {port.name()} <-- {l}")
#             else:
#                 print(f"    {port.name()} (no link)")

#         # Ports de sortie
#         print("  outputs:")
#         for port in node.output_ports():
#             links = [f"{cp.node().name()}.{cp.name()}" for cp in port.connected_ports()]
#             if links:
#                 for l in links:
#                     print(f"    {port.name()} --> {l}")
#             else:
#                 print(f"    {port.name()} (no link)")
#     print("====================\n")



class ControlPanel(QtWidgets.QWidget):

    def __init__(self, node_graph):
        super().__init__()
        self.node_graph = node_graph
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

    def select_all_nodes(self):
        all_nodes = self.node_graph.all_nodes()
        return all_nodes


    def generate_bash_script(self):
        script = []
        cmds = fill_cmd(nodes=self.node_graph.all_nodes())

        script.append("#!/bin/bash\n\n")
        script.append("\n\n".join(cmds))

        with open("run_gromacs.sh", "w") as f:
            f.write("".join(script))
            print(f"Bash script generated at {"run_gromacs.sh"}")


    def generate_python_script(self):
        script = []
        cmds = fill_cmd(nodes=self.node_graph.all_nodes())

        script.append("import subprocess\n\n")
        script.append("\n\n".join(cmds))

        with open("run_gromacs.py", "w") as f:
            f.write("".join(script))
            print(f"Python script generated at {"run_gromacs.py"}")


class GromacsPanel(QtWidgets.QWidget):

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
        # self.text.setPlainText(text or "No command to display")
        self.text.appendPlainText(text or "No command to display")