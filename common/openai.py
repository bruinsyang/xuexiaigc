import openai
from openai import OpenAI
import tiktoken

class OpenAIAgent:
    def __init__(self, model):
        self._model = model 
        self._client = OpenAI()

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-1106"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def chat_with_openai(self, messages, max_tokens=2000, temperature=0.1):
        while True:
            #print("messages length:", len(messages))
            print("Predictied prompt tokens:", self.num_tokens_from_messages(messages, self._model))
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                #print(response.choices[0].message.content)
                #print(response.choices[0].message.finish_reason)
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                print(f'Tokens counted by OpenAI API: [prompt:{prompt_tokens}, completion:{completion_tokens}, total:{total_tokens}]')
                return response
            except openai.BadRequestError as e:
                if 'tokens' in str(e):
                    messages = remove_oldest_message(messages)
                else:
                    raise e
            except openai.RateLimitError as e:
                print(e)
                time.sleep(30)
            except Exception as e:
                raise e

