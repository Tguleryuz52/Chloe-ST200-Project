# ChloeAI — Kurulum

Python **3.11+** önerilir. Backend ve Unreal Editor **aynı Windows makinesinde** çalışır; ses dosyası yolu WebSocket mesajında **mutlak (absolute) path** olarak gönderilir.

## 1. Sanal ortam ve bağımlılıklar

PowerShell:

```powershell
cd C:\Users\2200004011\Desktop\Chloe_ST200\ChloeAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Backend\requirements.txt
```

## 2. API anahtarları

```powershell
copy Backend\.env.example Backend\.env
```

`Backend\.env` içinde doldur:

- `OPENAI_API_KEY` — Whisper (Speech-to-Text)
- `ANTHROPIC_API_KEY` — Claude
- `ELEVENLABS_API_KEY` — TTS
- `ELEVENLABS_VOICE_ID` — ElevenLabs panelinden bir ses kimliği

İsteğe bağlı: `AUDIO_OUTPUT_DIR` — boş bırakılırsa varsayılan `ChloeAI\Audio` (mutlak yola çözülür).

## 3. Backend’i çalıştırma

Çalışma dizini **ChloeAI** kökü olmalı:

```powershell
cd C:\Users\2200004011\Desktop\Chloe_ST200\ChloeAI
.\.venv\Scripts\Activate.ps1
python -m Backend.main
```

- WebSocket sunucusu: `ws://127.0.0.1:8765` (`.env` ile değiştirilebilir).
- Mikrofon: önce konuşmanız beklenir; cümle bittikten sonra kısa bir **sessizlik** utterance’ı bitirir (`SILENCE_DURATION_MS`, `MIN_AUDIO_RMS` ile ayarlanır).

## 4. WebSocket mesajı (Unreal)

Örnek:

```json
{
  "type": "speech",
  "audio_path": "C:\\Users\\...\\Chloe_ST200\\ChloeAI\\Audio\\response.wav",
  "visemes": [{"t": 0.0, "v": "sil"}, {"t": 0.05, "v": "aa"}],
  "text": "Claude'un ürettiği cevap metni"
}
```

- `audio_path`: **her zaman mutlak Windows yolu**; Unreal bu string ile dosyayı diskten okur (`FFileHelper`, runtime WAV vb.).
- `visemes`: ElevenLabs karakter hizasından türetilmiş sezgisel zaman çizelgesi (AnimBP’de eşleme sizde).

## 5. Unreal Engine entegrasyonu

`UnrealHelpers\README.md` dosyasına bakın: `WebSockets` modülü, `websocket_client` dosyalarının modüle eklenmesi ve Blueprint/C++ tarafında JSON ayrıştırma.

## 6. ElevenLabs ses formatı

Varsayılan çıktı `wav_44100`. Hesabınızda kısıt varsa `Backend\tts.py` içindeki `output_format` değerini ElevenLabs dokümantasyonuna göre güncellemeniz gerekebilir (ör. `pcm_24000`).
