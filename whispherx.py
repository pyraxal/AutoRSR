import whisperx
import json
import gc 

def transcribe(wav_file):
    #Transcribes with whisperx
    device = "cuda" 
    audio_file = wav_file
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)
    model = whisperx.load_model("large-v3", device, compute_type=compute_type, language = "en")
    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)
    return format(result["segments"])

def format(a_list):
    #Formats into a nice json
    converted_data = {
    "transcriptions": [
        {
            "id": i + 1,
            "start_time": entry["start"],
            "end_time": entry["end"],
            "transcription": entry["text"]
        }
        for i, entry in enumerate(a_list)
    ]
    }
    json_output = json.dumps(converted_data, indent=2)
    return json_output
    




