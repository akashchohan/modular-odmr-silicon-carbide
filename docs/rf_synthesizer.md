# RF Synthesizer Subsystem

The RF excitation system consists of two independent sources to cover a wide frequency range.

## Si5351 DDS Synthesizer
- Controlled via Arduino UNO
- Frequency range: ~35 MHz – 225 MHz
- Used for low-frequency ODMR experiments
- Python GUI developed for:
  - Frequency sweep
  - Step size control
  - Real-time updates

Custom Arduino firmware and Python control scripts were written for this module.

## ADF4351 PLL Synthesizer
- Frequency range: 35 MHz – 4.4 GHz
- Controlled via Arduino + Python interface
- Used for higher-frequency spin transitions

Both RF sources can be independently selected depending on the experimental requirements.
