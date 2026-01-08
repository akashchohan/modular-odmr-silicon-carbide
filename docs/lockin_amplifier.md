# Software Lock-In Amplifier

A custom software lock-in amplifier was implemented in Python to extract weak ODMR signals buried in noise.

## Principle
- Input signal (photodiode output) is multiplied with a reference signal
- The mixed signal is passed through a low-pass filter
- The resulting output represents the recovered signal amplitude

## Implementation
- Phase-sensitive detection
- First-order Butterworth low-pass filter
- Adjustable time constant
- Signal recovery scaling

## Validation
Test signals were generated synthetically:
- Clean sinusoidal signal
- Gaussian noise added
- Reference signal at same frequency

The recovered signal was compared with the original clean signal using:
- RMSE
- Signal-to-Noise Ratio (SNR)

Results demonstrate effective noise rejection and signal recovery.
