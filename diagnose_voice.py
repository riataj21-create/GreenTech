"""
GreenTech voice diagnostic — run with: python diagnose_voice.py
Records 4 seconds. SPEAK CLEARLY during recording.
"""
import sys, time
sys.path.insert(0, '.')
import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly
from math import gcd
from faster_whisper import WhisperModel

# ── Device info ───────────────────────────────────────────────────────────────
print("=== AUDIO DEVICES ===")
devices = sd.query_devices()
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f"  [{i}] {d['name']} | sr={d['default_samplerate']} | ch={d['max_input_channels']}")
print(f"  Default input: {sd.default.device[0]}")
print()

default_idx = sd.default.device[0]
dev = devices[default_idx]
native_sr = int(dev['default_samplerate'])
native_ch = min(int(dev['max_input_channels']), 2)
print(f"Using: {dev['name']} | native_sr={native_sr} | channels={native_ch}")
print()

# ── Record at native sample rate ──────────────────────────────────────────────
print(f"Recording 4 seconds at native {native_sr} Hz, {native_ch} ch...")
print(">>> SPEAK NOW: 'Rice leaves are turning yellow' <<<")
chunks = []

def callback(indata, frames, t, status):
    if status:
        print(f"  [callback status] {status}")
    chunks.append(indata.copy())

stream = sd.InputStream(samplerate=native_sr, channels=native_ch,
                         dtype='float32', callback=callback)
stream.start()
time.sleep(4)
stream.stop()
stream.close()

audio_raw = np.concatenate(chunks)
if audio_raw.ndim > 1:
    audio_mono = audio_raw.mean(axis=1).astype(np.float32)
else:
    audio_mono = audio_raw.flatten().astype(np.float32)

rms_raw = float(np.sqrt(np.mean(audio_mono**2)))
print(f"\nRaw audio: {len(audio_mono)} samples, {len(audio_mono)/native_sr:.2f}s")
print(f"Raw RMS: {rms_raw:.6f} | Max: {float(np.max(np.abs(audio_mono))):.6f}")

# ── Resample to 16000 if needed ───────────────────────────────────────────────
TARGET_SR = 16000
if native_sr != TARGET_SR:
    g = gcd(TARGET_SR, native_sr)
    audio_16k = resample_poly(audio_mono, TARGET_SR // g, native_sr // g).astype(np.float32)
    print(f"Resampled {native_sr} → {TARGET_SR}: {len(audio_16k)} samples")
else:
    audio_16k = audio_mono
    print("No resampling needed.")

rms_16k = float(np.sqrt(np.mean(audio_16k**2)))
print(f"Post-resample RMS: {rms_16k:.6f}")

# ── Normalize ─────────────────────────────────────────────────────────────────
TARGET_RMS = 0.08
if rms_16k > 1e-6:
    gain        = min(TARGET_RMS / rms_16k, 20.0)   # cap at 20x
    audio_norm  = np.clip(audio_16k * gain, -1.0, 1.0)
    print(f"Gain applied: {gain:.2f}x → RMS after: {float(np.sqrt(np.mean(audio_norm**2))):.6f}")
else:
    audio_norm  = audio_16k
    print("Audio too quiet to normalise.")

# ── Transcribe with multiple settings ─────────────────────────────────────────
print("\n=== TRANSCRIPTION TESTS ===")
model = WhisperModel('base', device='cpu', compute_type='int8')

for label, audio_in in [("raw_16k", audio_16k), ("normalised", audio_norm)]:
    for vad in [False, True]:
        segs, info = model.transcribe(
            audio_in, language='en', beam_size=5,
            vad_filter=vad,
            condition_on_previous_text=False,
        )
        text = ' '.join(s.text.strip() for s in segs).strip()
        print(f"  [{label}] vad={vad}: {repr(text)}")
        print(f"    detected_lang={info.language} prob={info.language_probability:.3f}")
    print()
