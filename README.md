<div align="center">

<img src="assets/govindtank-avatar.png" width="180" alt="Govind Tank avatar" />

# Govind Tank

**Mobile architect & developer** — design systems, ship packages, automate the boring.

<img src="assets/terminal-intro.svg" alt="Terminal intro animation" width="100%" />

</div>

---

## Solutions, as code

**CASE 01 — phone validation across 50+ countries was guesswork**

```python
# country_code_picker v2 broke on Flutter master · fake length ranges everywhere
def validate(phone: str, country: str) -> Verdict:
    meta  = Metadata.refresh()                      # libphonenumber data, always current
    ok_len  = is_mobile_length(phone, meta[country])   # real ranges: 8–10, 10–11 digits
    ok_type = not meta[country].mobile_only or is_mobile(phone)  # landlines rejected
    return Verdict(valid=ok_len and ok_type)

ship("country_mobile_validator", version="0.2.0", pana=160, native_deps=0)
```

**CASE 02 — cloud speech-to-text: slow, private, metered**

```python
# whisper.cpp bridged into Flutter — the model runs on the device, not a server
class FlutterWhisper:
    def transcribe(audio: WAV, model: WhisperModel) -> Stream[Partial]:
        yield from whisper.cpp.stream(audio, model)   # off-main-thread
        # cancel() aborts mid-flight · results arrive as they decode

ship("flutter_whisper", version="0.1.0", offline=True, cost_per_user=0)
```

**CASE 03 — waveform rendering stuttered on long audio**

```dart
// GPU-accelerated — zoom, region selection, cue markers, peak extraction
class WaveformPro extends StatelessWidget {
  Widget build(_) => CustomPaint(
    painter: WaveformPainter(peaks: AudioPeaks.extract(wav)),
    // shader-based rasterization keeps 60fps on hour-long tracks
  );
}

ship("waveform_pro", version="1.0.0", renderer="GPU shader");
```

**CASE 04 — missed market breakouts because scanning was manual**

```python
# NSE scanner + options paper-trading bot, runs itself now
SCHEDULE = cron("09:15", "12:00", "15:30", "17:00", tz="IST")   # 4 daily jobs
def on_signal(signal: DarvaXBreakout) -> None:
    Telegram.send(signal.format())      # alerts land before you open the app
    paper_portfolio.update(signal)      # Short Put Credit Spread · ₹1L virtual

ship("stock-scanner", automation=100, human_attention=0)
```

---

## Currently shipping

- **country_mobile_validator** v0.2.0 — per-country mobile validation, pana 160/160
- **flutter_whisper** v0.1.0 — on-device speech-to-text, offline & private
- **waveform_pro** v1.0.0 — GPU waveform: zoom, regions, cue markers
- **quote_painter** v0.1.0 — styled text on image/video canvas
- **cmp-keyboard / cmp-linked-text / cmp-clipboard** — Compose Multiplatform libraries
- **stock-scanner** — NSE scanner + paper trading bot, 4 daily crons, Telegram alerts

## Recent activity

<!-- ACTIVITY:START -->
<!-- ACTIVITY:END -->

## Elsewhere

- Repositories — [github.com/govindtank](https://github.com/govindtank?tab=repositories)
- Portfolio — [govindtank.github.io](https://govindtank.github.io)
- LinkedIn — [linkedin.com/in/govindtank](https://www.linkedin.com/in/govindtank/)
- Email — [govindtank600@gmail.com](mailto:govindtank600@gmail.com)

---

<img src="https://raw.githubusercontent.com/govindtank/govindtank/master/dist/github-snake.svg" alt="Snake eating contributions" width="100%" />

_Last updated: <!--UPDATED-->_
