# Red Pitaya Integration

The Red Pitaya STEMlab 125-10 is used as the primary data acquisition and signal-processing platform.

## Operating System
- Red Pitaya OS version: **v1.1.8**
- Newer OS versions were tested but showed increased latency and GUI lag
- v1.1.8 provided the most stable real-time performance

## Built-in Tools
- Used the built-in Red Pitaya oscilloscope for initial signal validation
- Verified RF modulation and photodiode output

## Custom Oscilloscope
A Python-based dual-channel oscilloscope was developed:
- Communicates with Red Pitaya server
- Reads both ADC channels
- Displays time-domain signals in real time

This allowed customized signal inspection beyond the built-in interface.
