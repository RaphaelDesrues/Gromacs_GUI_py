# Check environment in a terminal + add to PATH
# Choose a working directory
# Add a check-up for all nodes and mandatory fields
# Add a preview
# Handle errors and crashes and managing for files

from genericpath import exists
import os, subprocess
import logging
from pathlib import Path

from Qt import QtCore # type: ignore


class ProcessRunner(QtCore.QObject):
    """Handle run shell commands and outputs via Qt signals"""


    command_started = QtCore.Signal(str)
    command_output = QtCore.Signal(str)
    # command_error = QtCore.Signal(str)


    def __init__(self, gmxlib=None):
        super().__init__()


        # Define gromacs env variables
        self._gmxrc = self._get_gmxrc()

        ## Optional: path to forcefield files
        gmxlib = "/home/rapha/2_Travail/test_GromacsGui/7PS8/FORCEFIELD"
        self._gmxlib = gmxlib or os.environ.get("GMXLIB")
        if self._gmxlib:
            os.environ["GMXLIB"] = self._gmxlib

        self.set_workdir("/home/rapha/2_Travail/test_GromacsGui/7PS8")

        self._process = QtCore.QProcess(self)
        self._process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)


    def set_workdir(self, path):
        if not path:
            return
        p = Path(path)
        if not exists(p) or not p.is_dir():
            logging.info("Directory not existing")
        self._workdir = str(p)


    def get_workdir(self) -> str:
        return self._workdir


    def is_running(self):
        return self._process.state() != QtCore.QProcess.NotRunning


    def run(self, cmds):
        # if not self._gmxrc:
        #     raise RuntimeError("No GMXRC found, cannot run gmx")

        if "GMXLIB" in os.environ:
            gmxlib_export = f"export GMXLIB='{os.environ['GMXLIB']}';"
        else:
            gmxlib_export = ""

        logging.info("gmxrc: %s\ngmxlib: %s", self._gmxrc, gmxlib_export)

        if self.is_running():
            logging.info("Already running")
            return

        # We store the cmds
        self._cmd_queue = list(cmds)

        # We execute the cmds sequentially
        self._start_next()


    def stop(self):
        if self._process.state() != QtCore.QProcess.NotRunning:
            self._process.kill()
        self._cmd_queue = []
        self.command_output.emit("Command stopped by user")


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

        if not gmxrc.exists() or not gmxrc.exists():
            logging.error("No GMXRC found at: %s", gmxrc)
            return None

        return gmxrc


    def _start_next(self):
        if not getattr(self, "_cmd_queue", None):
            logging.warning("No gromacs commands to run")
            return

        cmd = self._cmd_queue.pop(0)
        self.command_started.emit(f"Running: {cmd}")

        parts = [f"source '{self._gmxrc}'"]
        if self._gmxlib:
            parts.append(f"export GMXLIB='{self._gmxlib}'")

        parts.append(cmd)

        full_command = "; ".join(parts)

        self.command_output.emit(f"Directory: {self._workdir}")
        self.command_output.emit(f"Running {cmd}")

        self._process.setWorkingDirectory(self._workdir)
        self.command_output.emit(f"Directory2: {self._workdir}")
        self._process.start("/bin/bash", ["-lc", full_command])


    def _on_finished(self, exit_code, exit_status:QtCore.QProcess.ExitStatus):
        if exit_code != 0:
            self._cmd_queue = []
            return

        if getattr(self, "_cmd_queue", None):
            self._start_next()


    def _on_stdout(self):
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", "replace")
        if text:
            self.command_output.emit(text)


    def _on_stderr(self):
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", "replace")
        if text:
            self.command_output.emit(text)