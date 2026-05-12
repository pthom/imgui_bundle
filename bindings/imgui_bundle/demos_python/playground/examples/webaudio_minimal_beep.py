"""
WebAudio: minimal beep — Pyodide sanity check.

**Pyodide only.** Calls the browser's WebAudio API via Python's `js` interop.
Click **Beep** to hear a short sine tone whose frequency and duration you
can slide.

Why this exists: confirms that audio works in the Pyodide playground
without needing an SDL2-audio-enabled build or a Python audio binding.
Same pattern as the `webgl_minimal_mandelbrot.py` demo, just talking to
`AudioContext` instead of `WebGL2RenderingContext`.

## Gotcha

Browsers require a *user gesture* before an `AudioContext` is allowed to
produce sound. We create the context lazily inside the Beep button
handler — the button click is the gesture, so playback starts on the
very first press.
"""
from imgui_bundle import imgui, immapp


_audio_ctx = None       # js AudioContext (Pyodide); None on desktop or until first click
_frequency = 440.0      # Hz
_duration_ms = 200      # ms
_status = ""            # last-action message shown under the controls


def _ensure_audio_context():
    """Lazy-init the browser's AudioContext on first call. No-op on desktop."""
    global _audio_ctx, _status
    if _audio_ctx is not None:
        return _audio_ctx
    try:
        from js import AudioContext  # type: ignore[import-not-found,import-untyped]
        _audio_ctx = AudioContext.new()
        _status = "AudioContext ready"
    except Exception as e:
        _status = f"AudioContext unavailable: {e}"
    return _audio_ctx


def _beep():
    global _status
    ctx = _ensure_audio_context()
    if ctx is None:
        return
    try:
        osc = ctx.createOscillator()
        gain = ctx.createGain()
        osc.type = "sine"
        osc.frequency.value = _frequency
        now = ctx.currentTime
        end = now + _duration_ms / 1000.0
        # Short attack/release ramp avoids speaker-click on start/stop
        gain.gain.setValueAtTime(0.0, now)
        gain.gain.linearRampToValueAtTime(0.3, now + 0.01)
        gain.gain.linearRampToValueAtTime(0.0, end)
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.start(now)
        osc.stop(end + 0.05)
        _status = f"Beep @ {_frequency:.0f} Hz for {_duration_ms} ms"
    except Exception as e:
        _status = f"Beep failed: {e}"


def gui():
    global _frequency, _duration_ms
    imgui.text("WebAudio sanity check (Pyodide only)")
    imgui.separator()
    _, _frequency = imgui.slider_float("Frequency (Hz)", _frequency, 80.0, 2000.0)
    _, _duration_ms = imgui.slider_int("Duration (ms)", _duration_ms, 50, 1000)
    if imgui.button("Beep"):
        _beep()
    if _status:
        imgui.text_disabled(_status)


immapp.run(gui, window_title="WebAudio beep", window_size=(500, 220))
