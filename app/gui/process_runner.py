from genericpath import exists
import os, subprocess
import logging
from pathlib import Path

from Qt import QtCore # type: ignore


class ProcessRunner(QtCore.QObject):
    """ProcessRunner is a class that manages the execution of Gromacs commands in a separate process.
    
    This class inherits from `QtCore.QObject` and utilizes Qt's signal and slot mechanism to communicate the status and output of the commands being executed. It sets up the necessary environment variables and handles the command queue for sequential execution of commands.
    
    Attributes:
        command_started (QtCore.Signal): Emitted when a command starts executing.
        command_output (QtCore.Signal): Emitted when there is output from the command.
    
    Methods:
        __init__(gmxlib=None):
            Initializes the ProcessRunner, sets up the environment, and prepares the process for command execution.
    
        set_workdir(path):
            Sets the working directory for the process.
    
        get_workdir() -> str:
            Returns the current working directory.
    
        is_running() -> bool:
            Checks if the process is currently running.
    
        run(cmds):
            Starts executing a list of commands.
    
        stop():
            Stops the currently running command.
    
        _get_gmxrc() -> Path:
            Retrieves the path to the GMXRC file based on the Gromacs installation.
    
        _start_next():
            Starts the next command in the queue.
    
        _on_finished(exit_code, exit_status):
            Handles the completion of a command execution.
    
        _on_stdout():
            Processes standard output from the command.
    
        _on_stderr():
            Processes standard error output from the command.
    """
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
        """Sets the working directory to the specified path.
        
        This method updates the instance's working directory if the provided path is valid. 
        If the path is empty or does not point to an existing directory, the method will log 
        an informational message and will not change the working directory.
        
        Args:
            path (str): The path to the directory to set as the working directory. 
                         If the path is empty or invalid, the working directory will not be changed.
        
        Returns:
            None
        """
        if not path:
            return
        p = Path(path)
        if not exists(p) or not p.is_dir():
            logging.info("Directory not existing")
        self._workdir = str(p)

    def get_workdir(self) -> str:
        """Returns the current working directory.
        
        This method retrieves the value of the instance variable `_workdir`, which represents
        the directory where the current work is being performed.
        
        Returns:
            str: The current working directory as a string.
        """
        return self._workdir


    def is_running(self):
        """Determines if the associated process is currently running.
        
        Returns:
            bool: True if the process is running, False if it is not.
        """
        return self._process.state() != QtCore.QProcess.NotRunning

    def run(self, cmds):
        """Runs a series of commands in the context of the GROMACS environment.
        
        This method checks for the presence of the GMXLIB environment variable and logs the current gmxrc and gmxlib settings. If the process is already running, it logs an informational message and exits. Otherwise, it initializes the command queue with the provided commands and starts executing them.
        
        Args:
            cmds (list): A list of commands to be executed.
        
        Raises:
            None: This method does not raise any exceptions.
        """
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
        """Stops the currently running process if it is active.
        
        This method checks the state of the process and kills it if it is not already running. 
        It also clears the command queue and emits a signal indicating that the command has been stopped by the user.
        
        Attributes:
            _process (QProcess): The process to be managed.
            _cmd_queue (list): The queue of commands to be executed.
            command_output (Signal): The signal emitted to notify about command status.
        
        Returns:
            None
        """
        if self._process.state() != QtCore.QProcess.NotRunning:
            self._process.kill()
        self._cmd_queue = []
        self.command_output.emit("Command stopped by user")

    def _get_gmxrc(self):
        """Retrieve the path to the GMXRC file based on the installed version of GROMACS.
        
        This function attempts to execute the 'gmx --version' command to determine the data prefix for the GROMACS installation. It then constructs the path to the GMXRC file located in the 'bin' directory of the data prefix. If the command fails or the GMXRC file is not found, appropriate error messages are logged.
        
        Returns:
            Path or None: The path to the GMXRC file if found, otherwise None.
        """
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
        """Starts the next command in the command queue.
        
        This method checks if there are any commands in the `_cmd_queue`. If the queue is empty, it logs a warning and returns. If there are commands, it pops the first command from the queue, emits a signal indicating that the command is starting, and constructs a full command string that includes setting up the environment. It then emits the working directory and the command being run, sets the working directory for the process, and starts the command in a new bash shell.
        
        Attributes:
            _cmd_queue (list): A queue of commands to be executed.
            _gmxrc (str): The path to the gromacs configuration file.
            _gmxlib (str): The path to the gromacs library, if applicable.
            _workdir (str): The working directory for the command execution.
            _process (QProcess): The process object used to run the command.
        
        Emits:
            command_started (str): Signal emitted when a command starts running.
            command_output (str): Signal emitted with output messages related to command execution.
        """
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
        """Handles the completion of a process.
        
        This method is called when a process finishes execution. It checks the exit code of the process and manages the command queue accordingly. If the exit code is non-zero, it clears the command queue. If the exit code is zero and there are commands in the queue, it initiates the next command.
        
        Args:
            exit_code (int): The exit code returned by the process.
            exit_status (QtCore.QProcess.ExitStatus): The exit status of the process.
        """
        if exit_code != 0:
            self._cmd_queue = []
            return

        if getattr(self, "_cmd_queue", None):
            self._start_next()


    def _on_stdout(self):
        """Handles the standard output from a process.
        
        This method reads all standard output from the associated process, decodes it 
        from bytes to a UTF-8 string, and emits the output if it is not empty.
        
        Attributes:
            self._process: The process from which to read the standard output.
            self.command_output: The signal to emit the output text.
        
        Returns:
            None
        """
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", "replace")
        if text:
            self.command_output.emit(text)


    def _on_stderr(self):
        """Handles the standard error output from a process.
        
        This method reads all standard output from the associated process, decodes it 
        from bytes to a UTF-8 string, and emits the output if it is not empty.
        
        Attributes:
            self._process: The process from which to read the standard output.
            self.command_output: The signal to emit the decoded output.
        
        Returns:
            None
        """
        text = bytes(self._process.readAllStandardOutput()).decode("utf-8", "replace")
        if text:
            self.command_output.emit(text)