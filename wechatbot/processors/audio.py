#!/usr/bin/env python3
import whisper

def transcribe(path_to_recording, lang=None):
  model = whisper.load_model("small")
  result = model.transcribe(path_to_recording)
  return result["text"]