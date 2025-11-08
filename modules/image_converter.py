"""
Image Converter - PyQt6 Version
Convert images between formats, create multi-size icons, extract color palettes
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSlider,
    QProgressBar, QListWidget, QTextEdit, QSizePolicy, QComboBox,
    QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QImage
from PIL import Image
from pathlib import Path
import json
from typing import List, Tuple
from collections import Counter


class ImageConverterDialog(QDialog):
    """
    Image Converter - Convert between formats, create icons, extract palettes

    Features:
    - Load and convert images between formats
    - Multi-size ICO generation (32x32, 128x128, 256x256)
    - Quality adjustment for lossy formats
    - Batch conversion
    - Recent files tracking
    - Color palette extraction
    - Drag and drop support
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Converter")
        self.setMinimumSize(900, 700)

        self.current_image = None
        self.current_file_path = None
        self.quality = 95
        self.recent_files = []

        # Supported formats
        self.input_formats = "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.ico *.webp *.tiff *.tif);;All Files (*.*)"
        self.output_formats = {
            "ICO": "*.ico",
            "JPEG": "*.jpg",
            "PNG": "*.png",
            "BMP": "*.bmp",
            "GIF": "*.gif",
            "WebP": "*.webp",
            "TIFF": "*.tiff"
        }

        self._setup_ui()
        self._load_recent_files()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Image Converter")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Main content (horizontal split)
        content_layout = QHBoxLayout()

        # Left side: Preview and controls
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel, 6)

        # Right side: Options and info
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, 4)

        layout.addLayout(content_layout, 1)

        # Bottom: Progress and status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready - Drop an image file or click Select Image")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)

    def _create_left_panel(self) -> QGroupBox:
        """Create left panel with preview and main controls"""
        group = QGroupBox("Image Preview")
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(group)

        # Preview label
        self.preview_label = QLabel("No image loaded")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #555; background-color: #1E1E1E; min-height: 300px;")
        self.preview_label.setScaledContents(False)
        layout.addWidget(self.preview_label, 1)

        # Image info
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #888; font-size: 10pt;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.load_btn = QPushButton("Select Image...")
        self.load_btn.clicked.connect(self._load_image)
        button_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton("Save As...")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_image)
        button_layout.addWidget(self.save_btn)

        self.batch_btn = QPushButton("Batch Convert...")
        self.batch_btn.clicked.connect(self._batch_convert)
        button_layout.addWidget(self.batch_btn)

        layout.addLayout(button_layout)

        return group

    def _create_right_panel(self) -> QWidget:
        """Create right panel with options and tools"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Quality settings
        quality_group = QGroupBox("Conversion Settings")
        quality_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        quality_layout = QVBoxLayout(quality_group)

        quality_label_layout = QHBoxLayout()
        quality_label_layout.addWidget(QLabel("Quality (for JPEG/WebP):"))
        self.quality_value_label = QLabel("95%")
        self.quality_value_label.setStyleSheet("font-weight: bold;")
        quality_label_layout.addWidget(self.quality_value_label)
        quality_layout.addLayout(quality_label_layout)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(10, 100)
        self.quality_slider.setValue(95)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.valueChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self.quality_slider)

        layout.addWidget(quality_group)

        # ICO settings
        ico_group = QGroupBox("ICO Generation")
        ico_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        ico_layout = QVBoxLayout(ico_group)

        ico_layout.addWidget(QLabel("Generate .ico with multiple sizes:"))
        ico_layout.addWidget(QLabel("• 32x32 (standard)"))
        ico_layout.addWidget(QLabel("• 128x128 (medium)"))
        ico_layout.addWidget(QLabel("• 256x256 (large)"))

        layout.addWidget(ico_group)

        # Color Palette Extraction
        palette_group = QGroupBox("Color Palette Extraction")
        palette_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        palette_layout = QVBoxLayout(palette_group)

        extract_btn = QPushButton("Extract Color Palette")
        extract_btn.clicked.connect(self._extract_palette)
        palette_layout.addWidget(extract_btn)

        self.palette_display = QTextEdit()
        self.palette_display.setMaximumHeight(100)
        self.palette_display.setPlaceholderText("Top colors will appear here...")
        self.palette_display.setReadOnly(True)
        palette_layout.addWidget(self.palette_display)

        layout.addWidget(palette_group)

        # Recent Files
        recent_group = QGroupBox("Recent Files")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        self.recent_list.itemDoubleClicked.connect(self._load_recent_file)
        recent_layout.addWidget(self.recent_list)

        layout.addWidget(recent_group)

        layout.addStretch()

        return container

    # ==================== File Operations ====================

    def _load_image(self):
        """Load image from file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            self.input_formats
        )

        if file_path:
            self._load_image_from_path(file_path)

    def _load_image_from_path(self, file_path: str):
        """Load image from file path"""
        try:
            self.current_file_path = Path(file_path)
            self.current_image = Image.open(file_path)

            # Convert to RGB if needed for display
            if self.current_image.mode in ('RGBA', 'LA', 'P'):
                display_image = self.current_image.convert('RGB')
            else:
                display_image = self.current_image

            # Update preview
            self._update_preview(display_image)

            # Update info
            width, height = self.current_image.size
            mode = self.current_image.mode
            format_name = self.current_image.format or "Unknown"
            self.info_label.setText(f"{width}x{height} • {mode} • {format_name}")

            # Enable save button
            self.save_btn.setEnabled(True)

            # Update status
            self.status_label.setText(f"Loaded: {self.current_file_path.name}")

            # Add to recent files
            self._add_to_recent_files(file_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")

    def _update_preview(self, image: Image.Image):
        """Update preview label with image"""
        # Convert PIL Image to QPixmap
        if image.mode == 'RGB':
            data = image.tobytes("raw", "RGB")
            qimage = QImage(data, image.width, image.height, image.width * 3, QImage.Format.Format_RGB888)
        elif image.mode == 'RGBA':
            data = image.tobytes("raw", "RGBA")
            qimage = QImage(data, image.width, image.height, image.width * 4, QImage.Format.Format_RGBA8888)
        else:
            data = image.convert('RGB').tobytes("raw", "RGB")
            qimage = QImage(data, image.width, image.height, image.width * 3, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)

        # Scale to fit preview (max 500x500)
        scaled_pixmap = pixmap.scaled(
            500, 500,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview_label.setPixmap(scaled_pixmap)

    def _save_image(self):
        """Save/convert current image"""
        if not self.current_image:
            QMessageBox.warning(self, "No Image", "Please load an image first")
            return

        # Create filter string for file dialog
        filter_str = ";;".join([f"{name} Files ({ext})" for name, ext in self.output_formats.items()])
        filter_str += ";;All Files (*.*)"

        # Get initial filename
        initial_name = self.current_file_path.stem if self.current_file_path else "image"

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            initial_name,
            filter_str
        )

        if file_path:
            self._convert_and_save(file_path)

    def _convert_and_save(self, file_path: str):
        """Convert and save image to specified path"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Saving...")

            file_path = Path(file_path)

            # Handle ICO format specially (multi-size)
            if file_path.suffix.lower() == '.ico':
                self._save_as_ico(file_path)
            else:
                # Regular conversion
                image_to_save = self.current_image.copy()

                self.progress_bar.setValue(25)

                # Convert RGBA to RGB for JPEG
                if file_path.suffix.lower() in ('.jpg', '.jpeg') and image_to_save.mode in ('RGBA', 'LA'):
                    rgb_image = Image.new('RGB', image_to_save.size, (255, 255, 255))
                    if image_to_save.mode == 'RGBA':
                        rgb_image.paste(image_to_save, mask=image_to_save.split()[3])
                    else:
                        rgb_image.paste(image_to_save)
                    image_to_save = rgb_image

                self.progress_bar.setValue(50)

                # Save with appropriate options
                save_kwargs = {}
                if file_path.suffix.lower() in ('.jpg', '.jpeg', '.webp'):
                    save_kwargs['quality'] = self.quality
                    save_kwargs['optimize'] = True

                image_to_save.save(file_path, **save_kwargs)

            self.progress_bar.setValue(100)
            self.status_label.setText(f"Saved: {file_path.name}")

            QMessageBox.information(self, "Success", f"Image saved successfully:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save image:\n{e}")
        finally:
            self.progress_bar.setVisible(False)

    def _save_as_ico(self, file_path: Path):
        """Save image as multi-size ICO file"""
        try:
            sizes = [(32, 32), (128, 128), (256, 256)]
            images = []

            for size in sizes:
                resized = self.current_image.copy()
                resized.thumbnail(size, Image.Resampling.LANCZOS)

                # Convert to RGBA if needed
                if resized.mode != 'RGBA':
                    resized = resized.convert('RGBA')

                images.append(resized)

            # Save all sizes to ICO
            images[0].save(file_path, format='ICO', sizes=[(img.width, img.height) for img in images], append_images=images[1:])

            self.progress_bar.setValue(100)

        except Exception as e:
            raise Exception(f"ICO generation failed: {e}")

    def _batch_convert(self):
        """Batch convert multiple images"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images for Batch Conversion",
            "",
            self.input_formats
        )

        if not file_paths:
            return

        # Create dialog for format selection
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Output Format")
        dialog_layout = QVBoxLayout(dialog)

        dialog_layout.addWidget(QLabel("Choose output format:"))

        format_combo = QComboBox()
        format_combo.addItems(list(self.output_formats.keys()))
        dialog_layout.addWidget(format_combo)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        dialog_layout.addLayout(button_layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        format_name = format_combo.currentText()

        # Ask for output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        # Convert all files
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(file_paths))
        total = len(file_paths)
        succeeded = 0

        for i, file_path in enumerate(file_paths):
            try:
                img = Image.open(file_path)
                input_path = Path(file_path)
                output_path = Path(output_dir) / f"{input_path.stem}.{self.output_formats[format_name].replace('*.', '')}"

                # Convert and save
                if output_path.suffix.lower() == '.ico':
                    # Multi-size ICO
                    sizes = [(32, 32), (128, 128), (256, 256)]
                    images = []
                    for size in sizes:
                        resized = img.copy()
                        resized.thumbnail(size, Image.Resampling.LANCZOS)
                        if resized.mode != 'RGBA':
                            resized = resized.convert('RGBA')
                        images.append(resized)
                    images[0].save(output_path, format='ICO', sizes=[(im.width, im.height) for im in images], append_images=images[1:])
                else:
                    save_kwargs = {}
                    if output_path.suffix.lower() in ('.jpg', '.jpeg', '.webp'):
                        save_kwargs['quality'] = self.quality
                        if img.mode in ('RGBA', 'LA'):
                            rgb_image = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                rgb_image.paste(img, mask=img.split()[3])
                            else:
                                rgb_image.paste(img)
                            img = rgb_image
                    img.save(output_path, **save_kwargs)

                succeeded += 1
                self.status_label.setText(f"Converting: {i+1}/{total}")
                self.progress_bar.setValue(i + 1)

            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")

        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Batch conversion complete: {succeeded}/{total} successful")
        QMessageBox.information(self, "Batch Conversion Complete", f"Successfully converted {succeeded} out of {total} images")

    # ==================== Color Palette Extraction ====================

    def _extract_palette(self):
        """Extract top colors from current image"""
        if not self.current_image:
            QMessageBox.warning(self, "No Image", "Please load an image first")
            return

        try:
            # Convert to RGB if needed
            img = self.current_image
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize for faster processing (max 200x200)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # Get all pixels
            pixels = list(img.getdata())

            # Count colors
            color_counts = Counter(pixels)

            # Get top 10 colors
            top_colors = color_counts.most_common(10)

            # Format output
            output = "Top 10 Colors:\n\n"
            for i, (color, count) in enumerate(top_colors, 1):
                hex_color = "#{:02X}{:02X}{:02X}".format(*color)
                percentage = (count / len(pixels)) * 100
                output += f"{i}. {hex_color}  ({percentage:.1f}%)\n"

            self.palette_display.setPlainText(output)
            self.status_label.setText("Color palette extracted")

        except Exception as e:
            QMessageBox.critical(self, "Extraction Error", f"Failed to extract palette:\n{e}")

    # ==================== Recent Files ====================

    def _load_recent_files(self):
        """Load recent files from settings"""
        try:
            settings_file = Path(__file__).parent.parent / "config" / "image_converter_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                    self.recent_files = data.get('recent_files', [])
                    self._update_recent_list()
        except:
            pass

    def _save_recent_files(self):
        """Save recent files to settings"""
        try:
            settings_file = Path(__file__).parent.parent / "config" / "image_converter_settings.json"
            settings_file.parent.mkdir(exist_ok=True)
            data = {'recent_files': self.recent_files}
            with open(settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def _add_to_recent_files(self, file_path: str):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self._save_recent_files()
        self._update_recent_list()

    def _update_recent_list(self):
        """Update recent files list widget"""
        self.recent_list.clear()
        for file_path in self.recent_files:
            if Path(file_path).exists():
                self.recent_list.addItem(Path(file_path).name)

    def _load_recent_file(self, item):
        """Load file from recent files list"""
        index = self.recent_list.row(item)
        if index < len(self.recent_files):
            file_path = self.recent_files[index]
            if Path(file_path).exists():
                self._load_image_from_path(file_path)
            else:
                QMessageBox.warning(self, "File Not Found", f"File no longer exists:\n{file_path}")

    # ==================== Drag and Drop ====================

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._load_image_from_path(file_path)

    # ==================== Slots ====================

    def _on_quality_changed(self, value: int):
        """Handle quality slider change"""
        self.quality = value
        self.quality_value_label.setText(f"{value}%")
