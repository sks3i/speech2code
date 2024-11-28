import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import onnxruntime as ort

# Define the class for ONNX export
class WhisperForONNX(WhisperForConditionalGeneration):
    def forward(self, input_features, decoder_input_ids):
        return super().forward(input_features=input_features, decoder_input_ids=decoder_input_ids)

def export_whisper_to_onnx(model_name="openai/whisper-small.en", output_path="whisper-small.onnx"):
    # Load the model and processor
    model = WhisperForONNX.from_pretrained(model_name)
    processor = WhisperProcessor.from_pretrained(model_name)

    # Prepare dummy audio input (10 seconds of random audio at 16 kHz)
    sample_rate = 16000
    dummy_audio = np.random.rand(sample_rate * 10).astype(np.float32)
    inputs = processor(dummy_audio, return_tensors="pt", sampling_rate=sample_rate)

    # Extract encoder inputs
    input_features = inputs["input_features"]

    # Add decoder inputs (starting with the special token for the model)
    decoder_start_token_id = model.config.decoder_start_token_id
    decoder_input_ids = torch.tensor([[decoder_start_token_id]])

    # Export the model to ONNX
    torch.onnx.export(
        model,
        (input_features, decoder_input_ids),
        output_path,
        input_names=["input_features", "decoder_input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_features": {0: "batch_size", 2: "sequence_length"},
            "decoder_input_ids": {0: "batch_size", 1: "decoder_length"},
        },
    )
    print(f"Model exported to {output_path}")

def validate_onnx_model(model_path="whisper-small.onnx"):
    # Load ONNX model
    ort_session = ort.InferenceSession(model_path)

    # Dummy inputs for validation
    dummy_input_features = np.random.rand(1, 80, 3000).astype(np.float32)  # Example Mel spectrogram
    decoder_start_token_id = 50257  # Replace with actual model config value if different
    dummy_decoder_input_ids = np.array([[decoder_start_token_id]], dtype=np.int64)

    # Run inference
    outputs = ort_session.run(
        None,
        {"input_features": dummy_input_features, "decoder_input_ids": dummy_decoder_input_ids},
    )

    print("ONNX model inference successful")
    print("Output shape:", outputs[0].shape)

if __name__ == "__main__":
    # Specify model name and ONNX output path
    model_name = "openai/whisper-small.en"
    output_path = "whisper-small.onnx"

    # Export and validate
    export_whisper_to_onnx(model_name, output_path)
    validate_onnx_model(output_path)
