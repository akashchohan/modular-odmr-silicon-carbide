import os
from signal_generator import generate_signal_files
from lockin_processor import LockInProcessor
import numpy as np
import matplotlib.pyplot as plt

def main():
    """
    This is our main program that coordinates all the steps:
    1. Generate test signals
    2. Process them with lock-in amplifier
    3. Display and analyze results
    """
    print("=== Lock-in Amplifier Demonstration ===")
    
    # Generate our test signals
    print("\nStep 1: Generating signal files...")
    t, clean_signal, noisy_signal, reference_signal = generate_signal_files()
    
    # Create and use our lock-in amplifier
    print("\nStep 2: Processing signals...")
    processor = LockInProcessor(time_constant=0.1)
    recovered_signal = processor.process_signals(noisy_signal, reference_signal)
    
    # Show results
    print("\nStep 3: Creating visualization...")
    create_visualization(t, noisy_signal, recovered_signal, clean_signal)
    
    # Calculate how well we did
    print("\nStep 4: Calculating signal quality metrics...")
    calculate_metrics(clean_signal, recovered_signal)

def calculate_metrics(clean_signal, recovered_signal):
    """
    Measures how well we recovered the signal:
    - RMSE: Lower is better (perfect would be 0)
    - SNR: Higher is better (perfect would be infinity)
    """
    # Root Mean Square Error shows average difference from original
    rmse = np.sqrt(np.mean((clean_signal - recovered_signal) ** 2))
    
    # Signal-to-Noise Ratio shows how much signal vs noise we have
    signal_power = np.mean(clean_signal ** 2)
    noise_power = np.mean((clean_signal - recovered_signal) ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    
    print(f"Root Mean Square Error: {rmse:.4f}")
    print(f"Signal-to-Noise Ratio: {snr:.2f} dB")