import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from main import convert_to_obj
from pyawd.PyAwdLogger import logger


class AWDConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AWD to OBJ Converter")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        # Configure high DPI scaling
        try:
            self.root.tk.call('tk', 'scaling', 1.2)
        except:
            pass
        
        # Variables
        self.input_files = []
        self.output_directory = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with better styling
        title_label = ttk.Label(main_frame, text="AWD to OBJ Converter", 
                               font=("Segoe UI", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Left panel - File selection
        left_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="12")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)
        
        # File selection buttons in a horizontal layout
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="📁 Select Files", 
                  command=self.select_files).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 4))
        
        ttk.Button(button_frame, text="📂 Select Folder", 
                  command=self.select_directory).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(4, 0))
        
        # File count label
        self.file_count_label = ttk.Label(left_frame, text="No files selected", 
                                         font=("Segoe UI", 9))
        self.file_count_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # File list with frame for better appearance
        list_frame = ttk.Frame(left_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(list_frame, height=10, font=("Consolas", 9))
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Clear button
        ttk.Button(left_frame, text="🗑️ Clear All", 
                  command=self.clear_files).grid(row=3, column=0, sticky=tk.W)
        
        # Right panel - Export settings and controls
        right_frame = ttk.LabelFrame(main_frame, text="Export Settings", padding="12")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        right_frame.columnconfigure(0, weight=1)
        
        # Output directory section
        ttk.Label(right_frame, text="Output Directory:", 
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Directory selection frame
        dir_frame = ttk.Frame(right_frame)
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(dir_frame, textvariable=self.output_directory, 
                                     state="readonly", font=("Consolas", 9))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.select_output_directory).grid(row=0, column=1)
        
        # Conversion controls
        controls_frame = ttk.Frame(right_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        controls_frame.columnconfigure(0, weight=1)
        
        # Convert button with better styling
        self.convert_button = ttk.Button(controls_frame, text="🔄 Convert to OBJ", 
                                        command=self.start_conversion)
        self.convert_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress section
        progress_frame = ttk.LabelFrame(controls_frame, text="Progress", padding="8")
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready to convert files", 
                                     font=("Segoe UI", 9))
        self.status_label.grid(row=1, column=0)
    
    def select_files(self):
        """Select individual AWD files"""
        files = filedialog.askopenfilenames(
            title="Select AWD Files",
            filetypes=[("AWD files", "*.awd"), ("All files", "*.*")]
        )
        
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
        
        self.update_file_list()
    
    def select_directory(self):
        """Select directory containing AWD files"""
        directory = filedialog.askdirectory(title="Select Directory with AWD Files")
        
        if directory:
            awd_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                        if f.lower().endswith('.awd')]
            
            for file in awd_files:
                if file not in self.input_files:
                    self.input_files.append(file)
            
            self.update_file_list()
    
    def clear_files(self):
        """Clear the file list"""
        self.input_files.clear()
        self.update_file_list()
    
    def update_file_list(self):
        """Update the listbox with current files"""
        self.file_listbox.delete(0, tk.END)
        for file in self.input_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
        
        # Update file count label
        count = len(self.input_files)
        if count == 0:
            self.file_count_label.configure(text="No files selected")
        elif count == 1:
            self.file_count_label.configure(text="1 file selected")
        else:
            self.file_count_label.configure(text=f"{count} files selected")
    
    def select_output_directory(self):
        """Select output directory for OBJ files"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
    
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please select AWD files to convert.")
            return
        
        if not self.output_directory.get():
            messagebox.showwarning("No Output Directory", "Please select an output directory.")
            return
        
        # Disable convert button and start progress
        self.convert_button.configure(state="disabled")
        self.progress.start()
        self.status_label.configure(text="Converting files...")
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def convert_files(self):
        """Convert all selected files"""
        failed_files = []
        total_files = len(self.input_files)
        
        for i, input_file in enumerate(self.input_files):
            try:
                # Update status
                filename = os.path.basename(input_file)
                self.root.after(0, lambda f=filename, i=i, t=total_files: 
                               self.status_label.configure(text=f"Converting {f} ({i+1}/{t})"))
                
                # Generate output filename
                output_filename = os.path.splitext(os.path.basename(input_file))[0] + ".obj"
                output_path = os.path.join(self.output_directory.get(), output_filename)
                
                # Convert file
                convert_to_obj(input_file, output_path)
                
            except Exception as e:
                logger.error(f"Failed to convert {input_file}: {str(e)}")
                failed_files.append(os.path.basename(input_file))
        
        # Update UI on main thread
        self.root.after(0, lambda: self.conversion_complete(failed_files, total_files))
    
    def conversion_complete(self, failed_files, total_files):
        """Handle conversion completion"""
        self.progress.stop()
        self.convert_button.configure(state="normal")
        
        success_count = total_files - len(failed_files)
        
        if failed_files:
            message = f"Conversion complete!\n\nSuccessful: {success_count}/{total_files}\nFailed files: {', '.join(failed_files)}"
            messagebox.showwarning("Conversion Complete", message)
        else:
            message = f"All {total_files} files converted successfully!"
            messagebox.showinfo("Conversion Complete", message)
        
        self.status_label.configure(text="Ready to convert files")


def main():
    root = tk.Tk()
    app = AWDConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()