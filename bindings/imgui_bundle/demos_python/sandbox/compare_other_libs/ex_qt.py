from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget

selected_idx = 0
items = ["Apple", "Banana", "Cherry"]

class FruitPicker(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label = QLabel("Choose a fruit:")
        self.list_widget = QListWidget()
        self.list_widget.addItems(items)
        self.result_label = QLabel(f"You selected: {items[selected_idx]}")

        self.list_widget.currentRowChanged.connect(self.on_selection_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_selection_changed(self, index):
        global selected_idx
        selected_idx = index
        self.result_label.setText(f"You selected: {items[selected_idx]}")

app = QApplication([])
window = FruitPicker()
window.show()
app.exec()