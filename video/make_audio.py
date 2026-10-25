#!/usr/bin/env python3
"""Synthesises the intro soundtrack (no samples, no licensing): heartbeat, monitor beeps,
impacts and a low drone, all timed to the cues in intro.html. Writes intro-audio.wav."""
import math
import wave

import numpy as np

SR, DUR = 48000, 12.0
t = np.arange(int(SR * DUR)) / SR
mix = np.zeros_like(t)


def at(start, sig):
    i = int(start * SR)
    n = min(len(sig), len(mix) - i)
    mix[i:i + n] += sig[:n]


def env(n, attack, decay):
    x = np.arange(n) / SR
    return np.minimum(1, x / attack) * np.exp(-x / decay)


def thump(freq=55, dur=0.35, gain=0.9, drop=0.5):
    n = int(dur * SR); x = np.arange(n) / SR
    f = freq * (1 + drop * np.exp(-x / 0.03))
    return gain * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, dur / 4)


def heartbeat(start, gain=0.9):
    at(start, thump(58, 0.3, gain))
    at(start + 0.16, thump(50, 0.3, gain * 0.7))


def beep(start, gain=0.22, dur=0.13):
    n = int(dur * SR); x = np.arange(n) / SR
    at(start, gain * np.sin(2 * np.pi * 1050 * x) * np.minimum(1, x / 0.004) * np.minimum(1, (dur - x) / 0.02))


def noise_swell(start, dur, gain=0.25, rising=True):
    n = int(dur * SR)
    w = np.random.default_rng(int(start * 100)).normal(0, 1, n)
    k = 60  # crude low-pass by moving average
    w = np.convolve(w, np.ones(k) / k, mode="same")
    shape = np.linspace(0, 1, n) ** 2 if rising else np.linspace(1, 0, n) ** 2
    at(start, gain * 4 * w * shape)


def boom(start, gain=1.0):
    at(start, thump(42, 1.4, gain, drop=1.5))


# spike of the drawn heartbeat line (see ecg path in intro.html): draw runs 0.25 -> 1.45 s linearly
pts = [(0, 0), (306, 0), (326, -32), (346, 0), (364, 0), (382, 46), (408, -206), (436, 114), (454, 0),
       (472, 0), (490, -36), (508, 0), (800, 0)]
seglen = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
spike = 0.25 + 1.2 * sum(seglen[:6]) / sum(seglen)

# low drone under everything, swelling with the scenes
drone = 0.05 * (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.5 * t) + 0.3 * np.sin(2 * np.pi * 110 * t))
drone *= np.clip(t / 1.5, 0, 1) * np.clip((12 - t) / 0.6, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * t / 6))
mix += drone

heartbeat(spike - 0.55, 0.6)        # a beat before the line peaks
beep(spike); heartbeat(spike, 0.9)  # the peak itself
boom(1.52, 1.0)                     # plates slam on: the barbell forms
beep(2.45, 0.12); beep(2.6, 0.12)   # name reveal ticks
noise_swell(3.7, 0.55, 0.22)        # whoosh into the photo
boom(4.25, 0.8)
for s in (6.1, 6.75, 7.4):          # kinetic words
    at(s, thump(70, 0.25, 0.9)); noise_swell(s - 0.12, 0.12, 0.12)
noise_swell(7.95, 0.5, 0.25)        # whoosh into the manifesto
for s in (8.5, 8.85, 9.2):
    at(s, thump(60, 0.3, 0.8))
boom(9.2, 0.9)
heartbeat(10.1, 0.8); beep(10.1, 0.18)
heartbeat(10.9, 0.55)

mix = np.tanh(mix * 1.1)            # soft limiter
mix *= 0.89 / np.max(np.abs(mix))   # about -1 dBFS peak
pcm = (mix * 32767).astype("<i2")
with wave.open("intro-audio.wav", "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
print(f"spike at {spike:.3f}s, wrote intro-audio.wav")
