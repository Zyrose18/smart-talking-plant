import board
import busio
import sdcardio
import storage
import os
import time
import audiobusio
import audiocore
import audiomixer
import analogio

# ---------------------------------------------------------
# CONFIGURATION (Tweak these values for your specific setup)
# ---------------------------------------------------------
DRY_VALUE = 52000     # Raw analog value when sensor is dry in air (0%)
WET_VALUE = 25000     # Raw analog value when sensor is submerged in water (100%)
WARN_PERCENT = 20     # Trigger threshold: plant complains below this percentage
VOLUME = 0.3          # Amplifier volume (0.0 to 1.0)
SOUND_FOLDER = "/sd/sounds" # Directory on the MicroSD card
# ---------------------------------------------------------

print("Starting Smart Plant Monitoring...")

# --- 1. Init SD Card (SPI) ---
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
sd = sdcardio.SDCard(spi, board.GP13)
vfs = storage.VfsFat(sd)
storage.mount(vfs, "/sd")

# --- 2. Init Audio Amplifier (I2S) ---
i2s = audiobusio.I2SOut(board.GP4, board.GP3, board.GP2)

# --- 3. Init Moisture Sensor (Analog In) ---
sensor = analogio.AnalogIn(board.A0)

# --- 4. Scan and sort audio files ---
all_files = os.listdir(SOUND_FOLDER)
playlist = []

for file in all_files:
    if file.lower().endswith(".wav"):
        playlist.append(file)

# Sort alphabetically to keep the coworker loop consistent
playlist.sort()

print("Found audio files (sorted):", playlist)

if len(playlist) == 0:
    print("WARNING: No .wav files found in the specified folder!")

# Tracker for the playback loop
speaker_index = 0

print("System ready. Starting moisture loop...")

# --- 5. Main Loop ---
while True:
    raw_val = sensor.value
    
    # Map raw value to percentage
    percent = (DRY_VALUE - raw_val) / (DRY_VALUE - WET_VALUE) * 100
    
    # Clamp values between 0% and 100%
    if percent > 100: percent = 100
    if percent < 0: percent = 0
        
    percent = int(percent)
    print("Moisture:", percent, "% (Raw:", raw_val, ")")
    
    # Check if soil is too dry
    if percent < WARN_PERCENT and len(playlist) > 0:
        print("Alert! Moisture critical. Playing audio...")
        
        # Select current audio track
        selection = playlist[speaker_index]
        file_path = SOUND_FOLDER + "/" + selection 
        print("Playing:", selection)
        
        # Load audio and configure mixer
        audio_file = open(file_path, "rb")
        wav = audiocore.WaveFile(audio_file)
        
        mixer = audiomixer.Mixer(
            voice_count=1, 
            sample_rate=wav.sample_rate, 
            channel_count=1, 
            bits_per_sample=16, 
            samples_signed=True
        )
        
        i2s.play(mixer)
        mixer.voice[0].level = VOLUME  
        mixer.voice[0].play(wav)
        
        # Wait until the track finishes
        while mixer.voice[0].playing:
            time.sleep(0.1)
            
        # Stop hardware cleanly to prevent I2S hissing noise
        i2s.stop()
        mixer.deinit()
        audio_file.close()
        
        # Move to the next coworker in the playlist
        speaker_index += 1
        
        # Reset loop if we reach the end
        if speaker_index >= len(playlist):
            speaker_index = 0
        
        # Cooldown after alert to prevent audio spam
        time.sleep(5) 
        
    else:
        # Moisture is fine, just wait a bit before checking again
        time.sleep(5)