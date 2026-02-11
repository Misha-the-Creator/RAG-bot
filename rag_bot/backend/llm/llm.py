from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLM:
    def __init__(self, model_path):
        self.model = None
        self.tokenizer = None
        self.model_path = model_path

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype="auto", device_map="auto")
    
    def generate(self, chunk_list: List[str], think: bool):
        questions_arr = []
        for chunk in chunk_list:
            query = f"Write a question that can be asked of this text:\n\n{chunk}"
            messages = [{"role": "user", "content": query}]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=think
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=32768
            )
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

            try:
                index = len(output_ids) - output_ids[::-1].index(151668)
            except ValueError:
                index = 0

            content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

            questions_arr.append(content)
        
        return questions_arr