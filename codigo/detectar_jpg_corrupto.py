#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Imágenes JPG Corruptas con PySide6
"""

import os
import sys
import threading
import time
from pathlib import Path
from PIL import Image, ImageFile

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QWidget, QPushButton, QLabel, QProgressBar,
    QTextEdit, QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QObject

# Permitir cargar imágenes truncadas
ImageFile.LOAD_TRUNCATED_IMAGES = True


# ------------------ Lógica Detector ------------------

class JPGCorruptionDetector(QObject):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(list, list, int)

    def __init__(self):
        super().__init__()
        self.corrupted_files = []
        self.valid_files = []
        self.total_files = 0

    def is_jpg_file(self, file_path):
        return Path(file_path).suffix.lower() in {'.jpg', '.jpeg'}

    def check_file_header(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
                if len(header) < 3 or header[:3] != b'\xff\xd8\xff':
                    return False, "Cabecera JPG inválida"
                return True, "Cabecera válida"
        except Exception as e:
            return False, f"Error leyendo archivo: {str(e)}"

    def check_with_pil(self, file_path):
        try:
            with Image.open(file_path) as img:
                if img.format not in ['JPEG', 'JPG']:
                    return False, f"Formato incorrecto: {img.format}"
                img.verify()
                with Image.open(file_path) as img2:
                    img2.load()
                return True, f"Imagen válida {img.size}"
        except Exception as e:
            return False, f"Error PIL: {str(e)}"

    def check_file_size(self, file_path):
        try:
            size = os.path.getsize(file_path)
            if size == 0:
                return False, "Archivo vacío"
            elif size < 100:
                return False, f"Archivo muy pequeño ({size} bytes)"
            return True, f"Tamaño: {size} bytes"
        except Exception as e:
            return False, f"Error obteniendo tamaño: {str(e)}"

    def detect_corruption(self, file_path):
        if not self.is_jpg_file(file_path):
            return False, "No es un archivo JPG"

        results = {}
        is_valid_size, size_msg = self.check_file_size(file_path)
        results['size'] = (is_valid_size, size_msg)

        is_valid_header, header_msg = self.check_file_header(file_path)
        results['header'] = (is_valid_header, header_msg)

        is_valid_pil, pil_msg = self.check_with_pil(file_path)
        results['pil'] = (is_valid_pil, pil_msg)

        is_corrupted = not (is_valid_size and is_valid_header and is_valid_pil)
        return not is_corrupted, results

    def scan(self, path, recursive=True):
        self.corrupted_files = []
        self.valid_files = []

        if os.path.isfile(path):
            jpg_files = [Path(path)]
        else:
            if recursive:
                jpg_files = list(Path(path).rglob("*.jpg")) + list(Path(path).rglob("*.jpeg"))
            else:
                jpg_files = list(Path(path).glob("*.jpg")) + list(Path(path).glob("*.jpeg"))

        self.total_files = len(jpg_files)
        if not jpg_files:
            self.log_signal.emit("No se encontraron archivos JPG")
            self.finished_signal.emit(self.valid_files, self.corrupted_files, 0)
            return

        for i, jpg_file in enumerate(jpg_files, start=1):
            self.progress_signal.emit(i, len(jpg_files), f"Analizando: {jpg_file.name}")
            is_valid, results = self.detect_corruption(jpg_file)

            if is_valid:
                self.valid_files.append(jpg_file)
                self.log_signal.emit(f"✅ {jpg_file}")
            else:
                self.corrupted_files.append((jpg_file, results))
                self.log_signal.emit(f"❌ {jpg_file} - CORRUPTA")
                for check_type, (ok, msg) in results.items():
                    if not ok:
                        self.log_signal.emit(f"   └─ {check_type}: {msg}")

        self.finished_signal.emit(self.valid_files, self.corrupted_files, len(jpg_files))


# ------------------ Interfaz Gráfica ------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = JPGCorruptionDetector()
        self.scanning = False
        self.path = ""

        self.setWindowTitle("Detector de Imágenes JPG Corruptas - PySide6")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Botones selección
        btn_layout = QHBoxLayout()
        self.btn_folder = QPushButton("📁 Seleccionar Carpeta")
        self.btn_file = QPushButton("📄 Seleccionar Archivo")
        btn_layout.addWidget(self.btn_folder)
        btn_layout.addWidget(self.btn_file)
        layout.addLayout(btn_layout)

        self.path_label = QLabel("Ruta seleccionada: Ninguna")
        layout.addWidget(self.path_label)

        # Opción recursiva
        self.chk_recursive = QCheckBox("Búsqueda recursiva")
        self.chk_recursive.setChecked(True)
        layout.addWidget(self.chk_recursive)

        # Botones acción
        action_layout = QHBoxLayout()
        self.btn_scan = QPushButton("🔍 Iniciar Análisis")
        self.btn_stop = QPushButton("⏹ Detener")
        self.btn_stop.setEnabled(False)
        action_layout.addWidget(self.btn_scan)
        action_layout.addWidget(self.btn_stop)
        layout.addLayout(action_layout)

        # Progreso
        self.progress = QProgressBar()
        self.progress_label = QLabel("Listo para analizar")
        layout.addWidget(self.progress)
        layout.addWidget(self.progress_label)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Estadísticas
        self.stats_label = QLabel("Total: 0 | Válidas: 0 | Corruptas: 0")
        layout.addWidget(self.stats_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Conectar señales
        self.btn_folder.clicked.connect(self.select_folder)
        self.btn_file.clicked.connect(self.select_file)
        self.btn_scan.clicked.connect(self.start_scan)
        self.btn_stop.clicked.connect(self.stop_scan)

        self.detector.log_signal.connect(self.log_message)
        self.detector.progress_signal.connect(self.update_progress)
        self.detector.finished_signal.connect(self.scan_finished)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            self.path = folder
            self.path_label.setText(f"Ruta seleccionada: {folder}")

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", "Imágenes JPG (*.jpg *.jpeg);;Todos (*.*)")
        if file:
            self.path = file
            self.path_label.setText(f"Ruta seleccionada: {file}")

    def log_message(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {msg}")

    def update_progress(self, current, total, status):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress_label.setText(f"{current}/{total} - {status}")

    def start_scan(self):
        if not self.path:
            QMessageBox.warning(self, "Advertencia", "Selecciona una carpeta o archivo primero")
            return
        if not os.path.exists(self.path):
            QMessageBox.critical(self, "Error", "La ruta seleccionada no existe")
            return

        self.log_text.clear()
        self.scanning = True
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)

        recursive = self.chk_recursive.isChecked()

        thread = threading.Thread(target=self.detector.scan, args=(self.path, recursive), daemon=True)
        thread.start()

    def stop_scan(self):
        self.scanning = False
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_message("⏹ Escaneo detenido (no implementado completamente)")

    def scan_finished(self, valid_files, corrupted_files, total):
        self.scanning = False
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)

        resumen = (
            f"\n📊 RESUMEN:\n"
            f"Total analizados: {total}\n"
            f"✅ Válidos: {len(valid_files)}\n"
            f"❌ Corruptos: {len(corrupted_files)}"
        )
        self.log_message(resumen)
        self.stats_label.setText(f"Total: {total} | Válidas: {len(valid_files)} | Corruptas: {len(corrupted_files)}")

        if corrupted_files:
            QMessageBox.information(self, "Análisis Completado",
                                    f"Se encontraron {len(corrupted_files)} archivos corruptos.\nRevisa el log.")
        else:
            QMessageBox.information(self, "Análisis Completado", "¡Todas las imágenes están en buen estado!")


# ------------------ MAIN ------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())