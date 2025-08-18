# To map every gromacs node type to its gromacs command

MAPPING = {
    # --- Simple nodes ---
    "pdb2gmx": (
        "gmx pdb2gmx "
        "-f {f_input_pdb} "
        "-o {f_output_gro} "
        "-ff {forcefield} "
        "-water {water_type}"
    ),
    "editconf": (
        "gmx editconf "
        "-f {f_input_gro} "
        "-o {f_output_gro} "
        "-box {box} "
        "-bt {bt}"
    ),
    "solvate": (
        "gmx solvate "
        "-cp {f_input_gro} "
        "-o {f_output_gro} "
        "-cs {water_type} "
        "-p {top}"
    ),
    "genion": (
        "gmx genion "
        "-s {tpr} "
        "-o {f_output_gro} "
        "-p {top} "
        "-pname {pname} "
        "-nname {nname} "
        "-conc {conc} "
        "-neutral"
    ),

    # --- Stage nodes (grompp + mdrun) ---
    "em": [
        "gmx grompp -f {mdp} -c {f_input_gro} -p {top} -o {f_output_tpr} -maxwarn {maxwarn}",
        "gmx mdrun  -deffnm {deffnm} -v {gpu_flags}"
    ],
    "nvt": [
        "gmx grompp -f {mdp} -c {f_input_gro} -p {top} -o {f_output_tpr} -maxwarn {maxwarn}",
        "gmx mdrun  -deffnm {deffnm} -v {gpu_flags}"
    ],
    "npt": [
        "gmx grompp -f {mdp} -c {f_input_gro} -p {top} -o {f_output_tpr} -maxwarn {maxwarn}",
        "gmx mdrun  -deffnm {deffnm} -v {gpu_flags}"
    ],
    "md": [
        "gmx grompp -f {mdp} -c {f_input_gro} -p {top} -o {f_output_tpr} -maxwarn {maxwarn}",
        "gmx mdrun  -deffnm {deffnm} -v {gpu_flags}"
    ],
}


def map_props(raw_cmd, props):
    if isinstance(raw_cmd, (list, tuple)):
        return [cmd.format(**props) for cmd in raw_cmd]
    return raw_cmd.format(**props)




    
