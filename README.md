# Modular ODMR System Using Silicon Carbide (SiC)
### A Practical, Low-Cost Quantum Sensing Platform

This repository contains the complete design, hardware, software, documentation, and results from my 6-month industrial research project developing a **modular, low-cost ODMR (Optically Detected Magnetic Resonance) system** using Silicon Carbide (SiC) defects.

The system demonstrates room-temperature quantum sensing by exciting SiC with an 808 nm laser and detecting spin-dependent fluorescence under RF excitation. All RF generation, signal acquisition, lock-in detection, and optical control were built from scratch using Arduino, Red Pitaya, Python GUIs, and custom hardware.

---

## 🔍 Features

- Custom RF synthesizer (Si5351 + Arduino UNO)
- ADF4351 GHz clock generator with GUI
- Software-based lock-in amplifier (Python)
- Hardware lock-in via Red Pitaya
- 808 nm laser diode module with TEC cooling to –4 °C
- Photodiode fluorescence detection
- Dual-channel oscilloscope GUI using Red Pitaya ADC
- Temperature–humidity control chamber (Peltier + fan)
- Full optical alignment setup using a green laser
- Modular, replaceable RF, optical, and DAQ subsystems

---

## 📡 ODMR Results Obtained
- Clear ODMR dips near **70 MHz**  
- Higher-frequency transitions using ADF4351  
- Improved SNR with software lock-in detection  
- Stable fluorescence modulation with SiC defects  

Example theoretical layout:

![ODMR Setup Diagram](images/odmr_diagram.png)

---

## 📁 Repository Structure
docs/ → Theory, explanations, system architecture
hardware/ → Synthesizer, ADF4351, optics, laser, chamber
software/ → GUIs, lock-in, oscilloscopes, controllers
reports/ → Synopsis 1, Synopsis 2, Final Report
images/ → RF board, optics, alignment, Red Pitaya
results/ → ODMR dips, resonance sweeps, lock-in plots


---

## 🎓 Why It Matters

Silicon Carbide-based ODMR is a powerful tool for:

- Room-temperature quantum sensing  
- Magnetic field measurement  
- Precision timing  
- Education & research training platforms  

This project demonstrates that a **full ODMR system can be built affordably**, using accessible hardware and custom software.

---

## 👤 Author

**Akash**  
Quantum Sensing • Embedded Systems • Machine Learning  
MSc Data Science, University of Surrey  

