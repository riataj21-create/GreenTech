"""
GreenTech voice model accuracy test.
Tests base vs small model on the same recorded audio.
Run: python diagnose_voice2.py
Speak clearly when prompted.
"""
import sys, time
sys.path.insert(0, '.')
import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly
from math import gcd
from faster_whisper import WhisperModel

NATIVE_SR = 44100
TARGET_SR = 16000

print("Recording 5 seconds...")
print(">>> SPEAK: 'Rice leaves are turning yellow. The crop looks weak.' <<<")

chunks = []
def cb(indata, frames, t, status):
    chunks.append(indata.copy())

stream = sd.InputStream(samplerate=NATIVE_SR, channels=2, dtype='float32', callback=cb)
stream.start()
time.sleep(5)
stream.stop()
stream.close()

audio = np.concatenate(chunks).mean(axis=1).astype(np.float32)
g = gcd(TARGET_SR, NATIVE_SR)
audio_16k = resample_poly(audio, TARGET_SR//g, NATIVE_SR//g).astype(np.float32)

rms = float(np.sqrt(np.mean(audio_16k**2)))
if rms > 1e-6:
    gain = min(0.08 / rms, 20.0)
    audio_16k = np.clip(audio_16k * gain, -1.0, 1.0)
print(f"Audio: {len(audio_16k)/TARGET_SR:.1f}s, RMS after norm: {float(np.sqrt(np.mean(audio_16k**2))):.4f}")
print()

for model_name in ["base", "small"]:
    print(f"--- Model: {model_name} ---")
    try:
        m = WhisperModel(model_name, device="cpu", compute_type="int8")
        for beam in [1, 5]:
            segs, info = m.transcribe(
                audio_16k, language="en", beam_size=beam,
                vad_filter=False,
                condition_on_previous_text=False,
                temperature=0.0,
            )
            text = " ".join(s.text.strip() for s in segs).strip()
            print(f"  beam={beam}: {repr(text)}")
        print()
    except Exception as e:
        print(f"  ERROR: {e}")
