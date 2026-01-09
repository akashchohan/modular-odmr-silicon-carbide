import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time
from tkinter import messagebox
import threading
from datetime import datetime

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            relief="flat",
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(bg="#1976D2")

    def on_leave(self, e):
        self.configure(bg="#2196F3")

class RFGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RF Signal Generator")
        self.root.geometry("900x700")
        self.root.configure(bg="#F0F0F0")
        
        # Initialize variables
        self.serial_port = None
        self.is_connected = False
        self.sweep_running = False
        self.sweep_thread = None
        
        # Initialize UI elements as class attributes
        self.port_combo = None
        self.connect_btn = None
        self.freq_entry = None
        self.start_freq = None
        self.stop_freq = None
        self.step_size = None
        self.dwell_time = None
        self.sweep_btn = None
        self.status_label = None
        self.console = None
        
        # Create main container with padding
        self.main_frame = tk.Frame(root, bg="#F0F0F0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI elements
        self.create_title()
        self.create_console()  # Create console first
        self.create_connection_frame()
        self.create_frequency_control()
        self.create_sweep_control()
        self.create_status_frame()

    def create_title(self):
        title_label = tk.Label(
            self.main_frame,
            text="RF Signal Generator",
            font=("Segoe UI", 24, "bold"),
            bg="#F0F0F0",
            fg="#1565C0"
        )
        title_label.pack(pady=(0, 20))

    def create_console(self):
        console_frame = tk.LabelFrame(
            self.main_frame,
            text="Debug Console",
            font=("Segoe UI", 12, "bold"),
            bg="#F0F0F0",
            fg="#1565C0",
            padx=10,
            pady=10
        )
        console_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        
        self.console = tk.Text(
            console_frame,
            height=10,
            font=("Consolas", 10),
            bg="#263238",
            fg="#FFFFFF",
            wrap=tk.WORD
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
    def create_connection_frame(self):
        conn_frame = tk.LabelFrame(
            self.main_frame,
            text="Connection",
            font=("Segoe UI", 12, "bold"),
            bg="#F0F0F0",
            fg="#1565C0",
            padx=10,
            pady=10
        )
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        port_frame = tk.Frame(conn_frame, bg="#F0F0F0")
        port_frame.pack(fill=tk.X)
        
        tk.Label(
            port_frame,
            text="Port:",
            font=("Segoe UI", 10),
            bg="#F0F0F0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.port_combo = ttk.Combobox(
            port_frame,
            width=15,
            font=("Segoe UI", 10)
        )
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = ModernButton(
            port_frame,
            text="Connect",
            command=self.toggle_connection
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ModernButton(
            port_frame,
            text="Refresh Ports",
            command=self.refresh_ports
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_ports()
        
    def create_frequency_control(self):
        freq_frame = tk.LabelFrame(
            self.main_frame,
            text="Frequency Control",
            font=("Segoe UI", 12, "bold"),
            bg="#F0F0F0",
            fg="#1565C0",
            padx=10,
            pady=10
        )
        freq_frame.pack(fill=tk.X, pady=(0, 10))
        
        entry_frame = tk.Frame(freq_frame, bg="#F0F0F0")
        entry_frame.pack(fill=tk.X)
        
        tk.Label(
            entry_frame,
            text="Frequency (MHz):",
            font=("Segoe UI", 10),
            bg="#F0F0F0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.freq_entry = tk.Entry(
            entry_frame,
            width=10,
            font=("Segoe UI", 10),
            justify="right"
        )
        self.freq_entry.insert(0, "50")
        self.freq_entry.pack(side=tk.LEFT, padx=5)
        
        set_freq_btn = ModernButton(
            entry_frame,
            text="Set Frequency",
            command=self.set_frequency
        )
        set_freq_btn.pack(side=tk.LEFT, padx=5)

    def create_sweep_control(self):
        sweep_frame = tk.LabelFrame(
            self.main_frame,
            text="Sweep Control",
            font=("Segoe UI", 12, "bold"),
            bg="#F0F0F0",
            fg="#1565C0",
            padx=10,
            pady=10
        )
        sweep_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create grid for sweep controls
        for i in range(2):
            sweep_frame.grid_columnconfigure(i*2+1, weight=1)
        
        labels = [
            ("Start (MHz):", 0, 0),
            ("Stop (MHz):", 0, 2),
            ("Step (MHz):", 1, 0),
            ("Dwell (ms):", 1, 2)
        ]
        
        for text, row, col in labels:
            tk.Label(
                sweep_frame,
                text=text,
                font=("Segoe UI", 10),
                bg="#F0F0F0"
            ).grid(row=row, column=col, padx=5, pady=5)
        
        # Create and place entry widgets
        self.start_freq = self.create_entry(sweep_frame, "35", 0, 1)
        self.stop_freq = self.create_entry(sweep_frame, "4400", 0, 3)
        self.step_size = self.create_entry(sweep_frame, "100", 1, 1)
        self.dwell_time = self.create_entry(sweep_frame, "100", 1, 3)
        
        self.sweep_btn = ModernButton(
            sweep_frame,
            text="Start Sweep",
            command=self.toggle_sweep
        )
        self.sweep_btn.grid(row=2, column=0, columnspan=4, pady=10)

    def create_entry(self, parent, default_value, row, col):
        entry = tk.Entry(
            parent,
            width=10,
            font=("Segoe UI", 10),
            justify="right"
        )
        entry.insert(0, default_value)
        entry.grid(row=row, column=col, padx=5, pady=5)
        return entry

    def create_status_frame(self):
        status_frame = tk.LabelFrame(
            self.main_frame,
            text="Status",
            font=("Segoe UI", 12, "bold"),
            bg="#F0F0F0",
            fg="#1565C0",
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Disconnected",
            font=("Segoe UI", 10),
            bg="#F0F0F0",
            fg="#D32F2F"
        )
        self.status_label.pack()

    def log_debug(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
        self.log_debug(f"Available ports: {', '.join(ports)}")
            
    def toggle_connection(self):
        if not self.is_connected:
            try:
                port = self.port_combo.get()
                self.serial_port = serial.Serial(port, 115200, timeout=1)
                time.sleep(2)  # Wait for Arduino reset
                self.is_connected = True
                self.connect_btn.configure(text="Disconnect")
                self.status_label.configure(text="Connected", fg="#2E7D32")
                self.log_debug(f"Connected to {port}")
            except Exception as e:
                self.log_debug(f"Connection error: {str(e)}")
                messagebox.showerror("Error", f"Failed to connect: {str(e)}")
        else:
            self.disconnect()
            
    def disconnect(self):
        if self.serial_port:
            self.serial_port.close()
        self.is_connected = False
        self.connect_btn.configure(text="Connect")
        self.status_label.configure(text="Disconnected", fg="#D32F2F")
        self.log_debug("Disconnected from device")
            
    def set_frequency(self):
        if not self.is_connected:
            self.log_debug("Error: Not connected to device")
            messagebox.showerror("Error", "Please connect to device first")
            return
            
        try:
            freq = float(self.freq_entry.get())
            if 35 <= freq <= 4400:
                command = f"FREQ:{freq:.3f}\n"
                self.log_debug(f"Sending command: {command.strip()}")
                self.serial_port.write(command.encode())
                
                # Read debug information
                while True:
                    response = self.serial_port.readline().decode().strip()
                    if not response:
                        break
                    self.log_debug(f"Device response: {response}")
                    if response == "OK":
                        self.status_label.configure(
                            text=f"Frequency set to {freq} MHz",
                            fg="#2E7D32"
                        )
                        break
                    elif response.startswith("ERROR"):
                        messagebox.showerror("Error", response)
                        break
            else:
                self.log_debug("Error: Frequency out of range")
                messagebox.showerror("Error", "Frequency must be between 35 and 4400 MHz")
        except ValueError:
            self.log_debug("Error: Invalid frequency value")
            messagebox.showerror("Error", "Invalid frequency value")
        except Exception as e:
            self.log_debug(f"Error setting frequency: {str(e)}")
            messagebox.showerror("Error", f"Failed to set frequency: {str(e)}")
            
    def toggle_sweep(self):
        if not self.is_connected:
            self.log_debug("Error: Not connected to device")
            messagebox.showerror("Error", "Please connect to device first")
            return
            
        if not self.sweep_running:
            try:
                start = float(self.start_freq.get())
                stop = float(self.stop_freq.get())
                step = float(self.step_size.get())
                dwell = float(self.dwell_time.get())
                
                if not (35 <= start <= 4400 and 35 <= stop <= 4400):
                    self.log_debug("Error: Sweep frequencies out of range")
                    messagebox.showerror("Error", "Frequencies must be between 35 and 4400 MHz")
                    return
                    
                self.sweep_running = True
                self.sweep_btn.configure(text="Stop Sweep")
                self.log_debug(f"Starting sweep: {start}MHz to {stop}MHz, step={step}MHz, dwell={dwell}ms")
                
                # Start sweep in separate thread
                self.sweep_thread = threading.Thread(
                    target=self.run_sweep,
                    args=(start, stop, step, dwell)
                )
                self.sweep_thread.daemon = True
                self.sweep_thread.start()
            except ValueError:
                self.log_debug("Error: Invalid sweep parameters")
                messagebox.showerror("Error", "Invalid sweep parameters")
        else:
            self.sweep_running = False
            self.sweep_btn.configure(text="Start Sweep")
            self.log_debug("Sweep stopped")
            
    def run_sweep(self, start, stop, step, dwell):
        current = start
        while current <= stop and self.sweep_running:
            self.freq_entry.delete(0, tk.END)
            self.freq_entry.insert(0, f"{current:.3f}")
            self.set_frequency()
            time.sleep(dwell / 1000)  # Convert ms to seconds
            current += step
            
        if self.sweep_running:
            self.sweep_running = False
            self.root.after(0, lambda: self.sweep_btn.configure(text="Start Sweep"))
            self.log_debug("Sweep completed")

def main():
    root = tk.Tk()
    app = RFGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 