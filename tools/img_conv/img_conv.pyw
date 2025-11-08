import sys
import argparse
import os
from pathlib import Path

# Check if running in command line mode first
def is_command_line_mode():
    return len(sys.argv) > 1 and sys.argv[1] not in ['--help', '-h']

# Import GUI libraries only if not in command line mode
GUI_AVAILABLE = True
if not is_command_line_mode():
    try:
        import customtkinter as ctk
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
        from PIL import Image, ImageTk
        from tkinterdnd2 import DND_FILES
        import customtkinter
    except ImportError as e:
        GUI_AVAILABLE = False
        print(f"GUI libraries not available: {e}")
        if len(sys.argv) == 1:  # No arguments, user expects GUI
            print("Please install required dependencies: pip install customtkinter pillow tkinterdnd2")
            sys.exit(1)
else:
    # Command line mode - only import essential libraries
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        # Tkinter not available, will use console output only
        tk = None
        messagebox = None

# Always import these for both GUI and CLI
from PIL import Image
import threading
import json
import time

# Import for SVG support
try:
    import cairosvg
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False

class ImageConverter:
    def __init__(self):
        # Set theme and appearance
        try:
            customtkinter.set_default_color_theme("../themes/GhostTrain.json")
        except:
            customtkinter.set_default_color_theme("blue")  # Fallback to default theme
        
        customtkinter.set_appearance_mode("light")
        
        # Initialize variables
        self.current_image = None
        self.current_filename = ""
        self.current_file_path = ""
        self.conversion_quality = 95  # Default quality for lossy formats
        
        # Extended format support including SVG
        self.supported_formats = {
            "input": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".ico", ".webp", 
                     ".ppm", ".pgm", ".pnm", ".tiff", ".tif"] + ([".svg"] if SVG_SUPPORT else []),
            "output": [("ICO", "*.ico"), ("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp"), 
                      ("GIF", "*.gif"), ("WebP", "*.webp"), ("PPM", "*.ppm"), ("PGM", "*.pgm"), 
                      ("PNM", "*.pnm"), ("TIFF", "*.tiff")]
        }
        
        # Recent files (max 5)
        self.recent_files = self.load_recent_files()
        
        self.setup_ui()
        
    def load_recent_files(self):
        """Load recent files from settings"""
        try:
            settings_file = "config/image_converter_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                    return data.get('recent_files', [])
        except:
            pass
        return []
    
    def save_recent_files(self):
        """Save recent files to settings"""
        try:
            settings_file = "config/image_converter_settings.json"
            data = {'recent_files': self.recent_files}
            with open(settings_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def add_to_recent_files(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5]  # Keep only 5 recent files
        self.save_recent_files()
        self.update_recent_menu()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.root = ctk.CTk()
        self.root.title("Image Converter - Enhanced with SVG Support")
        
        # Set icon with fallback
        try:
            icon_path = "../icons/img_conv.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        except:
            pass  # Skip if icon not found
            
        self.root.geometry("1000x700")
        self.root.minsize(600, 500)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        # Title
        title_text = "Image Converter" + (" with SVG Support" if SVG_SUPPORT else "")
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text=title_text, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Button frame
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Buttons
        self.load_button = ctk.CTkButton(
            button_frame, 
            text="📁 Select Image", 
            command=self.load_image_dialog,
            height=40
        )
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.save_button = ctk.CTkButton(
            button_frame, 
            text="💾 Save As", 
            command=self.save_image,
            state="disabled",
            height=40
        )
        self.save_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2.5, 2.5))
        
        self.batch_button = ctk.CTkButton(
            button_frame, 
            text="📦 Batch Convert", 
            command=self.batch_convert,
            height=40
        )
        self.batch_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Quality slider
        quality_label = ctk.CTkLabel(settings_frame, text="Quality:")
        quality_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.quality_slider = ctk.CTkSlider(
            settings_frame,
            from_=10,
            to=100,
            command=self.on_quality_change
        )
        self.quality_slider.set(95)
        self.quality_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.quality_value_label = ctk.CTkLabel(settings_frame, text="95%")
        self.quality_value_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            settings_frame, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 10))
        self.progress_bar.pack_forget()  # Hide initially
        
        # Status and info frame
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            info_frame, 
            text="No image loaded", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            info_frame, 
            text="", 
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.info_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Drag and drop area
        self.drop_frame = ctk.CTkFrame(self.main_frame)
        self.drop_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        supported_text = "📥\nDrag & Drop Image Here\n\nSupported formats: JPG, PNG, BMP, GIF, ICO, WebP, TIFF"
        if SVG_SUPPORT:
            supported_text += ", SVG"
        else:
            supported_text += "\n\n⚠️ SVG support requires 'cairosvg' package"
            
        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text=supported_text,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        self.drop_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Preview area (initially hidden)
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Setup drag and drop
        self.setup_drag_drop()
        
    def create_menu_bar(self):
        """Create menu bar with File menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Open Image...", command=self.load_image_dialog, accelerator="Ctrl+O")
        file_menu.add_command(label="Save As...", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Batch Convert...", command=self.batch_convert)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_image_dialog())
        self.root.bind('<Control-s>', lambda e: self.save_image() if self.current_image else None)
    
    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="No recent files", state="disabled")
        else:
            for file_path in self.recent_files:
                filename = os.path.basename(file_path)
                self.recent_menu.add_command(
                    label=filename, 
                    command=lambda fp=file_path: self.load_image_from_path(fp)
                )
    
    def on_quality_change(self, value):
        """Handle quality slider change"""
        self.conversion_quality = int(value)
        self.quality_value_label.configure(text=f"{self.conversion_quality}%")
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
    def handle_drop(self, event):
        """Handle drag and drop events with proper file path parsing"""
        try:
            # Parse the dropped file path properly (handles spaces and special characters)
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]  # Take the first file if multiple are dropped
                # Remove curly braces if present (Windows specific)
                file_path = file_path.strip('{}')
                self.load_image_from_path(file_path)
        except Exception as e:
            messagebox.showerror("Drop Error", f"Error processing dropped file: {e}")
    
    def load_image_dialog(self):
        """Open file dialog to select an image"""
        file_types = [
            ("All Supported Images", " ".join([f"*{ext}" for ext in self.supported_formats["input"]])),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("PNG files", "*.png"),
            ("BMP files", "*.bmp"),
            ("GIF files", "*.gif"),
            ("ICO files", "*.ico"),
            ("WebP files", "*.webp"),
            ("TIFF files", "*.tiff;*.tif")
        ]
        
        if SVG_SUPPORT:
            file_types.insert(-1, ("SVG files", "*.svg"))
        
        file_types.append(("All files", "*.*"))
        
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=file_types
        )
        
        if file_path:
            self.load_image_from_path(file_path)
    
    def load_image_from_path(self, file_path):
        """Load image from file path with validation and error handling"""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "File does not exist")
                return
            
            # Validate file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats["input"]:
                if file_ext == ".svg" and not SVG_SUPPORT:
                    messagebox.showerror("Error", "SVG support requires 'cairosvg' package.\nInstall with: pip install cairosvg")
                else:
                    messagebox.showerror("Error", f"Unsupported file format: {file_ext}")
                return
            
            # Update status and show progress
            self.status_label.configure(text="Loading image...")
            self.show_progress()
            self.root.update()
            
            # Load image in a separate thread to prevent UI freezing
            threading.Thread(target=self._load_image_thread, args=(file_path,), daemon=True).start()
            
        except Exception as e:
            self.hide_progress()
            messagebox.showerror("Error", f"Unable to load image: {e}")
    
    def _load_image_thread(self, file_path):
        """Load image in background thread"""
        try:
            # Handle SVG files
            if file_path.lower().endswith('.svg') and SVG_SUPPORT:
                # Convert SVG to PNG in memory
                # Use file_obj for better Windows path handling
                with open(file_path, 'rb') as svg_file:
                    png_data = cairosvg.svg2png(file_obj=svg_file)
                from io import BytesIO
                image = Image.open(BytesIO(png_data))
            else:
                # Load regular image
                image = Image.open(file_path)
            
            # Schedule UI update in main thread
            self.root.after(0, self._update_loaded_image, image, file_path)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._handle_load_error(error_msg))
    
    def _handle_load_error(self, error_msg):
        """Handle image loading error"""
        self.hide_progress()
        messagebox.showerror("Error", f"Unable to load image: {error_msg}")
    
    def _update_loaded_image(self, image, file_path):
        """Update UI after image is loaded"""
        self.current_image = image
        self.current_filename = os.path.basename(file_path)
        self.current_file_path = file_path
        
        # Add to recent files
        self.add_to_recent_files(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Update status
        size_info = f"{image.width}x{image.height}"
        mode_info = image.mode
        format_info = image.format or Path(file_path).suffix.upper().strip('.')
        
        self.status_label.configure(text=f"Loaded: {self.current_filename}")
        self.info_label.configure(
            text=f"{size_info} • {mode_info} • {format_info} • {file_size_mb:.1f}MB"
        )
        
        # Enable save button
        self.save_button.configure(state="normal")
        
        # Update preview
        self.update_preview()
        self.hide_progress()
        
    def show_progress(self):
        """Show progress bar"""
        self.progress_bar.pack(side=tk.RIGHT, padx=(0, 10))
        self.progress_var.set(0)
        
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.pack_forget()
        
    def update_preview(self):
        """Update the image preview with proper scaling"""
        if not self.current_image:
            return
            
        try:
            # Hide drop area and show preview
            self.drop_frame.pack_forget()
            self.preview_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
            
            # Calculate preview size (max 400x400 while maintaining aspect ratio)
            preview_size = self.calculate_preview_size(self.current_image.size, (400, 400))
            
            # Create preview image
            preview_image = self.current_image.copy()
            preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(preview_image)
            
            # Update preview label
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Preview error: {e}")
    
    def calculate_preview_size(self, original_size, max_size):
        """Calculate preview size maintaining aspect ratio"""
        orig_width, orig_height = original_size
        max_width, max_height = max_size
        
        # Calculate aspect ratio
        ratio = min(max_width / orig_width, max_height / orig_height)
        
        return (int(orig_width * ratio), int(orig_height * ratio))
    
    def save_image(self):
        """Save the current image with format conversion"""
        if not self.current_image:
            messagebox.showerror("Error", "No image loaded")
            return
        
        try:
            # Prepare initial filename without extension
            initial_name = os.path.splitext(self.current_filename)[0]
            
            # Open save dialog
            save_path = filedialog.asksaveasfilename(
                title="Save Image As",
                defaultextension=".png",
                filetypes=self.supported_formats["output"],
                initialfile=initial_name
            )
            
            if save_path:
                # Update status and show progress
                self.status_label.configure(text="Saving image...")
                self.show_progress()
                self.root.update()
                
                # Save in background thread
                threading.Thread(target=self._save_image_thread, args=(save_path,), daemon=True).start()
                
        except Exception as e:
            self.hide_progress()
            messagebox.showerror("Error", f"Unable to save image: {e}")
    
    def _save_image_thread(self, save_path):
        """Save image in background thread"""
        try:
            # Update progress
            self.root.after(0, lambda: self.progress_var.set(25))
            
            # Handle ICO format specially (needs specific sizes)
            if save_path.lower().endswith('.ico'):
                self._save_as_ico(save_path)
            else:
                # For other formats, convert if necessary
                image_to_save = self.current_image.copy()
                
                self.root.after(0, lambda: self.progress_var.set(50))
                
                # Convert RGBA to RGB for JPEG
                if save_path.lower().endswith(('.jpg', '.jpeg')) and image_to_save.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image_to_save.size, (255, 255, 255))
                    background.paste(image_to_save, mask=image_to_save.split()[-1] if image_to_save.mode == 'RGBA' else None)
                    image_to_save = background
                
                self.root.after(0, lambda: self.progress_var.set(75))
                
                # Save with quality settings for lossy formats
                if save_path.lower().endswith(('.jpg', '.jpeg', '.webp')):
                    image_to_save.save(save_path, quality=self.conversion_quality, optimize=True)
                else:
                    image_to_save.save(save_path)
            
            self.root.after(0, lambda: self.progress_var.set(100))
            
            # Update UI in main thread
            self.root.after(0, lambda: self._save_complete(save_path))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._handle_save_error(error_msg))
    
    def _handle_save_error(self, error_msg):
        """Handle save error"""
        self.hide_progress()
        messagebox.showerror("Save Error", f"Unable to save image: {error_msg}")
    
    # def _save_as_ico(self, save_path):
        # """Save image as ICO format with multiple sizes"""
        # image = self.current_image.copy()
        
        # # ICO files can contain multiple sizes
        # sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # # Convert to RGBA if not already
        # if image.mode != 'RGBA':
            # image = image.convert('RGBA')
        
        # image.save(save_path, format='ICO', sizes=sizes)


    def _save_as_ico(self, save_path):
        """Save image as ICO format with multiple sizes"""
        image = self.current_image.copy()
        
        # ICO files can contain multiple sizes
        sizes = [(32, 32),(128, 128),(256, 256)]
        
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        image.save(save_path, format='ICO', sizes=sizes)

    
    def _save_complete(self, save_path):
        """Handle save completion"""
        filename = os.path.basename(save_path)
        self.status_label.configure(text=f"Saved: {filename}")
        self.hide_progress()
        messagebox.showinfo("Success", f"Image saved successfully as:\n{filename}")
    
    def batch_convert(self):
        """Open batch conversion dialog"""
        BatchConvertDialog(self.root)
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.current_image = None
        self.current_filename = ""
        self.current_file_path = ""
        self.save_button.configure(state="disabled")
        self.status_label.configure(text="No image loaded")
        self.info_label.configure(text="")
        self.preview_frame.pack_forget()
        self.drop_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.hide_progress()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class BatchConvertDialog:
    def __init__(self, parent):
        self.parent = parent
        self.input_files = []
        self.output_format = "png"
        self.output_directory = ""
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup batch conversion dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Batch Convert Images")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Batch Image Conversion",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Input files section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(input_frame, text="Input Files:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # File list
        self.file_listbox = tk.Listbox(input_frame, height=8)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Input buttons
        input_buttons_frame = ctk.CTkFrame(input_frame)
        input_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            input_buttons_frame,
            text="Add Files",
            command=self.add_files
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkButton(
            input_buttons_frame,
            text="Remove Selected",
            command=self.remove_selected
        ).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(
            input_buttons_frame,
            text="Clear All",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Output settings
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(output_frame, text="Output Settings:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Format selection
        format_frame = ctk.CTkFrame(output_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        ctk.CTkLabel(format_frame, text="Format:").pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        self.format_var = tk.StringVar(value="png")
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            variable=self.format_var,
            values=["png", "jpg", "bmp", "gif", "webp", "tiff", "ico"]
        )
        format_menu.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        
        # Output directory
        dir_frame = ctk.CTkFrame(output_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        self.dir_entry = ctk.CTkEntry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5), pady=10)
        
        ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self.browse_output_dir,
            width=80
        ).pack(side=tk.LEFT, padx=(0, 10), pady=10)
        
        # Progress
        self.batch_progress = ttk.Progressbar(
            output_frame,
            mode='determinate'
        )
        self.batch_progress.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Start Conversion",
            command=self.start_conversion
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 5), pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 10), pady=10)
    
    def add_files(self):
        """Add files to batch conversion list"""
        file_types = [
            ("All Supported Images", "*.jpg *.jpeg *.png *.bmp *.gif *.ico *.webp *.tiff *.tif" + (" *.svg" if SVG_SUPPORT else "")),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Images for Batch Conversion",
            filetypes=file_types
        )
        
        for file_path in files:
            if file_path not in self.input_files:
                self.input_files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
    
    def remove_selected(self):
        """Remove selected files from list"""
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            del self.input_files[index]
            self.file_listbox.delete(index)
    
    def clear_all(self):
        """Clear all files from list"""
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def start_conversion(self):
        """Start batch conversion process"""
        if not self.input_files:
            messagebox.showerror("Error", "No input files selected")
            return
        
        output_dir = self.dir_entry.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please select output directory")
            return
        
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", "Output directory does not exist")
            return
        
        output_format = self.format_var.get()
        
        # Start conversion in background thread
        threading.Thread(
            target=self._batch_convert_thread,
            args=(self.input_files.copy(), output_dir, output_format),
            daemon=True
        ).start()
    
    def _batch_convert_thread(self, files, output_dir, output_format):
        """Perform batch conversion in background thread"""
        total_files = len(files)
        converted = 0
        errors = []
        
        for i, file_path in enumerate(files):
            try:
                # Update progress
                progress = (i / total_files) * 100
                self.dialog.after(0, lambda p=progress: self.batch_progress.configure(value=p))
                
                # Load image
                if file_path.lower().endswith('.svg') and SVG_SUPPORT:
                    with open(file_path, 'rb') as svg_file:
                        png_data = cairosvg.svg2png(file_obj=svg_file)
                    from io import BytesIO
                    image = Image.open(BytesIO(png_data))
                else:
                    image = Image.open(file_path)
                
                # Prepare output filename
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"{base_name}.{output_format}"
                output_path = os.path.join(output_dir, output_filename)
                
                # Convert and save
                if output_format == 'ico':
                    # Handle ICO format specially
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                    image.save(output_path, format='ICO', sizes=sizes)
                elif output_format in ['jpg', 'jpeg'] and image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                    image.save(output_path, quality=95, optimize=True)
                else:
                    if output_format in ['jpg', 'jpeg', 'webp']:
                        image.save(output_path, quality=95, optimize=True)
                    else:
                        image.save(output_path)
                
                converted += 1
                
            except Exception as e:
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")
        
        # Update progress to 100%
        self.dialog.after(0, lambda: self.batch_progress.configure(value=100))
        
        # Show completion message
        self.dialog.after(0, lambda: self._show_batch_completion(converted, total_files, errors))
    
    def _show_batch_completion(self, converted, total, errors):
        """Show batch conversion completion message"""
        message = f"Batch conversion completed!\n\nConverted: {converted}/{total} files"
        
        if errors:
            message += f"\n\nErrors ({len(errors)}):"
            for error in errors[:5]:  # Show first 5 errors
                message += f"\n• {error}"
            if len(errors) > 5:
                message += f"\n... and {len(errors) - 5} more errors"
        
        if errors:
            messagebox.showwarning("Batch Conversion Complete", message)
        else:
            messagebox.showinfo("Batch Conversion Complete", message)


# Command line conversion functions
def is_running_from_terminal():
    """Check if the script is running from a terminal/console"""
    try:
        # Check if stdout is attached to a terminal
        return sys.stdout.isatty()
    except:
        return False

def show_error_message(message, is_terminal=None):
    """Show error message - console for terminal, messagebox for GUI"""
    if is_terminal is None:
        is_terminal = is_running_from_terminal()
    
    if is_terminal or tk is None or messagebox is None:
        print(f"Error: {message}")
    else:
        # Initialize tkinter for messagebox if not already done
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Image Converter Error", message)
            root.destroy()
        except:
            print(f"Error: {message}")

def show_success_message(message, is_terminal=None):
    """Show success message - console for terminal, messagebox for GUI"""
    if is_terminal is None:
        is_terminal = is_running_from_terminal()
    
    if is_terminal or tk is None or messagebox is None:
        print(message)
    else:
        # Initialize tkinter for messagebox if not already done
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showinfo("Image Converter", message)
            root.destroy()
        except:
            print(message)

def convert_to_ico_cli(input_path):
    """Convert image to ICO format via command line"""
    is_terminal = is_running_from_terminal()
    
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            show_error_message(f"File does not exist: {input_path}", is_terminal)
            return False
        
        # Validate file extension
        supported_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".ico", ".webp", 
                              ".ppm", ".pgm", ".pnm", ".tiff", ".tif"]
        if SVG_SUPPORT:
            supported_extensions.append(".svg")
        
        file_ext = Path(input_path).suffix.lower()
        if file_ext not in supported_extensions:
            if file_ext == ".svg" and not SVG_SUPPORT:
                show_error_message("SVG support requires 'cairosvg' package. Install with: pip install cairosvg", is_terminal)
            else:
                show_error_message(f"Unsupported file format: {file_ext}", is_terminal)
            return False
        
        # Prepare output path
        input_path_obj = Path(input_path)
        output_path = input_path_obj.parent / (input_path_obj.stem + ".ico")
        
        # Check if output file already exists
        if output_path.exists():
            if is_terminal:
                response = input(f"Output file '{output_path.name}' already exists. Overwrite? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("Conversion cancelled.")
                    return False
            else:
                # For right-click mode, automatically overwrite (user expects this behavior)
                # If we want to ask, we can show a message box
                if tk and messagebox:
                    try:
                        root = tk.Tk()
                        root.withdraw()
                        result = messagebox.askyesno("File Exists", 
                            f"Output file '{output_path.name}' already exists. Overwrite?")
                        root.destroy()
                        if not result:
                            return False
                    except:
                        # If messagebox fails, just overwrite
                        pass
        
        # Load and convert image
        if is_terminal:
            print(f"Converting '{input_path_obj.name}' to ICO format...")
        
        # Handle SVG files
        if input_path.lower().endswith('.svg') and SVG_SUPPORT:
            with open(input_path, 'rb') as svg_file:
                png_data = cairosvg.svg2png(file_obj=svg_file)
            from io import BytesIO
            image = Image.open(BytesIO(png_data))
        else:
            image = Image.open(input_path)
        
        # Convert to RGBA if not already (required for ICO)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Save as ICO with multiple sizes
        sizes = [(32, 32), (128, 128), (256, 256)]
        image.save(str(output_path), format='ICO', sizes=sizes)
        
        # Show success message
        success_msg = f"Successfully converted to: {output_path.name}"
        show_success_message(success_msg, is_terminal)
        
        return True
        
    except Exception as e:
        error_msg = f"Failed to convert image: {str(e)}"
        show_error_message(error_msg, is_terminal)
        return False

def parse_command_line():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Image to ICO Converter",
        epilog="If no arguments provided, GUI mode will start."
    )
    parser.add_argument('input_file', nargs='?', 
                       help='Input image file to convert to ICO')
    parser.add_argument('--version', action='version', version='Image Converter 1.0')
    
    return parser.parse_args()


# Create and run the application
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_command_line()
    
    # Check for SVG support and show warning if not available
    if not SVG_SUPPORT:
        if is_running_from_terminal():
            print("Warning: SVG support not available. Install with: pip install cairosvg")
    
    # If input file provided, run in CLI mode
    if args.input_file:
        success = convert_to_ico_cli(args.input_file)
        sys.exit(0 if success else 1)
    else:
        # No arguments provided, start GUI
        if not GUI_AVAILABLE:
            print("Error: GUI libraries not available.")
            print("Please install required dependencies: pip install customtkinter pillow tkinterdnd2")
            print("Or use command line mode: python img_conv_ctk.pyw <image_file>")
            sys.exit(1)
        
        app = ImageConverter()
        app.run()
