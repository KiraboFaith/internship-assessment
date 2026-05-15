from mutagen import File as MutagenFile
from backend.sunbird_client import (
    transcribe_audio,
    summarise,
    translate,
    synthesise_speech,
)

MAX_AUDIO_SECONDS = 300  # 5 minutes


def get_audio_duration(path: str) -> float:
    try:
        audio = MutagenFile(path)
        if audio and audio.info:
            return audio.info.length
    except Exception:
        pass
    return 0.0


def run_pipeline(
    input_type: str,
    text_input: str | None,
    audio_path: str | None,
    target_language: str,
) -> dict:
    result = {
        "transcript": None,
        "summary": None,
        "translation": None,
        "audio_bytes": None,
        "error": None,
    }

    try:
        if input_type == "audio":
            if not audio_path:
                raise ValueError("No audio file provided.")

            duration = get_audio_duration(audio_path)
            if duration > MAX_AUDIO_SECONDS:
                mins = duration / 60
                raise ValueError(
                    f"Audio is {mins:.1f} minutes long. "
                    "Please upload a file shorter than 5 minutes."
                )

            result["transcript"] = transcribe_audio(audio_path)
            source_text = result["transcript"]
        else:
            if not text_input or not text_input.strip():
                raise ValueError("Please enter some text before running the pipeline.")
            source_text = text_input.strip()

        result["summary"] = summarise(source_text)
        result["translation"] = translate(result["summary"], target_language)
        result["audio_bytes"] = synthesise_speech(result["translation"], target_language)

    except ValueError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"API error: {e}"

    return result