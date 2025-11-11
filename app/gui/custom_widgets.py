from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from NodeGraphQt.custom_widgets.properties_bin.prop_widgets_abstract import BaseProperty # type: ignore


class FileLinkProperty(BaseProperty):
    """FileLinkProperty is a custom property widget that allows users to select a file from their filesystem. 
    
    This widget consists of a text input field and a 'Browse' button. The user can either type the file path directly into the text field or click the 'Browse' button to open a file dialog for file selection. 
    
    Attributes:
        _edit (QLineEdit): The text input field for displaying the selected file path.
        _btn (QPushButton): The button that opens the file dialog.
    
    Methods:
        _prop_name():
            Returns the name of the property, either from a custom getter or a default value.
    
        get_value():
            Retrieves the current text from the input field.
    
        set_value(value):
            Sets the text of the input field to the provided value.
    
        _emit_from_edit():
            Emits a signal indicating that the value has changed when editing is finished.
    
        _browse():
            Opens a file dialog for the user to select a file and updates the input field with the selected file path.
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

    def _prop_name(self):
        """Returns the property name of the object.
        
        If the object has a method named `get_name`, it calls and returns the result of that method.
        Otherwise, it attempts to retrieve the value of the `_name` attribute. If `_name` is not set, it defaults to returning the string "file_link".
        
        Returns:
            str: The property name of the object, either from `get_name`, `_name`, or "file_link".
        """
        if hasattr(self, "get_name"):
            return self.get_name()
        return getattr(self, "_name", "file_link")

    def get_value(self):
        """Retrieves the current text value from the edit field.
        
        Returns:
            str: The text currently displayed in the edit field.
        """
        return self._edit.text()

    def set_value(self, value):
        """Sets the value of the edit text.
        
        This method updates the text of the edit control. If the provided value is None, 
        the text will be set to an empty string. Otherwise, the value will be converted 
        to a string and set as the text.
        
        Args:
            value: The value to set in the edit control. Can be of any type, 
                   but will be converted to a string if not None.
        """
        self._edit.setText("" if value is None else str(value))

    def _emit_from_edit(self):
        """Emits a signal indicating that the value has changed.
        
        This method triggers the `value_changed` signal, passing the property name and the current value.
        
        Attributes:
            value_changed (Signal): The signal emitted when the value changes.
            _prop_name (callable): A method that returns the name of the property.
            get_value (callable): A method that retrieves the current value.
        """
        self.value_changed.emit(self._prop_name(), self.get_value())

    def _browse(self):
        """Browse for a file and update the text field with the selected file path.
        
        This method opens a file dialog for the user to select a file. If a file is selected, 
        it updates the text field with the file path and emits a signal indicating that the 
        value has changed.
        
        Args:
            self: The instance of the class.
        
        Returns:
            None
        """
        path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if path:
            self._edit.setText(path)
            self.value_changed.emit(self._prop_name(), path)












