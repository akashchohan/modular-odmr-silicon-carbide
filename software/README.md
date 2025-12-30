# Software & Control Tools

This directory contains all Python GUIs, acquisition scripts, and signal processing tools developed for the ODMR system.

Subfolders:
- `rf_gui_python/` — GUI for controlling Si5351 and ADF4351 synthesizers
- `lockin_detection/` — Software lock-in amplifier implementation
- `dual_channel_oscilloscope/` — Python oscilloscope using Red Pitaya ADCs
- `temperature_control_gui/` — GUI for Peltier and environmental chamber

All scripts were designed to be modular and work with USB/serial-controlled RF sources.
