import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # This line helps ensure the plot works on different systems
import matplotlib.pyplot as plt
from scipy import signal
import os

class NoiseVisualizer:
    def __init__(self, sample_rate=1000, duration=1.0):
        """Initialize the noise visualizer with given parameters"""
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_points = int(sample_rate * duration)
        self.time = np.linspace(0, duration, self.num_points)
        self.frequencies = np.fft.fftfreq(self.num_points, 1/sample_rate)
        
    def generate_noise(self, noise_type='white', amplitude=1.0):
        """Generate specified type of noise"""
        print(f"Generating {noise_type} noise...")
        
        if noise_type == 'white':
            noise = amplitude * np.random.normal(0, 1, self.num_points)
        
        elif noise_type == 'pink':
            white = np.random.normal(0, 1, self.num_points)
            f = np.abs(self.frequencies)
            f[0] = 1
            pink = white / np.sqrt(f)
            noise = amplitude * np.real(np.fft.ifft(pink))
            noise = noise / np.std(noise)
            
        elif noise_type == 'brown':
            white = np.random.normal(0, 1, self.num_points)
            f = np.abs(self.frequencies)
            f[0] = 1
            brown = white / f
            noise = amplitude * np.real(np.fft.ifft(brown))
            noise = noise / np.std(noise)
            
        return noise
    
    def plot_noise_characteristics(self, save_path='./noise_types_comparison.png'):
        """Create and save visualization of different noise types"""
        try:
            print("Starting visualization...")
            noise_types = ['white', 'pink', 'brown']
            fig = plt.figure(figsize=(15, 10))
            
            for idx, noise_type in enumerate(noise_types):
                print(f"Processing {noise_type} noise...")
                noise = self.generate_noise(noise_type)
                frequencies = self.frequencies[:self.num_points//2]
                power_spectrum = np.abs(np.fft.fft(noise))[:self.num_points//2]
                
                # Time domain plot
                plt.subplot(3, 2, 2*idx + 1)
                plt.plot(self.time[:500], noise[:500], 
                        label=f'{noise_type.capitalize()} Noise',
                        color=['blue', 'green', 'red'][idx])
                plt.title(f'{noise_type.capitalize()} Noise - Time Domain')
                plt.xlabel('Time (s)')
                plt.ylabel('Amplitude')
                plt.grid(True)
                
                # Frequency domain plot
                plt.subplot(3, 2, 2*idx + 2)
                plt.loglog(frequencies[1:], power_spectrum[1:],
                          label=f'{noise_type.capitalize()} Noise',
                          color=['blue', 'green', 'red'][idx])
                plt.title(f'{noise_type.capitalize()} Noise - Frequency Domain')
                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Power')
                plt.grid(True)
                
                if noise_type != 'white':
                    f_ref = frequencies[1:]
                    if noise_type == 'pink':
                        plt.loglog(f_ref, 1/np.sqrt(f_ref), '--', 
                                 label='1/f slope', alpha=0.5)
                    else:  # brown noise
                        plt.loglog(f_ref, 1/f_ref, '--', 
                                 label='1/f² slope', alpha=0.5)
                plt.legend()
            
            plt.tight_layout()
            
            # Save the figure
            print(f"Saving figure to {save_path}...")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved successfully to {save_path}")
            
            # Show the plot
            plt.show()
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
def main():
    """Main function to run the visualization"""
    # Create output directory if it doesn't exist
    output_dir = "noise_visualization_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create full path for saving the figure
    save_path = os.path.join(output_dir, "noise_types_comparison.png")
    
    # Create and run visualizer
    print("Creating noise visualizer...")
    visualizer = NoiseVisualizer()
    visualizer.plot_noise_characteristics(save_path)

if __name__ == "__main__":
    main()