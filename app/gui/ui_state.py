from typing import Dict, Any
from PyQt5.QtWidgets import QSplitter, QTabWidget, QAbstractItemView
from PyQt5.QtCore import QByteArray
import base64


class UiStateManager:
    """UiStateManager is a class that manages the state of a user interface (UI) by capturing and restoring its geometry and state.
    
    Attributes:
        widgets_names (dict): A dictionary containing lists of widget names categorized by type (splitters, tabs, headers).
        include_geometry (bool): A flag indicating whether to include geometry information in the captured state. Defaults to True.
        include_state (bool): A flag indicating whether to include state information in the captured state. Defaults to True.
        schema_version (str): The version of the schema used for the state. Defaults to "1".
    
    Methods:
        capture(main_window):
            Captures the current UI state from the provided main window and returns it as a dictionary ready for JSON serialization.
    
        restore(main_window, state):
            Restores the UI state of the provided main window from the given state dictionary.
    
        _encode_bytes(data):
            Encodes the given data into a base64 string.
    
        _decode_bytes(data_b64):
            Decodes a base64 string back into a QByteArray.
    """
    def __init__(self, include_geometry = True, include_state = True, schema_version = "1"):

        self.widgets_names = {"splitters": [], "tabs": [], "headers": []}

        self.include_geometry = include_geometry
        self.include_state = include_state
        self.schema_version = schema_version


    def capture(self, main_window):
        """Captures the state of the main window and its child widgets.
        
        This method collects various aspects of the main window's state, including
        geometry, state, splitters, tabs, and headers, and returns them in a structured
        dictionary format.
        
        Args:
            main_window (QMainWindow): The main window from which to capture the state.
        
        Returns:
            dict: A dictionary containing the captured state, including:
                - version (str): The schema version of the state.
                - window (dict): A dictionary with the window's geometry and state.
                - splitters (dict): A dictionary mapping splitter object names to their saved states.
                - tabs (dict): A dictionary mapping tab widget object names to their current index.
                - headers (dict): A dictionary mapping item view object names to their header states.
        """
        # Base skeleton to save the state
        state = {
            "version": self.schema_version,
            "window": {},
            "splitters": {},
            "tabs": {},
            "headers": {}
        }

        # Window geometry and toolbar state
        # saveGeometry() and saveState() return a QByteArray which is not Json serialized
        # So we tranform it in base64 chain via self._encode_bytes()
        if self.include_geometry:
            geom = main_window.saveGeometry()
            state["window"]["geometry"] = self._encode_bytes(geom)
        if self.include_state:
            win_state = main_window.saveState()
            state["window"]["state"] = self._encode_bytes(win_state)

        # Splitters
        for i, splitter in enumerate(main_window.findChildren(QSplitter)):
            key = splitter.objectName()
            state["splitters"][key] = self._encode_bytes(splitter.saveState())

        # Tabs
        for i, tab in enumerate(main_window.findChildren(QTabWidget)):
            key = tab.objectName()
            state["tabs"][key] = int(tab.currentIndex())

        # Headers
        def _header_view(view):
            """Retrieve the header from a given view object.
            
            This function checks if the provided view object has a `header` method or a 
            `horizontalHeader` method. If either method is callable, it invokes the method 
            and returns the result if it is not `None`. If neither method is available or 
            both return `None`, the function returns `None`.
            
            Args:
                view: An object that may have a `header` or `horizontalHeader` method.
            
            Returns:
                The result of the `header` or `horizontalHeader` method if it is callable 
                and returns a non-None value; otherwise, returns `None`.
            """
            if hasattr(view, "header") and callable(view.header):
                h = view.header()
                if h is not None:
                    return h
            if hasattr(view, "horizontalHeader") and callable(view.horizontalHeader):
                h = view.horizontalHeader()
                if h is not None:
                    return h
            return None 
        
        for i, view in enumerate(main_window.findChildren(QAbstractItemView)):
            h = _header_view(view)
            if h is None:
                continue
            key = view.objectName()
            state["headers"][key] = self._encode_bytes(h.saveState())
        
        return state
            

    def restore(self, main_window, state: Dict[str, Any]) -> None:
        """Restores the state of the main window and its components from a given state dictionary.
        
        Args:
            main_window (QMainWindow): The main window instance to restore the state for.
            state (Dict[str, Any]): A dictionary containing the state information to restore. 
                It should include the following keys:
                - "window": A dictionary with keys "geometry" (base64 encoded) and "state" (base64 encoded).
                - "splitters": A dictionary mapping splitter names to their encoded states (base64 encoded).
                - "tabs": A dictionary mapping tab widget names to their current index.
                - "headers": A dictionary mapping view names to their header states (base64 encoded).
        
        Returns:
            None: This function does not return a value.
        
        Notes:
            - The function handles exceptions silently, meaning that if any restoration fails, it will continue with the next item.
            - The state dictionary must be a valid dictionary; otherwise, the function will return immediately without making any changes.
        """
        if not isinstance(state, dict):
            return

        # Window
        window_state = state.get("window", {}) or {}
        geom_b64 = window_state.get("geometry")
        if geom_b64:
            try:
                main_window.restoreGeometry(self._decode_bytes(geom_b64))
            except Exception:
                pass

        dock_b64 = window_state.get("state")
        if dock_b64:
            try:
                main_window.restoreState(self._decode_bytes(dock_b64))
            except Exception:
                pass

        # Splitters
        splitters_state = state.get("splitters", {}) or {}
        for name, encoded in splitters_state.items():
            # si le nom est vide, on ne peut pas le retrouver de façon fiable
            if not name or not encoded:
                continue
            splitter = main_window.findChild(QSplitter, name)
            if splitter is None:
                continue
            try:
                splitter.restoreState(self._decode_bytes(encoded))
            except Exception:
                # on n’échoue pas toute la restauration pour un seul splitter
                pass

        # Tabs
        tabs_state = state.get("tabs", {}) or {}
        for name, idx in tabs_state.items():
            if not name:
                continue
            tab = main_window.findChild(QTabWidget, name)
            if tab is None:
                continue
            try:
                i = int(idx)
                if 0 <= i < tab.count():
                    tab.setCurrentIndex(i)
            except Exception:
                pass

        # Headers
        def _header_view(view):
            """Retrieve the header view from a given view object.
            
            This function checks if the provided view object has a `header` method or a 
            `horizontalHeader` method. If either method is callable, it invokes the method 
            and returns the result if it is not `None`. If neither method is available or 
            both return `None`, the function returns `None`.
            
            Args:
                view: An object that may have a `header` or `horizontalHeader` method.
            
            Returns:
                The result of the `header` or `horizontalHeader` method if callable and 
                not `None`, otherwise `None`.
            """
            if hasattr(view, "header") and callable(view.header):
                h = view.header()
                if h is not None:
                    return h
            if hasattr(view, "horizontalHeader") and callable(view.horizontalHeader):
                h = view.horizontalHeader()
                if h is not None:
                    return h
            return None

        headers_state = state.get("headers", {}) or {}
        for name, encoded in headers_state.items():
            if not name or not encoded:
                continue
            view = main_window.findChild(QAbstractItemView, name)
            if view is None:
                continue
            h = _header_view(view)
            if h is None:
                continue
            try:
                h.restoreState(self._decode_bytes(encoded))
            except Exception:
                pass


    @staticmethod
    def _encode_bytes(data) -> str:
        """Encode the given data into a Base64 string.
        
        This function takes a QByteArray or a bytes/bytearray object and encodes it into a Base64 string. If the input is not of the expected type, it returns an empty string.
        
        Args:
            data (QByteArray | bytes | bytearray): The data to be encoded. Can be a QByteArray, bytes, or bytearray.
        
        Returns:
            str: The Base64 encoded string representation of the input data, or an empty string if the input is not valid.
        """
        if isinstance(data, QByteArray):
            raw = bytes(data)
        else:
            raw = data if isinstance(data, (bytes, bytearray)) else b""
        return base64.b64encode(raw).decode("ascii") if raw else ""
    
    @staticmethod
    def _decode_bytes(data_b64: str) -> QByteArray:
        """Decode a base64 encoded string into a QByteArray.
        
        Args:
            data_b64 (str): The base64 encoded string to decode. If the string is empty, an empty QByteArray is returned.
        
        Returns:
            QByteArray: The decoded QByteArray containing the raw bytes. If decoding fails or the input is empty, an empty QByteArray is returned.
        """
        try:
            raw = base64.b64decode(data_b64) if data_b64 else b""
        except Exception:
            raw = b""
        return QByteArray(raw)
