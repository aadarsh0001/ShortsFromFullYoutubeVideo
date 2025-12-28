from transformers import WhisperForConditionalGeneration, WhisperProcessor

class WhisperLoader:
    def __init__(self, model_name="openai/whisper-base"):
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)

    def transcribe(self, audio_input):
        inputs = self.processor(audio_input, return_tensors="pt", sampling_rate=16000)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription

    def detect_language(self, audio_input):
        inputs = self.processor(audio_input, return_tensors="pt", sampling_rate=16000)
        language_probs = self.model.detect_language(**inputs)
        return language_probs.argmax().item()  # Returns the index of the detected language