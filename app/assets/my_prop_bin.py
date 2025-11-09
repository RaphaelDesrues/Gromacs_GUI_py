import logging
from NodeGraphQt.custom_widgets.properties_bin.node_property_widgets import PropertiesBinWidget, NodePropEditorWidget #type: ignore
from NodeGraphQt import BaseNode # type: ignore
from Qt import QtCore, QtWidgets


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
        # Retrieve the labels in add_text_input
        mapping = getattr(node, "_prop_labels", {})

        for prop_name, pretty_label in mapping.items():
            try:
                w = self.get_widget(prop_name)
                if not w:
                    continue

                # Access internal grid that stores: QLabel, widget
                container = w.parent()
                grid = getattr(container, "_PropertiesContainer__layout", None)
                if not grid:
                    continue

                idx = grid.indexOf(w)
                if idx < 0:
                    continue

                r, c, rs, cs = grid.getItemPosition(idx)
                item = grid.itemAtPosition(r, 0)  # 0 = column label
                if item and item.widget():
                    item.widget().setText(pretty_label)
            except Exception:
                logging.exception("Failed to apply pretty label for %s on %s", prop_name, node)
        
        # Colors by role based on IN_PORT / OUT_PORT mapping
        try:
            in_flags = set((getattr(node, "IN_PORT", {}) or {}).values())
            out_flags = set((getattr(node, "OUT_PORT", {}) or {}).values())
            props = node.properties().get("custom", {})

            for name in props.keys():
                w = self.get_widget(name)
                if not w:
                    continue

                role = "in" if name in in_flags else ("out" if name in out_flags else "param")

                w.setProperty("propRole", role)

                # Force Qt to apply sytle
                style = w.style()
                if style:
                    style.unpolish(w)
                    style.polish(w)
                w.update()

        except Exception:
            logging.exception("Failed to tag custom properties for node %s", node)

        return ports


class MyPropertiesBin(PropertiesBinWidget):
    def create_property_editor(self, node):
        return MyPropEditor(node=node)
