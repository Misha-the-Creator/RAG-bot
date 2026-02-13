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
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype="auto", device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
    
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

    def generate(self, chunk_list: List[str], think: bool, user_query: str) -> str:
        chunks_text = "\n".join(chunk_list)
        check_query = (
            f"Тебе даны следующие данные:\n\n{chunks_text}\n\n"
            f"Дают ли хоть одно из них ответ на следующий вопрос?: {user_query}\n\n"
            f"Ответ ТОЛЬКО 'да' или 'нет'"
        )

        for _ in range(5):
            raw_answer = self.generate_by_query(query=check_query, think=think)
            yes_no = raw_answer.strip().lower()
            if yes_no == "да":
                answer_query = (
                    f"Тебе даны следующие данные:\n\n{chunks_text}\n\n"
                    f"На основании этих данных ответь на следующий вопрос: {user_query}"
                )
                return self.generate_by_query(query=answer_query, think=think)
            elif yes_no == "нет":
                return "К сожалению, знаний в базе не хватает, чтобы ответить на данный вопрос :("

        return "Не удалось определить, содержится ли ответ в предоставленных данных."
            
