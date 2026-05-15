import os
import requests

BASE_URL = "https://api.sunbird.ai"

LANGUAGE_TO_SPEAKER = {
    "Luganda": 248,
    "Runyankole": 243,
    "Ateso": 242,
    "Lugbara": 245,
    "Acholi": 241,
}

def _get_token():
    token = os.getenv("SUNBIRD_API_TOKEN")
    if not token:
        raise ValueError("SUNBIRD_API_TOKEN not set. Add it to your .env file.")
    return token

def _headers():
    return {"Authorization": f"Bearer {_get_token()}"}

def _extract_text(data: dict) -> str:
    """Safely extract text from Sunflower API response."""
    if "output" in data:
        out = data["output"]
        if isinstance(out, dict):
            return out.get("content") or out.get("text") or str(out)
        return str(out)
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return str(data)

def transcribe_audio(audio_path: str) -> str:
    url = f"{BASE_URL}/tasks/stt"
    with open(audio_path, "rb") as f:
        response = requests.post(
            url,
            files={"audio": f},
            headers=_headers(),
            timeout=120,
        )
    response.raise_for_status()
    data = response.json()
    if "output" in data:
        out = data["output"]
        if isinstance(out, dict):
            return out.get("text") or str(out)
        return str(out)
    return str(data)

def summarise(text: str) -> str:
    url = f"{BASE_URL}/tasks/sunflower_inference"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Summarise the following text "
                    "concisely in 3-5 sentences, preserving the key points."
                ),
            },
            {"role": "user", "content": f"Please summarise this text:\n\n{text}"},
        ]
    }
    response = requests.post(
        url,
        json=payload,
        headers={**_headers(), "Content-Type": "application/json"},
        timeout=60,
    )
    response.raise_for_status()
    return _extract_text(response.json())

def translate(text: str, target_language: str) -> str:
    url = f"{BASE_URL}/tasks/sunflower_inference"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a professional translator. Translate the following text "
                    f"into {target_language}. Output only the translated text, nothing else."
                ),
            },
            {"role": "user", "content": text},
        ]
    }
    response = requests.post(
        url,
        json=payload,
        headers={**_headers(), "Content-Type": "application/json"},
        timeout=300,
    )
    response.raise_for_status()
    return _extract_text(response.json())

def synthesise_speech(text: str, language: str) -> bytes:
    speaker_id = LANGUAGE_TO_SPEAKER.get(language)
    if speaker_id is None:
        raise ValueError(f"No TTS speaker available for language: {language}")

    url = f"{BASE_URL}/tasks/tts"
    payload = {"text": text, "speaker_id": speaker_id}
    response = requests.post(
        url,
        json=payload,
        headers={**_headers(), "Content-Type": "application/json"},
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()
    if "output" in data:
        audio_url = data["output"].get("audio_url")
    else:
        audio_url = data.get("audio_url")

    if not audio_url:
        raise ValueError(f"No audio_url in TTS response: {data}")

    audio_response = requests.get(audio_url, timeout=60)
    audio_response.raise_for_status()
    return audio_response.content