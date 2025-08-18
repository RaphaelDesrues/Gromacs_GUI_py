# self.add_text_input(name="f_input_pdb", label="Input PDB", text="input.pdb")

from NodeGraphQt import BaseNode # type: ignore

# -----------------------------
# pdb2gmx
# -----------------------------
class Gromacspdb2gmx(BaseNode):
    __identifier__ = "pdb2gmx"
    NODE_NAME = "Prep (pdb2gmx)"

    # map: port_type -> property name
    IN_PORT  = {"pdb_file": "f_input_pdb"}
    OUT_PORT = {"gro_file": "f_output_gro",
                "top_file": "top"}

    def __init__(self):
        super().__init__()

        # Ports
        in_pdb = self.add_input("in_pdb");   in_pdb.port_type = "pdb_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        # Properties (widget-hidden on the node)
        self.add_text_input("f_input_pdb",  "Input PDB",       "input.pdb")
        self.add_text_input("f_output_gro", "Output GRO",      "init_conf.gro")
        self.add_text_input("top",          "Topology TOP",    "topol.top")
        self.add_text_input("forcefield",   "Forcefield",      "amber99sb")
        self.add_text_input("water_type",   "Water model",     "tip3p")

        self.hide_widget("f_input_pdb",  push_undo=False)
        self.hide_widget("f_output_gro", push_undo=False)
        self.hide_widget("top",          push_undo=False)
        self.hide_widget("forcefield",   push_undo=False)
        self.hide_widget("water_type",   push_undo=False)


# -----------------------------
# editconf
# -----------------------------
class Gromacseditconf(BaseNode):
    __identifier__ = "editconf"
    NODE_NAME = "Box (editconf)"

    IN_PORT  = {"gro_file": "f_input_gro"}
    OUT_PORT = {"gro_file": "f_output_gro"}

    def __init__(self):
        super().__init__()

        in_gro  = self.add_input("in_gro");   in_gro.port_type = "gro_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"

        self.add_text_input("f_input_gro",  "Input GRO",   "init_conf.gro")
        self.add_text_input("f_output_gro", "Output GRO",  "box.gro")
        self.add_text_input("box",          "Box Size",    "7")
        self.add_combo_menu("bt",           "Box Type",    ["cubic", "dodecahedron"])

        self.hide_widget("f_input_gro",  push_undo=False)
        self.hide_widget("f_output_gro", push_undo=False)
        self.hide_widget("box",          push_undo=False)
        self.hide_widget("bt",           push_undo=False)


# -----------------------------
# solvate
# -----------------------------
class Gromacssolvate(BaseNode):
    __identifier__ = "solvate"
    NODE_NAME = "Solvate (solvate)"

    IN_PORT  = {"gro_file": "f_input_gro", "top_file": "top"}
    OUT_PORT = {"gro_file": "f_output_gro", "top_file": "top"}

    def __init__(self):
        super().__init__()

        in_gro  = self.add_input("in_gro");  in_gro.port_type  = "gro_file"
        in_top  = self.add_input("in_top");  in_top.port_type  = "top_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        self.add_text_input("f_input_gro",  "Input GRO",      "box.gro")
        self.add_text_input("f_output_gro", "Output GRO",     "solv.gro")
        self.add_text_input("water_type",   "Water (cs)",     "spc216.gro")
        self.add_text_input("top",          "Topology TOP",   "topol.top")

        self.hide_widget("f_input_gro",  push_undo=False)
        self.hide_widget("f_output_gro", push_undo=False)
        self.hide_widget("water_type",   push_undo=False)
        self.hide_widget("top",          push_undo=False)


# # -----------------------------
# # grompp (generic: ions/em/nvt/npt/md)
# # -----------------------------
# class Gromacsgrompp(BaseNode):
#     __identifier__ = "grompp"
#     NODE_NAME = "Preprocess (grompp)"

#     IN_PORT  = {"gro_file": "f_input_gro",
#                 "top_file": "top",
#                 "mdp_file": "mdp"}
#     OUT_PORT = {"tpr_file": "f_output_tpr"}

#     def __init__(self):
#         super().__init__()

#         in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
#         in_top = self.add_input("in_top"); in_top.port_type = "top_file"
#         in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
#         out_tpr = self.add_output("out_tpr"); out_tpr.port_type = "tpr_file"

#         self.add_text_input("f_input_gro",  "Input GRO",    "solv.gro")
#         self.add_text_input("top",          "Topology TOP", "topol.top")
#         self.add_text_input("mdp",          "MDP file",     "em.mdp")
#         self.add_text_input("f_output_tpr", "Output TPR",   "em.tpr")
#         self.add_text_input("maxwarn",      "MaxWarn",      "1")

#         self.hide_widget("f_input_gro",  push_undo=False)
#         self.hide_widget("top",          push_undo=False)
#         self.hide_widget("mdp",          push_undo=False)
#         self.hide_widget("f_output_tpr", push_undo=False)
#         self.hide_widget("maxwarn",      push_undo=False)


# -----------------------------
# # mdrun (generic)
# # -----------------------------
# class Gromacsmdrun(BaseNode):
#     __identifier__ = "mdrun"
#     NODE_NAME = "Run (mdrun)"

#     IN_PORT  = {"tpr_file": "tpr"}
#     OUT_PORT = {"gro_file": "f_output_gro",
#                 "cpt_file": "f_output_cpt",
#                 "xtc_file": "f_output_xtc",
#                 "edr_file": "f_output_edr"}

#     def __init__(self):
#         super().__init__()

#         in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
#         out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
#         out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
#         out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
#         out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

#         self.add_text_input("tpr",           "Input TPR",  "em.tpr")
#         self.add_text_input("deffnm",        "Deffnm",     "em")
#         self.add_text_input("f_output_gro",  "Output GRO", "em.gro")
#         self.add_text_input("f_output_cpt",  "Output CPT", "em.cpt")
#         self.add_text_input("f_output_xtc",  "Output XTC", "em.xtc")
#         self.add_text_input("f_output_edr",  "Output EDR", "em.edr")

#         # GPU flags (text — à insérer si tu les utilises)
#         self.add_text_input("gpu_flags", "GPU opts", "-bonded gpu -nb gpu -pmefft gpu -pme gpu")

#         for k in ["tpr","deffnm","f_output_gro","f_output_cpt","f_output_xtc","f_output_edr","gpu_flags"]:
#             self.hide_widget(k, push_undo=False)

# -----------------------------
# genion (2 variantes possibles: neutral/conc, ou np/pname)
# -----------------------------
class Gromacsgenion(BaseNode):
    __identifier__ = "genion"
    NODE_NAME = "Ions (genion)"

    IN_PORT  = {"tpr_file": "tpr", "top_file": "top"}   # -s tpr, -p top
    OUT_PORT = {"gro_file": "f_output_gro", "top_file": "top"}

    def __init__(self):
        super().__init__()

        in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_top = self.add_output("out_top"); out_top.port_type = "top_file"

        self.add_text_input("tpr",          "Input TPR",     "solv.tpr")
        self.add_text_input("top",          "Topology TOP",  "topol.top")
        self.add_text_input("f_output_gro", "Output GRO",    "ions.gro")

        # mode “neutral + conc”
        self.add_text_input("pname", "Pos ion name", "K")
        self.add_text_input("nname", "Neg ion name", "CL")
        self.add_text_input("conc",  "Concentration", "0.15")
        self.add_text_input("group", "Select group", "SOL")  # à choisir au prompt

        # (optionnel) autre mode: nombre d’ions fixes
        self.add_text_input("np", "N+ ions (optional)", "")

        # hide
        for k in ["tpr","top","f_output_gro","pname","nname","conc","group","np"]:
            self.hide_widget(k, push_undo=False)


# =========================
# EM (grompp + mdrun)
# =========================
class GromacsEM(BaseNode):
    __identifier__ = "em"
    NODE_NAME = "Run EM"

    IN_PORT  = {"gro_file": "f_input_gro", "top_file": "top", "mdp_file": "mdp"}
    OUT_PORT = {"gro_file": "f_output_gro", "cpt_file": "f_output_cpt",
                "xtc_file": "f_output_xtc", "edr_file": "f_output_edr"}

    def __init__(self):
        super().__init__()
        # Ports
        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
        out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

        # Props (grompp)
        self.add_text_input("f_input_gro",  "Input GRO",    "solv.gro")
        self.add_text_input("top",          "Topology TOP", "topol.top")
        self.add_text_input("mdp",          "MDP file",     "em.mdp")
        self.add_text_input("f_output_tpr", "Output TPR",   "em.tpr")
        self.add_text_input("maxwarn",      "MaxWarn",      "1")

        # Props (mdrun)
        self.add_text_input("deffnm",       "Deffnm",       "em")
        self.add_text_input("f_output_gro", "Output GRO",   "em.gro")
        self.add_text_input("f_output_cpt", "Output CPT",   "em.cpt")
        self.add_text_input("f_output_xtc", "Output XTC",   "em.xtc")
        self.add_text_input("f_output_edr", "Output EDR",   "em.edr")
        self.add_text_input("gpu_flags",    "GPU opts",     "-bonded gpu -nb gpu -pmefft gpu -pme gpu")

        for k in ["f_input_gro","top","mdp","f_output_tpr","maxwarn",
                  "deffnm","f_output_gro","f_output_cpt","f_output_xtc","f_output_edr","gpu_flags"]:
            self.hide_widget(k, push_undo=False)


# =========================
# NVT (grompp + mdrun)
# =========================
class GromacsNVT(BaseNode):
    __identifier__ = "nvt"
    NODE_NAME = "Run NVT"

    IN_PORT  = {"gro_file": "f_input_gro", "top_file": "top", "mdp_file": "mdp"}
    OUT_PORT = {"gro_file": "f_output_gro", "cpt_file": "f_output_cpt",
                "xtc_file": "f_output_xtc", "edr_file": "f_output_edr"}

    def __init__(self):
        super().__init__()
        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
        out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

        self.add_text_input("f_input_gro",  "Input GRO",    "em.gro")
        self.add_text_input("top",          "Topology TOP", "topol.top")
        self.add_text_input("mdp",          "MDP file",     "nvt.mdp")
        self.add_text_input("f_output_tpr", "Output TPR",   "nvt.tpr")
        self.add_text_input("maxwarn",      "MaxWarn",      "1")

        self.add_text_input("deffnm",       "Deffnm",       "nvt")
        self.add_text_input("f_output_gro", "Output GRO",   "nvt.gro")
        self.add_text_input("f_output_cpt", "Output CPT",   "nvt.cpt")
        self.add_text_input("f_output_xtc", "Output XTC",   "nvt.xtc")
        self.add_text_input("f_output_edr", "Output EDR",   "nvt.edr")
        self.add_text_input("gpu_flags",    "GPU opts",     "-bonded gpu -nb gpu -pmefft gpu -pme gpu")

        for k in ["f_input_gro","top","mdp","f_output_tpr","maxwarn",
                  "deffnm","f_output_gro","f_output_cpt","f_output_xtc","f_output_edr","gpu_flags"]:
            self.hide_widget(k, push_undo=False)


# =========================
# NPT (grompp + mdrun)
# =========================
class GromacsNPT(BaseNode):
    __identifier__ = "npt"
    NODE_NAME = "Run NPT"

    IN_PORT  = {"gro_file": "f_input_gro", "top_file": "top", "mdp_file": "mdp"}
    OUT_PORT = {"gro_file": "f_output_gro", "cpt_file": "f_output_cpt",
                "xtc_file": "f_output_xtc", "edr_file": "f_output_edr"}

    def __init__(self):
        super().__init__()
        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
        out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

        self.add_text_input("f_input_gro",  "Input GRO",    "nvt.gro")
        self.add_text_input("top",          "Topology TOP", "topol.top")
        self.add_text_input("mdp",          "MDP file",     "npt.mdp")
        self.add_text_input("f_output_tpr", "Output TPR",   "npt.tpr")
        self.add_text_input("maxwarn",      "MaxWarn",      "1")

        self.add_text_input("deffnm",       "Deffnm",       "npt")
        self.add_text_input("f_output_gro", "Output GRO",   "npt.gro")
        self.add_text_input("f_output_cpt", "Output CPT",   "npt.cpt")
        self.add_text_input("f_output_xtc", "Output XTC",   "npt.xtc")
        self.add_text_input("f_output_edr", "Output EDR",   "npt.edr")
        self.add_text_input("gpu_flags",    "GPU opts",     "-bonded gpu -nb gpu -pmefft gpu -pme gpu")

        for k in ["f_input_gro","top","mdp","f_output_tpr","maxwarn",
                  "deffnm","f_output_gro","f_output_cpt","f_output_xtc","f_output_edr","gpu_flags"]:
            self.hide_widget(k, push_undo=False)


# =========================
# MD (grompp + mdrun)
# =========================
class GromacsMD(BaseNode):
    __identifier__ = "md"
    NODE_NAME = "Run MD"

    IN_PORT  = {"gro_file": "f_input_gro", "top_file": "top", "mdp_file": "mdp"}
    OUT_PORT = {"gro_file": "f_output_gro", "cpt_file": "f_output_cpt",
                "xtc_file": "f_output_xtc", "edr_file": "f_output_edr"}

    def __init__(self):
        super().__init__()
        in_gro = self.add_input("in_gro"); in_gro.port_type = "gro_file"
        in_top = self.add_input("in_top"); in_top.port_type = "top_file"
        in_mdp = self.add_input("in_mdp"); in_mdp.port_type = "mdp_file"
        out_gro = self.add_output("out_gro"); out_gro.port_type = "gro_file"
        out_cpt = self.add_output("out_cpt"); out_cpt.port_type = "cpt_file"
        out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"
        out_edr = self.add_output("out_edr"); out_edr.port_type = "edr_file"

        self.add_text_input("f_input_gro",  "Input GRO",    "npt.gro")
        self.add_text_input("top",          "Topology TOP", "topol.top")
        self.add_text_input("mdp",          "MDP file",     "md.mdp")
        self.add_text_input("f_output_tpr", "Output TPR",   "md.tpr")
        self.add_text_input("maxwarn",      "MaxWarn",      "1")

        self.add_text_input("deffnm",       "Deffnm",       "md")
        self.add_text_input("f_output_gro", "Output GRO",   "md.gro")
        self.add_text_input("f_output_cpt", "Output CPT",   "md.cpt")
        self.add_text_input("f_output_xtc", "Output XTC",   "md.xtc")
        self.add_text_input("f_output_edr", "Output EDR",   "md.edr")
        self.add_text_input("gpu_flags",    "GPU opts",     "-bonded gpu -nb gpu -pmefft gpu -pme gpu")

        for k in ["f_input_gro","top","mdp","f_output_tpr","maxwarn",
                  "deffnm","f_output_gro","f_output_cpt","f_output_xtc","f_output_edr","gpu_flags"]:
            self.hide_widget(k, push_undo=False)



# -----------------------------
# trjconv (post-prod)
# -----------------------------
# class Gromacstrjconv(BaseNode):
#     __identifier__ = "trjconv"
#     NODE_NAME = "Post (trjconv)"

#     IN_PORT  = {"tpr_file": "tpr", "xtc_file": "xtc"}
#     OUT_PORT = {"xtc_file": "f_output_xtc"}

#     def __init__(self):
#         super().__init__()

#         in_tpr = self.add_input("in_tpr"); in_tpr.port_type = "tpr_file"
#         in_xtc = self.add_input("in_xtc"); in_xtc.port_type = "xtc_file"
#         out_xtc = self.add_output("out_xtc"); out_xtc.port_type = "xtc_file"

#         self.add_text_input("tpr",           "Input TPR",     "md.tpr")
#         self.add_text_input("xtc",           "Input XTC",     "md.xtc")
#         self.add_text_input("f_output_xtc",  "Output XTC",    "md_noPBC.xtc")
#         self.add_text_input("ur",            "Unit-cell",     "compact")
#         self.add_text_input("center",        "Center",        "yes")
#         self.add_text_input("pbc",           "PBC",           "mol")

#         for k in ["tpr","xtc","f_output_xtc","ur","center","pbc"]:
#             self.hide_widget(k, push_undo=False)
