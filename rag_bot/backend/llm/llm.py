from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer
from rag_bot.backend.logger.logger_config import logger1

class LLM:
    def __init__(self, model_path):
        self.model = None
        self.tokenizer = None
        self.logger = logger1
        self.model_path = model_path

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype="auto", device_map="auto")
    
    def generate_by_query(self, query, think):

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
        
        return content

    def generate(self, chunk_list: List[str], think: bool, user_query):
        allowed_tokens = ["да", "нет"]
        query = f"Тебе даны следующие данные:\n\nf'{'\n'.join(chunk_list)}\n\nДают ли хоть одно из них ответ на следующий вопрос?: {user_query}\n\nОтвет ТОЛЬКО 'да' или 'нет'"
        yes_or_no = None
        while yes_or_no not in allowed_tokens:
            self.logger.debug(f'{yes_or_no=}')
            yes_or_no = self.generate_by_query(query=query, think=think)
            if yes_or_no == 'да':
                query = f"Тебе даны следующие данные:\n\nf'{'\n'.join(chunk_list)}\n\nНа основании этих данны ответь на следующий вопрос: {user_query}"
                return self.generate_by_query(query=query, think=think)
            elif yes_or_no == 'нет':
                return 'К сожалению, знаний в базе не хватает, чтобы ответить на данный вопрос :('
            
