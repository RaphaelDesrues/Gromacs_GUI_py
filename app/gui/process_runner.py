# Check environment in a terminal + add to PATH
# Choose a working directory
# Add a check-up for all nodes and mandatory fields
# Add a preview
# Handle errors and crashes and managing for files

import os, subprocess
import logging
from pathlib import Path

from Qt import QtCore # type: ignore


class ProcessRunner(QtCore.QObject):
    """Handle run shell commands and outputs via Qt signals"""


    command_started = QtCore.Signal(str)
    command_output = QtCore.Signal(str)
    command_error = QtCore.Signal(str)


    def __init__(self, gmxlib=None):
        super().__init__()


        # Define gromacs env variables
        self._gmxrc = self._get_gmxrc()
        
        ## Optional: path to forcefield files
        if gmxlib is not None:
            os.environ["GMXLIB"] = gmxlib
        else:
            self._gmxlib = gmxlib


    def _get_gmxrc(self):
        try:
            gmx_version = subprocess.run(["gmx", "--version"], capture_output=True, text=True)
        
        except Exception as e:
            logging.error(f"Impossible to execute 'gmx --version': {e}")
        
        try:
            lines = gmx_version.stdout.splitlines()
            gmxrc = None
            for line in lines:
                if line.startswith("Data prefix:"):
                    prefix = line.split(":", 1)[1].strip()
                    gmxrc = Path(prefix) / "bin" / "GMXRC"
                    break
        except:
            logging.error("No 'Data prefix' found")
        
        if not gmxrc.exists():
            logging.error("No GMXRC found at: %s", gmxrc)

        return gmxrc


    def run(self, cmds):
        if not self.gmxrc:
            raise RuntimeError("No GMXRC found, cannot run gmx")
        
        if "GMXLIB" in os.environ:
            gmxlib_export = f"export GMXLIB={os.environ["GMXLIB"]};"
        else:
            gmxlib_export = ""

        logging.info("gmxrc: %s\ngmxlib: %s", self.gmxrc, gmxlib_export)

        for cmd in cmds:
            cmd = f"source '{self.gmxrc}'; {gmxlib_export} {cmd}"
            # subprocess.run(cmd, shell=True)


