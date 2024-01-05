from openai import OpenAI

class OpenAIAgent:
    def __init__(self, model):
        self._model = model 
        self._client = OpenAI()

    def chat_with_openai(self, messages, max_tokens=150, temperature=0):
        while True:
            #print("messages length:", len(messages))
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    #max_tokens=max_tokens,
                    temperature=temperature,
                )
                #print(response.choices[0].message.content)
                #print(response.choices[0].message.finish_reason)
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
                print(e)
                return None

