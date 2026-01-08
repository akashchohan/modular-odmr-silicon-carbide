import sys
import time
import numpy as np
import pyvisa
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QComboBox, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QStatusBar, QMessageBox,
                             QGridLayout, QLineEdit, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import pyqtgraph as pg


class TriggerIndicator(QFrame):
    """Custom widget to show trigger status with color indication"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(20, 20)
        self.setMaximumSize(20, 20)
        self.status = "WAITING"  # WAITING, TRIGGERED, TIMEOUT
        
    def paintEvent(self, event):
        painter = pg.QtGui.QPainter(self)
        
        if self.status == "WAITING":
            color = QColor(255, 165, 0)  # Orange
        elif self.status == "TRIGGERED":
            color = QColor(0, 255, 0)     # Green
        elif self.status == "TIMEOUT":
            color = QColor(255, 0, 0)     # Red
        else:
            color = QColor(128, 128, 128)  # Gray
            
        painter.setBrush(pg.QtGui.QBrush(color))
        painter.setPen(pg.QtGui.QPen(Qt.black, 1))
        painter.drawEllipse(2, 2, 16, 16)
        
    def set_status(self, status):
        self.status = status
        self.update()


class RedPitayaOscilloscope(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Red Pitaya Dual Channel Oscilloscope")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize VISA resource manager
        self.rm = pyvisa.ResourceManager('@py')
        self.device = None
        self.connected = False
        
        # Initialize data for both channels
        self.data_ch1 = np.zeros(1024)
        self.data_ch2 = np.zeros(1024)
        self.time_data = np.linspace(0, 131.072, 1024)
        
        # Setup UI
        self.setup_ui()
        
        # Setup timer for updating plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        
        # Decimation factors and corresponding sample rates
        self.decimation_factors = {
            "1": "125 MS/s",
            "8": "15.6 MS/s",
            "64": "1.95 MS/s",
            "1024": "122 kS/s",
            "8192": "15.3 kS/s",
            "65536": "1.9 kS/s"
        }
        
        # Update sample rate display
        self.update_sample_rate_display()
        
    def setup_ui(self):
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connection group
        connection_group = QGroupBox("Connection")
        connection_layout = QGridLayout()
        connection_group.setLayout(connection_layout)
        
        self.ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit("169.254.195.129")
        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit("5000")
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)
        
        connection_layout.addWidget(self.ip_label, 0, 0)
        connection_layout.addWidget(self.ip_input, 0, 1)
        connection_layout.addWidget(self.port_label, 0, 2)
        connection_layout.addWidget(self.port_input, 0, 3)
        connection_layout.addWidget(self.connect_button, 0, 4)
        
        # Acquisition settings group
        acq_group = QGroupBox("Acquisition Settings")
        acq_layout = QGridLayout()
        acq_group.setLayout(acq_layout)
        
        # Display channels checkboxes
        self.show_ch1_checkbox = QCheckBox("Show Channel 1")
        self.show_ch1_checkbox.setChecked(True)
        self.show_ch2_checkbox = QCheckBox("Show Channel 2")
        self.show_ch2_checkbox.setChecked(True)
        
        # Trigger settings
        self.trigger_source_label = QLabel("Trigger Source:")
        self.trigger_source_select = QComboBox()
        self.trigger_source_select.addItems(["DISABLED", "EXT_PE", "EXT_NE", "CH1_PE", "CH1_NE", "CH2_PE", "CH2_NE"])
        self.trigger_source_select.setToolTip("PE: Positive Edge, NE: Negative Edge")
        
        self.trigger_level_label = QLabel("Trigger Level (V):")
        self.trigger_level_input = QDoubleSpinBox()
        self.trigger_level_input.setRange(-20.0, 20.0)
        self.trigger_level_input.setSingleStep(0.1)
        self.trigger_level_input.setValue(0.5)
        self.trigger_level_input.valueChanged.connect(self.update_trigger_level_line)
        
        # Trigger indicator and test button
        self.trigger_indicator_label = QLabel("Trigger Status:")
        self.trigger_indicator = TriggerIndicator()
        self.trigger_test_button = QPushButton("Test Trigger")
        self.trigger_test_button.clicked.connect(self.run_trigger_test)
        self.trigger_test_button.setEnabled(False)
        
        # Horizontal settings
        self.decimation_label = QLabel("Decimation:")
        self.decimation_select = QComboBox()
        self.decimation_select.addItems(["1", "8", "64", "1024", "8192", "65536"])
        self.decimation_select.currentIndexChanged.connect(self.update_sample_rate_display)
        
        self.sample_rate_label = QLabel("Sample Rate:")
        self.sample_rate_display = QLabel("125 MS/s")
        
        # Custom acquisition points
        self.buffer_size_label = QLabel("Buffer Size:")
        self.buffer_size_input = QSpinBox()
        self.buffer_size_input.setRange(10, 16384)
        self.buffer_size_input.setSingleStep(100)
        self.buffer_size_input.setValue(1024)
        self.buffer_size_input.setToolTip("Set custom acquisition points (10-16384)")
        
        # Pre-trigger samples
        self.pretrigger_label = QLabel("Pre-trigger Samples:")
        self.pretrigger_input = QSpinBox()
        self.pretrigger_input.setRange(0, 8192)
        self.pretrigger_input.setSingleStep(128)
        self.pretrigger_input.setValue(0)
        
        # Grid layout for acquisition settings
        acq_layout.addWidget(self.show_ch1_checkbox, 0, 0)
        acq_layout.addWidget(self.show_ch2_checkbox, 0, 1)
        acq_layout.addWidget(self.trigger_source_label, 0, 2)
        acq_layout.addWidget(self.trigger_source_select, 0, 3)
        acq_layout.addWidget(self.trigger_level_label, 0, 4)
        acq_layout.addWidget(self.trigger_level_input, 0, 5)
        
        acq_layout.addWidget(self.trigger_indicator_label, 1, 0)
        acq_layout.addWidget(self.trigger_indicator, 1, 1)
        acq_layout.addWidget(self.trigger_test_button, 1, 2)
        
        acq_layout.addWidget(self.decimation_label, 2, 0)
        acq_layout.addWidget(self.decimation_select, 2, 1)
        acq_layout.addWidget(self.sample_rate_label, 2, 2)
        acq_layout.addWidget(self.sample_rate_display, 2, 3)
        acq_layout.addWidget(self.buffer_size_label, 2, 4)
        acq_layout.addWidget(self.buffer_size_input, 2, 5)
        acq_layout.addWidget(self.pretrigger_label, 3, 0)
        acq_layout.addWidget(self.pretrigger_input, 3, 1)
        
        # Measurement settings
        measure_group = QGroupBox("Measurements")
        measure_layout = QGridLayout()
        measure_group.setLayout(measure_layout)
        
        # Channel 1 Measurements
        self.ch1_label = QLabel("Channel 1:")
        self.ch1_freq_display = QLabel("Frequency: N/A")
        self.ch1_vpp_display = QLabel("Vpp: N/A")
        self.ch1_vrms_display = QLabel("Vrms: N/A")
        
        # Channel 2 Measurements
        self.ch2_label = QLabel("Channel 2:")
        self.ch2_freq_display = QLabel("Frequency: N/A")
        self.ch2_vpp_display = QLabel("Vpp: N/A")
        self.ch2_vrms_display = QLabel("Vrms: N/A")
        
        # Measurement options
        self.show_freq_checkbox = QCheckBox("Measure Frequency")
        self.show_freq_checkbox.setChecked(True)
        self.show_vpp_checkbox = QCheckBox("Measure Vpp")
        self.show_vpp_checkbox.setChecked(True)
        self.show_vrms_checkbox = QCheckBox("Measure Vrms")
        self.show_vrms_checkbox.setChecked(True)
        
        # Add to layout
        measure_layout.addWidget(self.show_freq_checkbox, 0, 0)
        measure_layout.addWidget(self.show_vpp_checkbox, 0, 1)
        measure_layout.addWidget(self.show_vrms_checkbox, 0, 2)
        
        measure_layout.addWidget(self.ch1_label, 1, 0)
        measure_layout.addWidget(self.ch1_freq_display, 1, 1)
        measure_layout.addWidget(self.ch1_vpp_display, 1, 2)
        measure_layout.addWidget(self.ch1_vrms_display, 1, 3)
        
        measure_layout.addWidget(self.ch2_label, 2, 0)
        measure_layout.addWidget(self.ch2_freq_display, 2, 1)
        measure_layout.addWidget(self.ch2_vpp_display, 2, 2)
        measure_layout.addWidget(self.ch2_vrms_display, 2, 3)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.acquire_button = QPushButton("Single Acquisition")
        self.acquire_button.clicked.connect(self.single_acquisition)
        self.acquire_button.setEnabled(False)
        
        self.continuous_button = QPushButton("Start Continuous")
        self.continuous_button.clicked.connect(self.toggle_continuous)
        self.continuous_button.setEnabled(False)
        self.continuous_mode = False
        
        self.auto_scale_button = QPushButton("Auto Scale")
        self.auto_scale_button.clicked.connect(self.auto_scale)
        self.auto_scale_button.setEnabled(False)
        
        control_layout.addWidget(self.acquire_button)
        control_layout.addWidget(self.continuous_button)
        control_layout.addWidget(self.auto_scale_button)
        
        # Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Voltage', 'V')
        self.plot_widget.setLabel('bottom', 'Time', 's')
        self.plot_widget.showGrid(x=True, y=True)
        
        # Create plot curves for both channels
        self.plot_curve_ch1 = self.plot_widget.plot(self.time_data, self.data_ch1, pen=pg.mkPen('y', width=2), name='CH1')
        self.plot_curve_ch2 = self.plot_widget.plot(self.time_data, self.data_ch2, pen=pg.mkPen('c', width=2), name='CH2')
        
        # Add legend
        self.legend = self.plot_widget.addLegend()
        
        # Add trigger level line
        self.trigger_line = pg.InfiniteLine(
            pos=self.trigger_level_input.value(), 
            angle=0, 
            pen=pg.mkPen('r', width=2, style=Qt.DashLine)
        )
        self.plot_widget.addItem(self.trigger_line)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected")
        
        # Add widgets to main layout
        main_layout.addWidget(connection_group)
        main_layout.addWidget(acq_group)
        main_layout.addWidget(measure_group)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.plot_widget, stretch=1)
        
        # Connect channel visibility checkboxes
        self.show_ch1_checkbox.stateChanged.connect(self.update_channel_visibility)
        self.show_ch2_checkbox.stateChanged.connect(self.update_channel_visibility)
    
    def update_channel_visibility(self):
        """Update the visibility of plot curves based on checkboxes"""
        self.plot_curve_ch1.setVisible(self.show_ch1_checkbox.isChecked())
        self.plot_curve_ch2.setVisible(self.show_ch2_checkbox.isChecked())
    
    def update_sample_rate_display(self):
        decimation = self.decimation_select.currentText()
        sample_rate = self.decimation_factors.get(decimation, "Unknown")
        self.sample_rate_display.setText(sample_rate)
    
    def update_trigger_level_line(self):
        """Update the trigger level line on the plot"""
        self.trigger_line.setValue(self.trigger_level_input.value())
    
    def connect_device(self):
        if not self.connected:
            try:
                ip = self.ip_input.text()
                port = self.port_input.text()
                resource_string = f"TCPIP::{ip}::{port}::SOCKET"
                self.device = self.rm.open_resource(resource_string)
                self.device.read_termination = '\r\n'
                self.device.write_termination = '\r\n'
                self.device.timeout = 5000  # 5 seconds timeout
                
                # Test connection
                idn = self.device.query("*IDN?")
                self.status_bar.showMessage(f"Connected to: {idn}")
                self.connected = True
                self.connect_button.setText("Disconnect")
                
                # Enable control buttons
                self.acquire_button.setEnabled(True)
                self.continuous_button.setEnabled(True)
                self.auto_scale_button.setEnabled(True)
                self.trigger_test_button.setEnabled(True)
                
                # Initialize Red Pitaya acquisition settings
                self.setup_acquisition()
                
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")
                self.status_bar.showMessage("Connection failed")
                self.connected = False
        else:
            # Disconnect
            try:
                if self.continuous_mode:
                    self.toggle_continuous()  # Stop continuous mode
                
                self.device.close()
                self.device = None
                self.connected = False
                self.connect_button.setText("Connect")
                self.acquire_button.setEnabled(False)
                self.continuous_button.setEnabled(False)
                self.auto_scale_button.setEnabled(False)
                self.trigger_test_button.setEnabled(False)
                self.trigger_indicator.set_status("WAITING")
                self.status_bar.showMessage("Disconnected")
            except Exception as e:
                QMessageBox.warning(self, "Disconnection Error", f"Error during disconnection: {str(e)}")
    
    def setup_acquisition(self):
        try:
            # Reset acquisition
            self.device.write("ACQ:RST")
            time.sleep(0.1)  # Add small delay to ensure command is processed
            
            # Make sure to stop any previous acquisition
            self.device.write("ACQ:STOP")
            time.sleep(0.1)
            
            # Set decimation
            decimation = self.decimation_select.currentText()
            self.device.write(f"ACQ:DEC {decimation}")
            
            # Set buffer size (custom acquisition points)
            buffer_size = self.buffer_size_input.value()
            self.device.write(f"ACQ:BUF:SIZE {buffer_size}")
            
            # Set pre-trigger samples
            pretrigger = self.pretrigger_input.value()
            self.device.write(f"ACQ:TRIG:DLY -{pretrigger}")
            
            # Configure trigger source
            trigger_source = self.trigger_source_select.currentText()
            if trigger_source != "DISABLED":
                self.device.write(f"ACQ:TRIG {trigger_source}")
                
                # Set trigger level (convert from volts to normalized)
                trigger_level_v = self.trigger_level_input.value()
                
                # Different scaling for different trigger sources
                if trigger_source.startswith("EXT"):
                    # External trigger range is typically 0V to 3.3V
                    normalized_level = trigger_level_v / 3.3
                    # Clamp between 0 and 1
                    normalized_level = max(0.0, min(1.0, normalized_level))
                else:
                    # Channel triggers use full ADC range (-1 to 1)
                    normalized_level = trigger_level_v / 20.0  # Convert from ±20V to ±1
                    # Clamp between -1 and 1
                    normalized_level = max(-1.0, min(1.0, normalized_level))
                
                self.device.write(f"ACQ:TRIG:LEV {normalized_level}")
            else:
                # Disable trigger for immediate acquisition
                self.device.write("ACQ:TRIG:DIS")
            
            self.status_bar.showMessage("Acquisition setup completed")
            self.trigger_indicator.set_status("WAITING")
        except Exception as e:
            QMessageBox.warning(self, "Setup Error", f"Error setting up acquisition: {str(e)}")
    
    def run_trigger_test(self):
        """Run comprehensive trigger test and display results"""
        if not self.connected:
            return
        
        trigger_source = self.trigger_source_select.currentText()
        if trigger_source == "DISABLED":
            QMessageBox.information(self, "Trigger Test", "Trigger is disabled. Please select a trigger source.")
            return
        
        try:
            self.status_bar.showMessage("Running trigger test...")
            self.trigger_indicator.set_status("WAITING")
            
            # Setup acquisition with current settings
            self.setup_acquisition()
            
            # Start acquisition
            self.device.write("ACQ:START")
            
            # Check initial trigger state
            initial_state = self.device.query("ACQ:TRIG:STAT?").strip()
            self.status_bar.showMessage(f"Initial trigger state: {initial_state}")
            
            # Wait up to 3 seconds for trigger
            trigger_state = ""
            for i in range(30):
                trigger_state = self.device.query("ACQ:TRIG:STAT?").strip()
                if trigger_state == "TD":
                    self.trigger_indicator.set_status("TRIGGERED")
                    self.status_bar.showMessage("Trigger test: PASSED - Trigger detected!")
                    time.sleep(0.1)  # Let the acquisition complete
                    self.single_acquisition()  # Get the data
                    return
                time.sleep(0.1)
            
            # No trigger detected within timeout
            self.trigger_indicator.set_status("TIMEOUT")
            self.status_bar.showMessage("Trigger test: FAILED - No trigger detected within timeout!")
            
            # Use message box for detailed info
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Trigger Test Results")
            msg.setText("Trigger Test Failed")
            
            trigger_level = self.trigger_level_input.value()
            
            details = (
                f"Trigger source: {trigger_source}\n"
                f"Trigger level: {trigger_level}V\n\n"
                "Suggestions:\n"
                "1. Check physical connections to the trigger input\n"
                "2. Verify your signal source is active\n"
                "3. Try different trigger level values\n"
                "4. Try a different trigger source (e.g., channel trigger instead of external)\n"
                "5. Verify Red Pitaya firmware is up to date\n"
                "6. Try 'DISABLED' trigger option to ignore triggering"
            )
            
            msg.setDetailedText(details)
            msg.exec_()
            
            # Stop acquisition
            self.device.write("ACQ:STOP")
            
        except Exception as e:
            QMessageBox.warning(self, "Trigger Test Error", f"Error during trigger test: {str(e)}")
            self.trigger_indicator.set_status("WAITING")

    def single_acquisition(self):
        if not self.connected:
            return
        
        try:
            # Update acquisition settings
            self.setup_acquisition()
            
            # Start acquisition
            self.device.write("ACQ:START")
            
            trigger_source = self.trigger_source_select.currentText()
            if trigger_source != "DISABLED":
                # Wait for trigger with better status reporting
                self.status_bar.showMessage("Waiting for trigger...")
                self.trigger_indicator.set_status("WAITING")
                
                # Clear any buffer before checking trigger
                self.device.clear()
                
                # Check if trigger has occurred
                trigger_state = ""
                timeout_counter = 0
                while trigger_state != "TD":
                    trigger_state = self.device.query("ACQ:TRIG:STAT?").strip()
                    self.status_bar.showMessage(f"Waiting for trigger... State: {trigger_state}")
                    time.sleep(0.1)
                    timeout_counter += 1
                    if timeout_counter > 50:  # 5 second timeout
                        self.status_bar.showMessage("Trigger timeout - no trigger detected")
                        self.trigger_indicator.set_status("TIMEOUT")
                        self.device.write("ACQ:STOP")
                        return
                
                # Trigger occurred
                self.trigger_indicator.set_status("TRIGGERED")
                self.status_bar.showMessage("Trigger detected! Retrieving data...")
            else:
                # In disabled trigger mode, just wait a bit for data
                time.sleep(0.5)
                self.trigger_indicator.set_status("TRIGGERED")  # Consider it "triggered" for UI consistency
                self.status_bar.showMessage("Acquiring data without trigger...")
            
            # Get data from both channels
            self.get_channel_data(1)  # Channel 1
            self.get_channel_data(2)  # Channel 2
            
            # Update plot
            self.plot_curve_ch1.setData(self.time_data, self.data_ch1)
            self.plot_curve_ch2.setData(self.time_data, self.data_ch2)
            
            # Update measurements
            self.update_measurements()
            
            self.status_bar.showMessage(f"Acquisition complete: {len(self.data_ch1)} points per channel")
            
        except Exception as e:
            QMessageBox.warning(self, "Acquisition Error", f"Error during acquisition: {str(e)}")
            self.status_bar.showMessage("Acquisition failed")
    
    def get_channel_data(self, channel_num):
        """Get data for a specific channel"""
        try:
            # Try with better error handling
            try:
                data_str = self.device.query(f"ACQ:SOUR{channel_num}:DATA?")
            except Exception as query_error:
                print(f"Error querying CH{channel_num} data: {str(query_error)}")
                # Try to clear the interface and retry
                self.device.clear()
                time.sleep(0.5)
                data_str = self.device.query(f"ACQ:SOUR{channel_num}:DATA?")
            
            # Process data with more robust parsing
            try:
                # Replace error markers and clean up the data string
                clean_data_str = data_str.replace("ERR!", "").replace("{", "").replace("}", "")
                
                # Split by commas and handle potential empty strings or non-numeric values
                values = clean_data_str.split(',')
                data_list = []
                for val in values:
                    val = val.strip()
                    if val:  # Check if value is not empty
                        try:
                            data_list.append(float(val))
                        except ValueError:
                            pass  # Skip invalid values
                
                if not data_list:
                    raise ValueError(f"No valid data points received for CH{channel_num}")
                
                # Assign data to appropriate channel
                if channel_num == 1:
                    self.data_ch1 = np.array(data_list)
                else:
                    self.data_ch2 = np.array(data_list)
                
                # Calculate time base based on decimation and buffer size
                decimation = int(self.decimation_select.currentText())
                sample_time = 8e-9  # 8ns base sample time for Red Pitaya 125-14/10
                self.time_data = np.linspace(0, len(data_list) * sample_time * decimation, len(data_list))
                
            except Exception as e:
                # Print raw data for debugging
                print(f"Raw CH{channel_num} data received: {data_str[:100]}..." if len(data_str) > 100 else data_str)
                raise ValueError(f"CH{channel_num} data parsing error: {str(e)}")
                
        except Exception as e:
            print(f"Error getting CH{channel_num} data: {str(e)}")
            if channel_num == 1:
                self.data_ch1 = np.zeros(1024)
            else:
                self.data_ch2 = np.zeros(1024)
    
    def update_measurements(self):
        # Update Channel 1 measurements
        if self.show_ch1_checkbox.isChecked() and len(self.data_ch1) > 0:
            # Calculate Vpp
            if self.show_vpp_checkbox.isChecked():
                vpp = np.max(self.data_ch1) - np.min(self.data_ch1)
                self.ch1_vpp_display.setText(f"Vpp: {vpp:.3f} V")
            
            # Calculate Vrms
            if self.show_vrms_checkbox.isChecked():
                vrms = np.sqrt(np.mean(np.square(self.data_ch1)))
                self.ch1_vrms_display.setText(f"Vrms: {vrms:.3f} V")
            
            # Calculate frequency (using FFT)
            if self.show_freq_checkbox.isChecked():
                freq = self.calculate_frequency(self.data_ch1)
                if freq is not None:
                    self.ch1_freq_display.setText(freq)
                else:
                    self.ch1_freq_display.setText("Frequency: N/A")
        
        # Update Channel 2 measurements
        if self.show_ch2_checkbox.isChecked() and len(self.data_ch2) > 0:
            # Calculate Vpp
            if self.show_vpp_checkbox.isChecked():
                vpp = np.max(self.data_ch2) - np.min(self.data_ch2)
                self.ch2_vpp_display.setText(f"Vpp: {vpp:.3f} V")
            
            # Calculate Vrms
            if self.show_vrms_checkbox.isChecked():
                vrms = np.sqrt(np.mean(np.square(self.data_ch2)))
                self.ch2_vrms_display.setText(f"Vrms: {vrms:.3f} V")
            
            # Calculate frequency (using FFT)
            if self.show_freq_checkbox.isChecked():
                freq = self.calculate_frequency(self.data_ch2)
                if freq is not None:
                    self.ch2_freq_display.setText(freq)
                else:
                    self.ch2_freq_display.setText("Frequency: N/A")
    
    def calculate_frequency(self, data):
        try:
            # Calculate sample rate
            decimation = int(self.decimation_select.currentText())
            sample_rate = 125e6 / decimation  # 125 MHz / decimation
            
            # Remove DC component
            data_ac = data - np.mean(data)
            
            # Apply window to reduce spectral leakage
            windowed_data = data_ac * np.hanning(len(data_ac))
            
            # Compute FFT
            fft_data = np.abs(np.fft.rfft(windowed_data))
            
            # Get frequency bins
            freq_bins = np.fft.rfftfreq(len(windowed_data), 1/sample_rate)
            
            # Find peak frequency, ignoring DC component
            peak_idx = np.argmax(fft_data[1:]) + 1
            peak_freq = freq_bins[peak_idx]
            
            # Format frequency display
            if peak_freq > 1e6:
                return f"Frequency: {peak_freq/1e6:.3f} MHz"
            elif peak_freq > 1e3:
                return f"Frequency: {peak_freq/1e3:.3f} kHz"
            else:
                return f"Frequency: {peak_freq:.3f} Hz"
                
        except Exception as e:
            print(f"Frequency calculation error: {str(e)}")
            return None
    
    def toggle_continuous(self):
        if not self.continuous_mode:
            # Start continuous mode
            self.continuous_mode = True
            self.continuous_button.setText("Stop Continuous")
            self.acquire_button.setEnabled(False)
            self.timer.start(500)  # Update every 500ms
            self.status_bar.showMessage("Continuous acquisition started")
        else:
            # Stop continuous mode
            self.continuous_mode = False
            self.continuous_button.setText("Start Continuous")
            self.acquire_button.setEnabled(True)
            self.timer.stop()
            self.status_bar.showMessage("Continuous acquisition stopped")
    
    def auto_scale(self):
        """Auto-scale the y-axis based on the current data"""
        # Calculate min and max values from both channels if visible
        min_vals = []
        max_vals = []
        
        if self.show_ch1_checkbox.isChecked() and len(self.data_ch1) > 0:
            min_vals.append(np.min(self.data_ch1))
            max_vals.append(np.max(self.data_ch1))
            
        if self.show_ch2_checkbox.isChecked() and len(self.data_ch2) > 0:
            min_vals.append(np.min(self.data_ch2))
            max_vals.append(np.max(self.data_ch2))
        
        if min_vals and max_vals:
            min_val = min(min_vals)
            max_val = max(max_vals)
            padding = (max_val - min_val) * 0.1  # 10% padding
            self.plot_widget.setYRange(min_val - padding, max_val + padding)
    
    def update_plot(self):
        if self.continuous_mode:
            self.single_acquisition()
    
    def closeEvent(self, event):
        # Clean up when closing
        if self.continuous_mode:
            self.toggle_continuous()
        
        if self.connected:
            try:
                self.device.write("ACQ:STOP")
                self.device.close()
            except:
                pass
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedPitayaOscilloscope()
    window.show()
    sys.exit(app.exec_())