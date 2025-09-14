from Qt import QtWidgets # type: ignore
from app.export.workflow_exporter import map_props, MAPPING
import subprocess


class ControlPanel(QtWidgets.QWidget):

    def __init__(self, node_graph):
        super().__init__()
        self.node_graph = node_graph
        self.layout = QtWidgets.QVBoxLayout(self)
        self.select_one_btn = QtWidgets.QPushButton("Select the node")
        self.select_many_btn = QtWidgets.QPushButton("Select the selected nodes")
        self.select_all_btn = QtWidgets.QPushButton("Select all nodes")
        self.generate_bash_script_btn = QtWidgets.QPushButton("Generate Bash Script")
        self.generate_python_script_btn = QtWidgets.QPushButton("Generate Python Script")
        self.run_gromacs_ui = QtWidgets.QPushButton("Run GROMACS")

        self.layout.addWidget(self.select_one_btn)
        self.layout.addWidget(self.select_many_btn)
        self.layout.addWidget(self.select_all_btn)
        self.layout.addWidget(self.generate_bash_script_btn)
        self.layout.addWidget(self.generate_python_script_btn)
        self.layout.addWidget(self.run_gromacs_ui)


    # def selected_node(self):
    #     # Retrieve the class of the node
    #     print(self.node_graph.selected_nodes()[0].properties())
    #     return self.node_graph.selected_nodes()[0]
    #     selected_node = self.node_graph.selected_nodes()[0]
    #     print("One (First) node selected", type(selected_node))


    # def selected_nodes(self):
    #     selected_nodes = self.node_graph.selected_nodes()
    #     print("Many nodes selected", type(selected_nodes))
    #     return

    # def select_all_nodes(self):
    #     all_nodes = self.node_graph.all_nodes()
    #     print("All nodes selected", type(all_nodes))
    #     return all_nodes

    def gen_gro_cmd(self):
        # Retrieve the class of the selected node
        sel_node_cls = self.selected_node()

        # Retrieve the custom properties
        custom_props = sel_node_cls.properties().get('custom', {})

        # Retrieve the associated raw gromacs command
        raw_cmd  = MAPPING[sel_node_cls.__identifier__]

        # Map the raw command with the custom props
        gro_cmd = map_props(raw_cmd=raw_cmd, props=custom_props)
        print("GROMACS COMMAND: ", gro_cmd)
        # return gro_cmd


    def test_cmd(self):
        print("\n===== TEST_CMD =====")
        for node in self.node_graph.all_nodes():
            print(f"Node: {node.name()} (id={node.id})")
            # Propriétés custom
            for pname, pval in node.properties().get("custom", {}).items():
                print(f"  prop: {pname} = {pval}")

            # Ports d'entrée
            print("  inputs:")
            for port in node.input_ports():
                links = [f"{cp.node().name()}.{cp.name()}" for cp in port.connected_ports()]
                if links:
                    for l in links:
                        print(f"    {port.name()} <-- {l}")
                else:
                    print(f"    {port.name()} (no link)")

            # Ports de sortie
            print("  outputs:")
            for port in node.output_ports():
                links = [f"{cp.node().name()}.{cp.name()}" for cp in port.connected_ports()]
                if links:
                    for l in links:
                        print(f"    {port.name()} --> {l}")
                else:
                    print(f"    {port.name()} (no link)")
        print("====================\n")


    def fill_one_cmd(self, node):
        node_props = node.properties().get("custom", {})
        cmd_tmp = " ".join(f"{name} {value}" for name, value in node_props.items() if name != "Add_Props")
        return cmd_tmp


    def fill_all_cmd(self):

        cmds = []
        # Spatially organises the script as the node from left to right
        all_nodes = sorted(self.node_graph.all_nodes(), key=lambda n: n.pos()[0])

        for node in all_nodes:
            cmd_tmp = self.fill_one_cmd(node)
            cmds.append(" ".join(["gmx", node.__identifier__, cmd_tmp]))

        return cmds


    # def generate_bash_script(self):
    #     script = []
    #     cmds = self.fill_all_cmd()

    #     script.append("#!/bin/bash\n\n")
    #     script.append("\n\n".join(cmds))

    #     with open("run_gromacs.sh", "w") as f:
    #         f.write("".join(script))
    #         print(f"Bash script generated at {"run_gromacs.sh"}")


    # def generate_python_script(self):
    #     script = []
    #     cmds = self.fill_all_cmd()

    #     script.append("import subprocess\n\n")
    #     script.append("\n\n".join(cmds))

    #     with open("run_gromacs.py", "w") as f:
    #         f.write("".join(script))
    #         print(f"Python script generated at {"run_gromacs.py"}")


    # def run_gromacs_from_ui(self):
    #     for cmd in self.fill_all_cmd():
    #         print("RUN: ", cmd)
    #         subprocess.run(cmd.split(), check=True)



