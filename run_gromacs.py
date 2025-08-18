import subprocess

gmx pdb2gmx -f input.pdb -o init_conf.gro -ff amber99sb -water tip3p

gmx editconf -f init_conf.gro -o box.gro -box 7 -bt cubic

gmx solvate -cp box.gro -o solv.gro -cs spc216.gro -p topol.top

gmx genion -s solv.gro -o ions.gro -p topol.top -pname K -nname CL -conc 0.15 -neutral

gmx grompp -f em.mdp -c ions.gro -p topol.top -o em.tpr -maxwarn 1

gmx mdrun  -deffnm em -v -bonded gpu -nb gpu -pmefft gpu -pme gpu

gmx grompp -f nvt.mdp -c em.gro -p em.cpt -o nvt.tpr -maxwarn 1

gmx mdrun  -deffnm nvt -v -bonded gpu -nb gpu -pmefft gpu -pme gpu

gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -maxwarn 1

gmx mdrun  -deffnm npt -v -bonded gpu -nb gpu -pmefft gpu -pme gpu

gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -maxwarn 1

gmx mdrun  -deffnm md -v -bonded gpu -nb gpu -pmefft gpu -pme gpu