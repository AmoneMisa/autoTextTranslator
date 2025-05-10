from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class LocalTranslator:
    def __init__(self, model_name="facebook/nllb-200-3.3B", src_lang="eng_Latn", tgt_lang="rus_Cyrl"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")
        self.device = self.model.device
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def translate(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True).to(self.device)
        inputs["forced_bos_token_id"] = self.tokenizer.convert_tokens_to_ids(self.tgt_lang)
        output = self.model.generate(**inputs, max_length=512)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)
