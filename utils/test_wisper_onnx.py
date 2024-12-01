import argparse
import librosa
import numpy as np
import torch

from gtts import gTTS
from optimum.onnxruntime import ORTModelForSpeechSeq2Seq
from transformers import AutoTokenizer, AutoFeatureExtractor


def generate_speech(text: str, save_fpath: str):
    tts = gTTS(text)
    tts.save(save_fpath)
    print(f"Audio file saved: {save_fpath}")


def load_model(onnx_model_fpath: str):
    model = ORTModelForSpeechSeq2Seq.from_pretrained(onnx_model_fpath, use_cache=False)
    return model


def extract_features(audio_np: np.ndarray):
    feature_extractor = AutoFeatureExtractor.from_pretrained("openai/whisper-small")
    audio_features = feature_extractor(audio, return_tensors="pt").input_features
    return audio_features


def decode(logits: torch.Tensor):
    tokenizer = AutoTokenizer.from_pretrained("openai/whisper-small")
    text = tokenizer.batch_decode(logits, skip_special_tokens=True)[0]
    return text


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("onnx_model_fpath", type=str, help="Path to the ONNX model file")
    args = args.parse_args()

    audio_save_fpath = "text.wav"
    audio_text = "This is a text file for whisper model. Let's see if is transcribes this text correctly."

    generate_speech(audio_text, audio_save_fpath)
    audio, sr = librosa.load(audio_save_fpath, sr=16000)

    model = load_model(args.onnx_model_fpath)
    audio_features = extract_features(audio)
    logits = model.generate(input_features=audio_features)
    text = decode(logits)

    print(f"Transcribed text: {text}")