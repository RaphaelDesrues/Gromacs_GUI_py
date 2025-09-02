from NodeGraphQt.custom_widgets.properties_bin.node_property_widgets import PropertiesBinWidget, NodePropEditorWidget #type: ignore
from NodeGraphQt import BaseNode # type: ignore


# -----------------------------
# Custom BaseNode
# -----------------------------
class MyBaseNode(BaseNode):
    def __init__(self):
        super().__init__()
        self._prop_labels = {}

        # self.PREDEFINED_PROPS = {
        #     "input_file": ("Fichier d’entrée", "init_conf.gro"),
        #     "output_file": ("Fichier de sortie", "out.gro"),
        #     "temperature": ("Température", "300"),
        # }

        self.add_combo_menu(
            name="Add_Props",
            label="Add_Props",
            items=list(self.PREDEFINED_PROPS.keys())
        )

        self.hide_widget(name="Add_Props", push_undo=False)

        self.set_property("Add_Props", None)


    def add_text_input(self, name, label=None, text=""):
        if label:
            self._prop_labels[name] = label
        return super().add_text_input(name=name, label=label, text=text)



    # def on_property_changed(self, name, value):
    #     if name == "Add_Props" and value:
    #         print(f"Propriété choisie: {value}")
    #         label, default = self.PREDEFINED_PROPS[value]
    #         self.add_text_input(name=value, label=label, text=default)
    #     return super().on_property_changed(name, value)



# -----------------------------
# Custom add_text_input
# -----------------------------
class MyPropEditor(NodePropEditorWidget):
    def _read_node(self, node):
        ports = super()._read_node(node)

        # On récupère les labels stockés par add_text_input
        mapping = getattr(node, "_prop_labels", {})

        for prop_name, pretty_label in mapping.items():
            w = self.get_widget(prop_name)
            if not w:
                continue

            # Accès au grid interne qui contient (QLabel, widget)
            container = w.parent()
            grid = getattr(container, "_PropertiesContainer__layout", None)
            if not grid:
                continue

            idx = grid.indexOf(w)
            if idx < 0:
                continue

            r, c, rs, cs = grid.getItemPosition(idx)
            item = grid.itemAtPosition(r, 0)  # 0 = colonne label
            if item and item.widget():
                item.widget().setText(pretty_label)

        return ports


class MyPropertiesBin(PropertiesBinWidget):
    def create_property_editor(self, node):
        return MyPropEditor(node=node)
