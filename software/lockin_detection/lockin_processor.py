import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class LockInProcessor:
    def __init__(self, time_constant=0.1):
        """
        Initialize the lock-in processor
        
        Parameters:
        time_constant: Integration time in seconds
        """
        self.time_constant = time_constant
        self.sample_rate = 1000  # Hz
    
    def apply_lowpass_filter(self, data):
        """Apply low-pass filter to remove high-frequency components"""
        cutoff_freq = 1.0 / (2.0 * np.pi * self.time_constant)
        b, a = signal.butter(1, cutoff_freq / (self.sample_rate/2))
        return signal.filtfilt(b, a, data)
    
    def process_signals(self, input_signal, reference_signal):
        """
        Process the input signal using the reference to recover the clean signal
        """
        # Perform phase-sensitive detection
        mixed_signal = input_signal * reference_signal
        
        # Apply low-pass filter
        recovered_signal = self.apply_lowpass_filter(mixed_signal)
        
        # Scale the recovered signal to match original amplitude
        recovered_signal *= 2
        
        return recovered_signal

def main():
    # Load signals from files
    input_signal = np.loadtxt('signal.txt')
    reference_signal = np.loadtxt('reference_signal.txt')
    clean_signal = np.loadtxt('clean_signal.txt')  # For comparison
    
    # Create processor instance
    processor = LockInProcessor(time_constant=0.1)
    
    # Process the signals
    recovered_signal = processor.process_signals(input_signal, reference_signal)
    
    # Create time array for plotting
    t = np.linspace(0, 1, len(input_signal))
    
    # Plot the results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(t, input_signal)
    plt.title('Noisy Input Signal')
    plt.ylabel('Amplitude')
    
    plt.subplot(3, 1, 2)
    plt.plot(t, recovered_signal)
    plt.title('Recovered Signal (Lock-in Output)')
    plt.ylabel('Amplitude')
    
    plt.subplot(3, 1, 3)
    plt.plot(t, clean_signal)
    plt.title('Original Clean Signal (For Comparison)')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    plt.tight_layout()
    plt.savefig('signal__ccomparison.png')
    plt.show()
    
    # Save the recovered signal
    np.savetxt('recovered_signal.txt', recovered_signal)
    print("Processing complete! Recovered signal saved to 'recovered_signal.txt'")

if __name__ == "__main__":
    main()