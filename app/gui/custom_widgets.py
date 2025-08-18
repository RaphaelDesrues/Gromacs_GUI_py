# Create custom widgets not implemented in NodeGraphQt
# from NodeGraphQt import NodeBaseWidget

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from NodeGraphQt.custom_widgets.properties_bin.prop_widgets_abstract import BaseProperty # type: ignore

class FileLinkProperty(BaseProperty):
    """
    Champ texte + bouton Browse, compatible avec PropertiesBin de ta version.
    Émet value_changed(prop_name, value) -> la propriété du node est mise à jour.
    """
    def __init__(self, parent=None):
        super(FileLinkProperty, self).__init__(parent)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._edit = QtWidgets.QLineEdit(self)
        self._btn  = QtWidgets.QPushButton("Browse", self)

        lay.addWidget(self._edit, 1)
        lay.addWidget(self._btn, 0)

        self._edit.editingFinished.connect(self._emit_from_edit)
        self._btn.clicked.connect(self._browse)

    # --- compat: ta version n'a pas name(), mais a get_name() / _name ---
    def _prop_name(self):
        if hasattr(self, "get_name"):
            return self.get_name()
        return getattr(self, "_name", "file_link")

    # --- API attendue par NodeGraphQt ---
    def get_value(self):
        return self._edit.text()

    def set_value(self, value):
        self._edit.setText("" if value is None else str(value))

    # --- Emissions de signal (signature: value_changed[str, object]) ---
    def _emit_from_edit(self):
        self.value_changed.emit(self._prop_name(), self.get_value())

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self._edit.setText(path)
            self.value_changed.emit(self._prop_name(), path)












