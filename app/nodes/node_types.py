# self.add_text_input(name="f_input_pdb", label="Input PDB", text="input.pdb")

from itertools import product
from app.assets.my_prop_bin import MyBaseNode


# -----------------------------
# Custom PortTypes + accepts
# -----------------------------
class AcceptsMixin:
    """
    Allow connecting any declared port name to compatible node types
    """

    ALL_NODES_TYPE = [
        "pdb2gmx.Gromacspdb2gmx",
        "editconf.Gromacseditconf",
        "solvate.Gromacssolvate",
        "genion.Gromacsgenion",
        "grompp.Gromacsgrompp",
        "mdrun.Gromacsmdrun"
    ]

    PORT_TYPES = ["in", "out"]  # we mostly use outputs in theory

    def manage_accepts(self, ACCEPTS, NAME_TO_PORT):
        for in_name, out_names in ACCEPTS.items():
            in_port = NAME_TO_PORT[in_name]
            if isinstance(out_names, str):
                out_names = [out_names]
            for port_name, port_type, node_type in product(out_names, self.PORT_TYPES, self.ALL_NODES_TYPE):
                self.add_accept_port_type(
                    in_port,
                    dict(
                        port_name=port_name,
                        port_type=port_type,
                        node_type=node_type
                    ),
                )



    def hide_all_props(self):
        [
            self.hide_widget(k, push_undo=False)
            for k in self.properties().get("custom", {}).keys()
            if k != "Add_Props"
        ]



# =============================
# pdb2gmx
# =============================
class Gromacspdb2gmx(MyBaseNode, AcceptsMixin):
    __identifier__ = "pdb2gmx"
    NODE_NAME = "Prep (pdb2gmx)"

    # Additional properties
    PREDEFINED_PROPS = {
                "Terminal selection (-ter)": ("-ter", ""),
                "Histidine tautomers (-his)": ("-his", ""),
                "Asp/Glu protonation (-asp/-glu)": ("-asp", ""),
                "Lys/Arg protonation (-lys/-arg)": ("-lys", ""),
                "Missing atoms (-missing)": ("-missing", ""),
                "No H-bond constraints (-heavyh)": ("-heavyh", "")
    }

    OUT_PORT = {"gro_file": "-o",
                "top_file": "-p"}

    def __init__(self):
        super().__init__()

        # Outputs only
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        # Most-used flags as visible widgets
        self.add_text_input(name="-f", label="Input structure (PDB/GRO)", text="input.pdb")
        self.add_text_input(name="-o", label="Output structure (GRO)", text="init_conf.gro")
        self.add_text_input(name="-p", label="Topology (TOP)", text="topol.top")
        self.add_text_input(name="-i", label="Posre file (ITP)", text="posre.itp")
        self.add_text_input(name="-ff", label="Forcefield", text="amber99sb")
        self.add_combo_menu(name="-water", label="Water model", items=["tip3p", "spce", "tip4p", "tip4pew", "tip4p2005"])
        self.add_combo_menu(name="-ignh", label="Ignore H from input", items=["no", "yes"])

        self.hide_all_props()

# =============================
# editconf
# =============================
class Gromacseditconf(MyBaseNode, AcceptsMixin):
    __identifier__ = "editconf"
    NODE_NAME = "Box (editconf)"

    ACCEPTS = {
        "in_gro": "out_gro"
    }

    PREDEFINED_PROPS = {
        "Align to principal axes (-princ)": ("-princ", ""),
        "Scale box (-scale)": ("-scale", "1 1 1"),
        "Rotate (deg) (-rotate)": ("-rotate", "0 0 0"),
        "Translate (nm) (-translate)": ("-translate", "0 0 0"),
        "Density (g/L) (-density)": ("-density", ""),
        "Index File (-n)": ("-n", "")
    }

    IN_PORT = {"gro_file": "-f"}
    OUT_PORT = {"gro_file": "-o"}

    def __init__(self):
        super().__init__()

        in_gro  = self.add_input("in_gro");   in_gro.port_type = "gro_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"

        self.add_text_input(name="-f", label="Input (GRO)", text="init_conf.gro")
        self.add_text_input(name="-o", label="Output (GRO)", text="box.gro")
        self.add_combo_menu(name="-bt", label="Box type", items=["cubic", "triclinic", "dodecahedron", "octahedron"])
        self.add_text_input(name="-box", label="Box size (nm, 1/2/3 vals)", text="7")
        self.add_text_input(name="-d", label="Solvent shell (nm)", text="1.0")
        self.add_combo_menu(name="-c", label="Center molecule", items=["no", "yes"])

        self.hide_all_props()

        NAME_TO_PORT = {"in_gro": in_gro}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)


# =============================
# solvate
# =============================
class Gromacssolvate(MyBaseNode, AcceptsMixin):
    __identifier__ = "solvate"
    NODE_NAME = "Solvate (solvate)"

    ACCEPTS = {"in_gro": "out_gro",
               "in_top": "out_top"
    }

    PREDEFINED_PROPS = {
            "Scale solvent box (-scale)": ("-scale", "1 1 1"),
            "Explicit box size (-box)": ("-box", ""),
            "Solvent radius nm (-radius)": ("-radius", ""),
            "Try to keep solute (-shell)": ("-shell", "")
    }

    IN_PORT = {"gro_file": "-f",
               "top_file": "-p"}
    OUT_PORT = {"gro_file": "-o",
                "top_file": "-p"}

    def __init__(self):
        super().__init__()

        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        # Common flags
        self.add_text_input(name="-cp", label="Input config (GRO)", text="box.gro")
        self.add_text_input(name="-cs", label="Solvent config", text="spc216.gro")
        self.add_text_input(name="-o", label="Output (GRO)", text="solv.gro")
        self.add_text_input(name="-p", label="Topology (TOP)", text="topol.top")

        self.hide_all_props()

        NAME_TO_PORT = {"in_gro": in_gro, "in_top": in_top}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)


# =============================
# genion
# =============================
class Gromacsgenion(MyBaseNode, AcceptsMixin):
    __identifier__ = "genion"
    NODE_NAME = "Ions (genion)"

    ACCEPTS = {"in_tpr": "out_gro",
               "in_top": "out_top"
    }

    PREDEFINED_PROPS = {
            "Fixed N+ ions (-np)": ("-np", ""),
            "Fixed N- ions (-nn)": ("-nn", ""),
            "Seed (-seed)": ("-seed", ""),
            "Index file (-n)": ("-n", ""),
    }

    IN_PORT = {"trp_file": "-s",
               "top_file": "-p"}
    OUT_PORT = {"gro_file": "-o",
                "top_file": "-p"}

    def __init__(self):
        super().__init__()

        in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        # Common workflow (neutralize to given salt conc)
        self.add_text_input(name="-s", label="Input (TPR)", text="solv.tpr")
        self.add_text_input(name="-p", label="Topology (TOP)", text="topol.top")
        self.add_text_input(name="-o", label="Output (GRO)", text="ions.gro")
        self.add_combo_menu(name="-neutral", label="Neutralize system", items=["no", "yes"])  # boolean
        self.add_text_input(name="-conc", label="Salt conc (mol/L)", text="0.15")
        self.add_text_input(name="-pname", label="Positive ion name", text="NA")
        self.add_text_input(name="-nname", label="Negative ion name", text="CL")
        self.add_text_input(name="group", label="Group to replace (interactive)", text="SOL")

        self.hide_all_props()

        NAME_TO_PORT = {"in_tpr": in_tpr, "in_top": in_top}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)


# =============================
# grompp
# =============================
class Gromacsgrompp(MyBaseNode, AcceptsMixin):
    __identifier__ = "grompp"
    NODE_NAME = "Preprocess (grompp)"

    ACCEPTS = {"in_gro": "out_gro",
               "in_top": "out_top",
               "in_mdp": "in_mdp"
    }

    PREDEFINED_PROPS = {
            "Define (e.g. -DPOSRES) (-D)": ("-D", ""),
            "Index file (-n)": ("-n", ""),
            "Reref conf (-r)": ("-r", ""),
            "Energy groups table (-table)": ("-table", "")
    }

    IN_PORT = {"gro_file": "-c",
               "top_file": "-p",
               "mdp_file": "-f"}
    OUT_PORT = {"tpr_file": "-o"}

    def __init__(self):
        super().__init__()

        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
        out_tpr = self.add_output("out_tpr"); out_tpr.port_type = "tpr_file"

        self.add_text_input(name="-f", label="MDP file", text="em.mdp")
        self.add_text_input(name="-c", label="Input structure (GRO)", text="solv.gro")
        self.add_text_input(name="-p", label="Topology (TOP)", text="topol.top")
        self.add_text_input(name="-o", label="Output (TPR)", text="em.tpr")
        self.add_text_input(name="-maxwarn", label="Max warn", text="1")

        self.hide_all_props()

        NAME_TO_PORT = {"in_gro": in_gro, "in_top": in_top, "in_mdp": in_mdp}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)



# =============================
# mdrun
# =============================
class Gromacsmdrun(MyBaseNode, AcceptsMixin):
    __identifier__ = "mdrun"
    NODE_NAME = "Run (mdrun)"

    ACCEPTS = {"in_tpr": ["out_gro", "out_tpr"]}

    PREDEFINED_PROPS = {
            "Threads (-nt)": ("-nt", ""),
            "Pin strategy (-pin)": ("-pin", ""),
            "Maxh (-maxh)": ("-maxh", ""),
            "Restrain groups (-rcon)": ("-rcon", ""),
    }

    IN_PORT = {"gro_file": "-s"}
    OUT_PORT = {"gro_file": "-o",
                "cpt_file": "-cp",
                "xtc_file": "-p",
                "top_file": "-f"}

    def __init__(self):
        super().__init__()

        in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
        out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

        self.add_text_input(name="-s", label="Input (TPR)", text="em.tpr")
        self.add_text_input(name="-deffnm", label="Deffnm", text="em")
        self.add_text_input(name="out_gro", label="Output GRO", text="em.gro")
        self.add_text_input(name="out_cpt", label="Output CPT", text="em.cpt")
        self.add_text_input(name="out_xtc", label="Output XTC", text="em.xtc")
        self.add_text_input(name="out_edr", label="Output EDR", text="em.edr")
        self.add_text_input(name="gpu_flags", label="GPU opts", text="-bonded gpu -nb gpu -pmefft gpu -pme gpu")

        self.hide_all_props()

        NAME_TO_PORT = {"in_tpr": in_tpr}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)


# =============================
# trjconv
# =============================
class Gromacstrjconv(MyBaseNode, AcceptsMixin):
    __identifier__ = "trjconv"
    NODE_NAME = "Post (trjconv)"

    ACCEPTS = {"in_tpr": "out_gro",
               "in_xtc": "out_xtc"
    }

    PREDEFINED_PROPS = {
            "Skip frames (-skip)": ("-skip", ""),
            "Dt output ps (-dt)": ("-dt", ""),
            "Fit selection (-fit)": ("-fit", ""),
            "Index file (-n)": ("-n", ""),
    }

    def __init__(self):
        super().__init__()

        in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
        in_xtc = self.add_input("in_xtc"); in_xtc.port_type = "xtc_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"

        self.add_text_input(name="-s", label="Input (TPR)", text="md.tpr")
        self.add_text_input(name="-f", label="Input (XTC/TRAJ)", text="md.xtc")
        self.add_text_input(name="-o", label="Output trajectory", text="md_noPBC.xtc")
        self.add_combo_menu(name="-pbc", label="PBC", items=["no", "mol", "res", "atom"])
        self.add_combo_menu(name="-center", label="Center", items=["no", "yes"]) 
        self.add_combo_menu(name="-ur", label="Unit-cell", items=["rect", "tric", "compact"]) 

        self.hide_all_props()

        NAME_TO_PORT = {"in_tpr": in_tpr, "in_xtc": in_xtc}
        self.manage_accepts(self.ACCEPTS, NAME_TO_PORT)