import os
import sys
import re

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

from IndicTransToolkit import IndicProcessor


MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

SRC_LANG = "eng_Latn"
TGT_LANG = "kan_Knda"


def application_directory():
    """
    Returns the directory containing the application.
    """

    if getattr(sys, "frozen", False):
        return os.path.dirname(
            os.path.abspath(sys.executable)
        )

    return os.path.dirname(
        os.path.abspath(__file__)
    )


def get_model_directory():
    """
    Model is bundled/downloaded into:

        models/indictrans2-en-indic-dist-200M
    """

    return os.path.join(
        application_directory(),
        "models",
        "indictrans2-en-indic-dist-200M"
    )


class KannadaTranslator:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model_dir = get_model_directory()

        if not os.path.isdir(self.model_dir):
            raise FileNotFoundError(
                "Local translation model was not found:\n\n"
                + self.model_dir
            )

        self.processor = IndicProcessor(
            inference=True
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_dir,
            trust_remote_code=True,
            local_files_only=True
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_dir,
            trust_remote_code=True,
            local_files_only=True
        )

        self.model.to(self.device)
        self.model.eval()

    def split_text(self, text, max_chars=450):
        """
        Split long text into reasonably sized pieces.
        """

        text = text.strip()

        if not text:
            return []

        paragraphs = text.splitlines()

        result = []

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            sentences = re.split(
                r"(?<=[.!?])\s+",
                paragraph
            )

            current = ""

            for sentence in sentences:

                sentence = sentence.strip()

                if not sentence:
                    continue

                if len(current) + len(sentence) + 1 <= max_chars:
                    if current:
                        current += " "

                    current += sentence

                else:

                    if current:
                        result.append(current)

                    current = sentence

            if current:
                result.append(current)

        return result

    def translate_batch(self, sentences):

        if not sentences:
            return []

        batch = self.processor.preprocess_batch(
            sentences,
            src_lang=SRC_LANG,
            tgt_lang=TGT_LANG
        )

        inputs = self.tokenizer(
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():

            generated_tokens = self.model.generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=256,
                num_beams=5,
                num_return_sequences=1
            )

        generated_tokens = (
            generated_tokens
            .detach()
            .cpu()
            .tolist()
        )

        decoded = self.tokenizer.batch_decode(
            generated_tokens,
            src=False
        )

        translations = self.processor.postprocess_batch(
            decoded,
            lang=TGT_LANG
        )

        return translations

    def translate(self, text):

        sentences = self.split_text(text)

        if not sentences:
            return ""

        results = []

        batch_size = 4

        for i in range(
            0,
            len(sentences),
            batch_size
        ):

            batch = sentences[
                i:i + batch_size
            ]

            translated = self.translate_batch(
                batch
            )

            results.extend(translated)

        return "\n".join(results)
