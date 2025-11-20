"""
Check energy levels in your audio files

This helps us find the right threshold

"""



import numpy as np

import soundfile as sf

import sys

from pathlib import Path





def analyze_audio(audio_file):

    """Analyze energy levels in audio file"""

    

    if not Path(audio_file).exists():

        print(f"❌ File not found: {audio_file}")

        return

    

    print(f"\n{'='*70}")

    print(f"Analyzing: {audio_file}")

    print(f"{'='*70}")

    

    # Load audio

    audio_data, sample_rate = sf.read(audio_file)

    

    # Convert to mono if stereo

    if len(audio_data.shape) > 1:

        audio_data = audio_data[:, 0]

    

    duration = len(audio_data) / sample_rate

    

    print(f"Sample rate: {sample_rate} Hz")

    print(f"Duration: {duration:.2f} seconds")

    print(f"Samples: {len(audio_data)}")

    print(f"\n{'='*70}")

    

    # Analyze in chunks

    chunk_duration = 0.1  # 100ms

    chunk_size = int(sample_rate * chunk_duration)

    

    energies = []

    

    print("Energy analysis (100ms chunks):\n")

    

    for i in range(0, len(audio_data), chunk_size):

        chunk = audio_data[i:i + chunk_size]

        energy = np.sqrt(np.mean(chunk**2))

        energies.append(energy)

        

        # Print sample energies

        if i < chunk_size * 10 or i > len(audio_data) - chunk_size * 10:

            time = i / sample_rate

            print(f"  {time:6.2f}s: energy = {energy:.6f}")

    

    print("\n" + "="*70)

    print("STATISTICS:")

    print("="*70)

    

    energies = np.array(energies)

    

    print(f"Min energy:     {energies.min():.6f}")

    print(f"Max energy:     {energies.max():.6f}")

    print(f"Mean energy:    {energies.mean():.6f}")

    print(f"Median energy:  {np.median(energies):.6f}")

    print(f"Std dev:        {energies.std():.6f}")

    

    # Find 90th percentile (likely speech)

    p90 = np.percentile(energies, 90)

    p50 = np.percentile(energies, 50)

    p10 = np.percentile(energies, 10)

    

    print(f"\n90th percentile: {p90:.6f} (likely speech)")

    print(f"50th percentile: {p50:.6f}")

    print(f"10th percentile: {p10:.6f} (likely silence)")

    

    print("\n" + "="*70)

    print("RECOMMENDED THRESHOLD:")

    print("="*70)

    

    # Recommend threshold between 10th and 50th percentile

    recommended = (p10 + p50) / 2

    print(f"\nRecommended: {recommended:.6f}")

    print(f"(Halfway between silence and median)\n")

    

    # Show how many chunks would be detected at different thresholds

    print("Detection rate at different thresholds:")

    for threshold in [0.001, 0.005, 0.01, 0.015, 0.02, 0.03]:

        detections = (energies > threshold).sum()

        percentage = (detections / len(energies)) * 100

        print(f"  Threshold {threshold:.3f}: {detections:4d}/{len(energies)} chunks ({percentage:5.1f}%)")

    

    print("\n" + "="*70)

    print("RECOMMENDATION FOR config.py:")

    print("="*70)

    print(f"\nENERGY_THRESHOLD = {recommended:.6f}\n")

    print("="*70 + "\n")





def main():

    if len(sys.argv) < 2:

        print("Usage: python check_audio_energy.py <audio_file1> [audio_file2] ...")

        print("\nExample:")

        print("  python check_audio_energy.py walkie1.mp3 walkie2.mp3")

        sys.exit(1)

    

    for audio_file in sys.argv[1:]:

        analyze_audio(audio_file)





if __name__ == "__main__":

    main()

