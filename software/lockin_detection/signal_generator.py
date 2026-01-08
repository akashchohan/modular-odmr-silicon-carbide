import numpy as np

def generate_signal_files():
    # Basic signal parameters you can modify
    duration = 1.0  # Total time in seconds
    sample_rate = 1000  # Number of samples per second (Hz)
    
    # Create time array: from 0 to duration with sample_rate points
    # For example, with duration=1s and sample_rate=1000Hz, 
    # we get 1000 evenly spaced points from 0 to 1 second
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    # Signal frequency and amplitude settings
    signal_frequency = 10  # This is your main signal frequency in Hz
                          # You can change this to any value below sample_rate/2
                          # Higher frequencies will need higher sample rates
    
    signal_amplitude = 0.5  # This sets how strong your signal is
                           # Increase this to make your signal stronger
    
    # Generate the clean sine wave signal
    # np.sin takes radians, so we convert our frequency to radians:
    # 2π × frequency × time
    clean_signal = signal_amplitude * np.sin(2 * np.pi * signal_frequency * t)
    
    # Create reference signal at the same frequency
    # Usually kept at amplitude 1.0 for simplicity
    reference_signal = np.sin(2 * np.pi * signal_frequency * t)
    
    # Add noise to create the noisy signal
    noise_amplitude = 0.3  # Controls how much noise to add
                          # Increase this to make signal more noisy
                          # Decrease to make signal clearer
    
    # Generate random noise using Gaussian (normal) distribution
    noise = noise_amplitude * np.random.normal(0, 1, len(t))
    
    # Combine clean signal with noise
    noisy_signal = clean_signal + noise
    
    # Save all signals to text files
    np.savetxt('signal.txt', noisy_signal)  # This is what we'll try to recover
    np.savetxt('reference_signal.txt', reference_signal)  # This helps us find our signal
    np.savetxt('clean_signal.txt', clean_signal)  # We'll use this to compare results
    
    return t, clean_signal, noisy_signal, reference_signal