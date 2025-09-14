from typing import Dict, Any
from PyQt5.QtWidgets import QSplitter, QTabWidget, QAbstractItemView
from PyQt5.QtCore import QByteArray
import base64


class UiStateManager:
    """Capture/restore UI state

    - Use objectName of specific widgets (splitters/tabs/headers)
    - Captures window geometry/state optionally
    - Returns a dict structure suitable for JSON
    """
    def __init__(self, include_geometry = True, include_state = True, schema_version = "1"):

        self.widgets_names = {"splitters": [], "tabs": [], "headers": []}

        # if widget_names:
        #     for key in self.widget_names.keys():
        #         if key in widget_names and isinstance(widget_names[key], list):
        #             self.widget_names[key] = widget_names[key]

        self.include_geometry = include_geometry
        self.include_state = include_state
        self.schema_version = schema_version


    def capture(self, main_window):
        """Capture UI state from main_window
        Returns a dict ready to be serialized to JSON
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
        if isinstance(data, QByteArray):
            raw = bytes(data)
        else:
            raw = data if isinstance(data, (bytes, bytearray)) else b""
        return base64.b64encode(raw).decode("ascii") if raw else ""
    
    @staticmethod
    def _decode_bytes(data_b64: str) -> QByteArray:
        try:
            raw = base64.b64decode(data_b64) if data_b64 else b""
        except Exception:
            raw = b""
        return QByteArray(raw)
