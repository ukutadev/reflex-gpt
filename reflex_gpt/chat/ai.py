#LangChain ->best for python  LLMs

from decouple import config
from openai import OpenAI

OPENAI_API_KEY=config("OPENAI_API_KEY",cast=str, default=None)
OPENAI_MODEL="gpt-4o-mini"

#client = OpenAI()

def get_client():
    return OpenAI(api_key=OPENAI_API_KEY)

def get_llm_response(gpt_messages):
    client = get_client()
    completion = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=gpt_messages
    )
    return completion.choices[0].message.content    



#response = client.responses.create(
    #model="gpt-5",
    #input="Write a short bedtime story about a unicorn."
#)

#print(response.output_text)
