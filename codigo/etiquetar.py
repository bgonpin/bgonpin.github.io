import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QListWidget, QComboBox, QMessageBox, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pymongo import MongoClient

class ImageViewer(QMainWindow):
    """Ventana de aplicación para visualizar y etiquetar imágenes con personas desde una base de datos MongoDB."""
    def __init__(self):
        """Inicializar la aplicación ImageViewer con componentes de interfaz gráfica y conexión a base de datos."""
        super().__init__()
        self.setWindowTitle("Imagenes Etiquetadas")
        self.setGeometry(100, 100, 800, 600)

        # MongoDB connection
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['album']
        self.collection = self.db['imagenes_2']

        # Fetch all images
        self.images = list(self.collection.find())
        if not self.images:
            QMessageBox.critical(self, "Error", "No se han encontrado imagenes.")
            sys.exit()
        self.current_index = 0

        # Get all unique personas
        all_personas = set()
        for img in self.images:
            if 'personas' in img and img['personas']:
                if isinstance(img['personas'], list):
                    all_personas.update(img['personas'])
        self.all_personas = sorted(list(all_personas))

        # Layouts
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.prev_btn.clicked.connect(self.show_prev)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Siguiente")
        self.next_btn.clicked.connect(self.show_next)
        nav_layout.addWidget(self.next_btn)

        self.delete_img_btn = QPushButton("Eliminar Imagen")
        self.delete_img_btn.clicked.connect(self.delete_image)
        nav_layout.addWidget(self.delete_img_btn)
        right_layout.addLayout(nav_layout)

        # Personas list
        right_layout.addWidget(QLabel("Personas etiquetadas:"))
        self.personas_layout = QVBoxLayout()
        self.personas_list = QListWidget()
        self.personas_layout.addWidget(self.personas_list)
        self.remove_btn = QPushButton("Eliminar Seleccionada")
        self.remove_btn.clicked.connect(self.remove_persona)
        self.personas_layout.addWidget(self.remove_btn)
        right_layout.addLayout(self.personas_layout)

        # Add new persona from dropdown
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Seleccionar existente:"))
        self.persona_combo = QComboBox()
        self.persona_combo.setEditable(True)
        self.persona_combo.addItems(self.all_personas)
        add_layout.addWidget(self.persona_combo)
        right_layout.addLayout(add_layout)

        self.add_btn = QPushButton("Añadir Seleccionada")
        self.add_btn.clicked.connect(self.add_persona)
        right_layout.addWidget(self.add_btn)

        # Manual add
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Añadir manualmente:"))
        self.manual_input = QLineEdit()
        manual_layout.addWidget(self.manual_input)
        right_layout.addLayout(manual_layout)

        self.add_manual_btn = QPushButton("Añadir Manual")
        self.add_manual_btn.clicked.connect(self.add_manual_persona)
        right_layout.addWidget(self.add_manual_btn)

        main_layout.addWidget(right_panel)

        # Load first image
        self.load_current_image()

    def load_current_image(self):
        """Cargar y mostrar la imagen actual, escalada a 515px de ancho con altura proporcional."""
        img = self.images[self.current_index]
        pixmap = QPixmap(img['ruta'])
        if pixmap.isNull():
            self.image_label.setText("Imagen no encontrada")
        else:
            # Scale to width 515, height proportional
            scaled_width = 515
            aspect_ratio = pixmap.height() / pixmap.width()
            scaled_height = int(scaled_width * aspect_ratio)
            self.image_label.setPixmap(pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio))

        self.update_personas()

    def update_personas(self):
        """Actualizar el widget de lista que muestra las personas (etiquetas) de la imagen actual."""
        self.personas_list.clear()
        img = self.images[self.current_index]
        if 'personas' in img and img['personas']:
            for persona in img['personas']:
                self.personas_list.addItem(persona)

    def show_next(self):
        """Navegar a la siguiente imagen si está disponible."""
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.load_current_image()
        else:
            QMessageBox.information(self, "Fin", "No hay más imágenes.")

    def show_prev(self):
        """Navegar a la imagen anterior si está disponible."""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
        else:
            QMessageBox.information(self, "Inicio", "Es la primera imagen.")

    def add_persona(self):
        """Añadir la persona seleccionada del menú desplegable a las etiquetas de la imagen actual."""
        selected_persona = self.persona_combo.currentText().strip()
        if selected_persona:
            img = self.images[self.current_index]
            if 'personas' not in img:
                img['personas'] = []
            if selected_persona not in img['personas']:
                img['personas'].append(selected_persona)
                self.collection.update_one({'_id': img['_id']}, {'$set': {'personas': img['personas']}})
                # Update all_personas if its new
                if selected_persona not in self.all_personas:
                    self.all_personas.append(selected_persona)
                    self.all_personas.sort()
                    self.persona_combo.clear()
                    self.persona_combo.addItems(self.all_personas)
                    self.persona_combo.setCurrentText(selected_persona)
                self.update_personas()
                QMessageBox.information(self, "Éxito", f"{selected_persona} añadida.")
            else:
                QMessageBox.warning(self, "Advertencia", f"{selected_persona} ya está en la lista.")

    def remove_persona(self):
        """Eliminar la persona seleccionada de las etiquetas de la imagen actual."""
        current_row = self.personas_list.currentRow()
        if current_row >= 0:
            img = self.images[self.current_index]
            if 'personas' in img and current_row < len(img['personas']):
                removed = img['personas'].pop(current_row)
                self.collection.update_one({'_id': img['_id']}, {'$set': {'personas': img['personas']}})
                self.update_personas()
                QMessageBox.information(self, "Éxito", f"{removed} eliminada.")
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona una persona para eliminar.")

    def add_manual_persona(self):
        """Añadir una persona introducida manualmente a las etiquetas de la imagen actual."""
        manual_persona = self.manual_input.text().strip()
        if manual_persona:
            img = self.images[self.current_index]
            if 'personas' not in img:
                img['personas'] = []
            if manual_persona not in img['personas']:
                img['personas'].append(manual_persona)
                self.collection.update_one({'_id': img['_id']}, {'$set': {'personas': img['personas']}})
                # Update all_personas if its new
                if manual_persona not in self.all_personas:
                    self.all_personas.append(manual_persona)
                    self.all_personas.sort()
                    self.persona_combo.clear()
                    self.persona_combo.addItems(self.all_personas)
                self.update_personas()
                self.manual_input.clear()
                QMessageBox.information(self, "Éxito", f"{manual_persona} añadida.")
            else:
                QMessageBox.warning(self, "Advertencia", f"{manual_persona} ya está en la lista.")

    def delete_image(self):
        """Eliminar la imagen actual del sistema de archivos y la base de datos."""
        img = self.images[self.current_index]
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar la imagen '{img['nombre']}' de forma permanente?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(img['ruta'])
            except OSError as e:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar el archivo: {e}")
                return
            self.collection.delete_one({'_id': img['_id']})
            del self.images[self.current_index]
            if len(self.images) == 0:
                QMessageBox.information(self, "Fin", "No hay más imágenes.")
                sys.exit()
            if self.current_index >= len(self.images):
                self.current_index = len(self.images) - 1
            self.load_current_image()
            QMessageBox.information(self, "Éxito", "Imagen eliminada del sistema y base de datos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Dark theme palette
    from PyQt5.QtGui import QPalette, QColor
    from PyQt5.QtCore import Qt
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
