from app.assets.my_prop_bin import MyBaseNode


"""
BaseNode is a general-purpose node structure used to represent a single computational or
configuration step in a modular workflow.

Each node exposes configurable parameters, optional arguments, and connection ports that
define how data and properties flow through the workflow graph. The node’s interface is
automatically built from predefined dictionaries describing these elements.

Attributes:
    BASE_PROPS (dict): 
        Defines the mandatory parameters of the node.
        Each entry maps a command-line flag to a tuple of (label, default_value or list of options).

    OPTIONAL_PROPS (dict): 
        Defines secondary, user-selectable parameters.
        These can be dynamically added through the GUI via a dropdown menu.

    IN_PORTS (dict): 
        Maps input connection flags to port metadata in the form (port_name, port_type, [linked_outputs]).
        Used for data propagation between connected nodes.

    OUT_PORTS (dict): 
        Maps output connection flags to port metadata (port_name, port_type).
        Determines which properties can be sent to downstream nodes.

    __identifier__ (str): 
        Internal namespace identifier used by the node factory to register and restore nodes.

    NODE_NAME (str): 
        Human-readable name displayed in the GUI for this node.

Methods:
    __init__():
        Initializes the node, registers all base ports and properties, and prepares optional
        property menus for dynamic configuration.

    add_text_input(name, label, text):
        Creates a text-based property widget associated with the given flag and label.

    add_combo_menu(name, label, items):
        Creates a dropdown menu property widget for selecting among multiple options.

    hide_widget(name, push_undo=False):
        Hides a property widget from the GUI while keeping its state accessible programmatically.

    set_property(name, value):
        Updates the node’s property value and synchronizes it with the GUI widget.

    get_property(name):
        Retrieves the current value of a property.

"""  


class Pdb2gmx(MyBaseNode):
    __identifier__ = "pdb2gmx"
    NODE_NAME = "Prep (pdb2gmx)"

    BASE_PROPS = {
        "-f": ("Input structure (PDB/GRO)", "input.pdb"),
        "-o": ("Output structure (GRO)", "init_conf.gro"),
        "-p": ("Topology (TOP)", "topol.top"),
        "-i": ("Posre file (ITP)", "posre.itp"),
        "-ff": ("Forcefield", "amber99sb"),
        "-water": ("Water model", ["tip3p", "spce", "tip4p", "tip4pew", "tip4p2005"]),
        "-ignh": ("Ignore H from input", ["no", "yes"]),
    }
    OPTIONAL_PROPS = {
        "-ter": ("Terminal selection (-ter)", ""),
        "-his": ("Histidine tautomers (-his)", ""),
        "-asp": ("Asp/Glu protonation (-asp/-glu)", ""),
        "-lys": ("Lys/Arg protonation (-lys/-arg)", ""),
        "-missing": ("Missing atoms (-missing)", ""),
        "-heavyh": ("No H-bond constraints (-heavyh)", ""),
    }
    IN_PORTS = {}
    OUT_PORTS = {
        "-o": ("out_gro", "gro_file"),
        "-p": ("out_top", "top_file"),
    }

    def __init__(self):
        super().__init__()


class Editconf(MyBaseNode):
    __identifier__ = "editconf"
    NODE_NAME = "Box (editconf)"

    BASE_PROPS = {
        "-f": ("Input (GRO)", "init_conf.gro"),
        "-o": ("Output (GRO)", "box.gro"),
        "-bt": ("Box type", ["cubic", "triclinic", "dodecahedron", "octahedron"]),
        "-box": ("Box size (nm, 1/2/3 vals)", "7"),
        "-d": ("Solvent shell (nm)", "1.0"),
        "-c": ("Center molecule", ["no", "yes"]),
    }
    OPTIONAL_PROPS = {
        "-princ": ("Align to principal axes (-princ)", ""),
        "-scale": ("Scale box (-scale)", "1 1 1"),
        "-rotate": ("Rotate (deg) (-rotate)", "0 0 0"),
        "-translate": ("Translate (nm) (-translate)", "0 0 0"),
        "-density": ("Density (g/L) (-density)", ""),
        "-n": ("Index File (-n)", ""),
    }
    IN_PORTS = { "-f": ("in_gro", "gro_file", ["out_gro"]) }
    OUT_PORTS = { "-o": ("out_gro", "gro_file") }

    def __init__(self):
        super().__init__()


class Solvate(MyBaseNode):
    __identifier__ = "solvate"
    NODE_NAME = "Solvate (solvate)"

    BASE_PROPS = {
        "-cp": ("Input config (GRO)", "box.gro"),
        "-o": ("Output (GRO)", "solv.gro"),
        "-p": ("Topology (TOP)", "topol.top"),
    }
    OPTIONAL_PROPS = {
        "-scale": ("Scale solvent box (-scale)", "1 1 1"),
        "-box": ("Explicit box size (-box)", ""),
        "-radius": ("Solvent radius (nm) (-radius)", ""),
        "-shell": ("Try to keep solute (-shell)", ""),
    }
    IN_PORTS = {
        "-cp": ("in_gro", "gro_file", ["out_gro"]),
        "-p":  ("in_top", "top_file", ["out_top"]),
    }
    OUT_PORTS = {
        "-o": ("out_gro", "gro_file"),
        "-p": ("out_top", "top_file"),
    }

    def __init__(self):
        super().__init__()


class Genion(MyBaseNode):
    __identifier__ = "genion"
    NODE_NAME = "Ions (genion)"

    BASE_PROPS = {
        "-s": ("Input (TPR)", "solv.tpr"),
        "-p": ("Topology (TOP)", "topol.top"),
        "-o": ("Output (GRO)", "ions.gro"),
        "-neutral": ("Neutralize system", ["no", "yes"]),
        "-conc": ("Salt conc (mol/L)", "0.15"),
        "-pname": ("Positive ion name", "NA"),
        "-nname": ("Negative ion name", "CL"),
        "group": ("Group to replace (interactive)", "SOL"),
    }
    OPTIONAL_PROPS = {
        "-np": ("Fixed N+ ions (-np)", ""),
        "-nn": ("Fixed N- ions (-nn)", ""),
        "-seed": ("Seed (-seed)", ""),
        "-n": ("Index file (-n)", ""),
    }
    IN_PORTS = {
        "-s": ("in_tpr", "tpr_file", ["out_tpr", "out_gro"]),
        "-p": ("in_top", "top_file", ["out_top"]),
    }
    OUT_PORTS = {
        "-o": ("out_gro", "gro_file"),
        "-p": ("out_top", "top_file"),
    }

    def __init__(self):
        super().__init__()


class Grompp(MyBaseNode):
    __identifier__ = "grompp"
    NODE_NAME = "Preprocess (grompp)"

    BASE_PROPS = {
        "-f": ("MDP file", "em.mdp"),
        "-c": ("Input structure (GRO)", "solv.gro"),
        "-p": ("Topology (TOP)", "topol.top"),
        "-o": ("Output (TPR)", "em.tpr"),
        "-maxwarn": ("Max warn", "1"),
    }
    OPTIONAL_PROPS = {
        "-D": ("Define (e.g. -DPOSRES)", ""),
        "-n": ("Index file (-n)", ""),
        "-r": ("Reref conf (-r)", ""),
        "-table": ("Energy groups table (-table)", ""),
    }
    IN_PORTS = {
        "-c": ("in_gro", "gro_file", ["out_gro"]),
        "-p": ("in_top", "top_file", ["out_top"]),
    }
    OUT_PORTS = {
        "-o": ("out_tpr", "tpr_file"),
    }

    def __init__(self):
        super().__init__()


class Mdrun(MyBaseNode):
    __identifier__ = "mdrun"
    NODE_NAME = "Run (mdrun)"

    BASE_PROPS = {
        "-s": ("Input (TPR)", "em.tpr"),
        "-deffnm": ("Deffnm", "em"),
        "out_gro": ("Output GRO", "em.gro"),
        "out_cpt": ("Output CPT", "em.cpt"),
        "out_xtc": ("Output XTC", "em.xtc"),
        "out_edr": ("Output EDR", "em.edr"),
        "gpu_flags": ("GPU opts", "-bonded gpu -nb gpu -pmefft gpu -pme gpu"),
    }
    OPTIONAL_PROPS = {
        "-nt": ("Threads (-nt)", ""),
        "-pin": ("Pin strategy (-pin)", ""),
        "-maxh": ("Maxh (-maxh)", ""),
        "-rcon": ("Restrain groups (-rcon)", ""),
    }
    IN_PORTS = { "-s": ("in_tpr", "tpr_file", ["out_tpr"]) }
    OUT_PORTS = {
        "-o": ("out_gro", "gro_file"),
        "-cp": ("out_cpt", "cpt_file"),
        "-p": ("out_xtc", "xtc_file"),
        "-f": ("out_edr", "edr_file"),
    }

    def __init__(self):
        super().__init__()


class Trjconv(MyBaseNode):
    __identifier__ = "trjconv"
    NODE_NAME = "Post (trjconv)"

    BASE_PROPS = {
        "-s": ("Input (TPR)", "md.tpr"),
        "-f": ("Input (XTC/TRAJ)", "md.xtc"),
        "-o": ("Output trajectory", "md_noPBC.xtc"),
        "-pbc": ("PBC", ["no", "mol", "res", "atom"]),
        "-center": ("Center", ["no", "yes"]),
        "-ur": ("Unit-cell", ["rect", "tric", "compact"]),
    }
    OPTIONAL_PROPS = {
        "-skip": ("Skip frames (-skip)", ""),
        "-dt": ("Dt output ps (-dt)", ""),
        "-fit": ("Fit selection (-fit)", ""),
        "-n": ("Index file (-n)", ""),
    }
    IN_PORTS = {
        "-s": ("in_tpr", "tpr_file", ["out_tpr"]),
        "-f": ("in_xtc", "xtc_file", ["out_xtc"]),
    }
    OUT_PORTS = { "-o": ("out_xtc", "xtc_file") }

    def __init__(self):
        super().__init__()
