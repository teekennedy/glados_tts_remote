import io
import subprocess
import time
import typing as t

import torch
from nltk import download
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
from scipy.io.wavfile import write

from utils.tools import prepare_text

print("Initializing TTS Engine...")

kwargs = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.PIPE,
    "stdin": subprocess.PIPE,
}


class tts_runner:
    def __init__(self, use_p1: bool = False, log: bool = False):
        self.log = log
        if use_p1:
            self.emb = torch.load("models/emb/glados_p1.pt", weights_only=False)
        else:
            self.emb = torch.load("models/emb/glados_p2.pt", weights_only=False)
        # Select the device
        if torch.cuda.is_available():
            self.device = "cuda"
            vocoder_model = "models/vocoder-gpu.pt"
        elif torch.is_vulkan_available():
            self.device = "vulkan"
            vocoder_model = "models/vocoder-gpu.pt"
        else:
            self.device = "cpu"
            vocoder_model = "models/vocoder-cpu-hq.pt"

        # Load models
        self.glados = torch.jit.load("models/glados-new.pt")
        self.vocoder = torch.jit.load(vocoder_model, map_location=self.device)
        for i in range(2):
            init = self.glados.generate_jit(prepare_text(str(i)), self.emb, 1.0)
            init_mel = init["mel_post"].to(self.device)
            _ = self.vocoder(init_mel)

    @torch.no_grad()
    def run_tts(self, text: str, format: str = "wav", alpha: float = 1.0) -> bytes:
        sentences = self.split_sentences(text)

        result_audio = AudioSegment.silent(100)

        for i, sentence in enumerate(sentences):
            # Generate generic TTS-output
            old_time = time.time()
            tts_output = self.glados.generate_jit(prepare_text(sentence), self.emb, alpha)
            if self.log:
                print(
                    "Forward Tacotron took "
                    + str((time.time() - old_time) * 1000)
                    + "ms"
                )

            # Use HiFiGAN as vocoder to make output sound like GLaDOS
            old_time = time.time()
            mel = tts_output["mel_post"].to(self.device)
            audio = self.vocoder(mel)
            if self.log:
                print("HiFiGAN took " + str((time.time() - old_time) * 1000) + "ms")

            # Normalize audio to fit in wav-file
            audio = audio.squeeze()
            audio = audio * 2147483647
            audio = audio.cpu().numpy().astype("int32")
            tmp_file = io.BytesIO()
            write(tmp_file, 22050, audio)

            result_audio += AudioSegment(tmp_file)

            # add a pause between sentences
            if i < len(sentences) - 1:
                result_audio += AudioSegment.silent(500)

        result_file = io.BytesIO()
        result_audio.export(result_file, format=format)
        return result_file.getvalue()

    def split_sentences(self, text: str)-> t.List[str]:
        """Helper function to split a text into a list of sentences using nltk."""
        download("punkt_tab", quiet=self.log)
        return sent_tokenize(text)
