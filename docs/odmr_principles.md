# ODMR Principles

Optically Detected Magnetic Resonance (ODMR) enables detection of electron or nuclear spin transitions by monitoring changes in optical fluorescence intensity.

### How ODMR Works

1. A laser excites defect centers, populating spin states.
2. An RF field is applied to drive transitions between spin sublevels.
3. When the RF frequency matches a resonance transition, fluorescence decreases, producing an "ODMR dip".
4. The dip is detected using:
   - Photodiode
   - Lock-in amplifier
   - Digitizer (Red Pitaya)

### Why Silicon Carbide (SiC)

SiC defects provide:
- Room-temperature operation  
- Long coherence times  
- Strong fluorescence  
- Compatibility with cheap laser diodes  
- Robustness under high optical power  

### ODMR Spectrum

A typical ODMR spectrum shows:
- A baseline fluorescence level  
- Resonance dips at frequency transitions  
- Enhanced signal using lock-in detection  

The system developed in this project successfully reproduces these features.
