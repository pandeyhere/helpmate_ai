import openai
import os, ast
from modules.cache import queryResultsFromCache
from modules.rank import get_top_3_documents_by_rank

import openai
import os, ast

from tenacity import retry, wait_random_exponential, stop_after_attempt


openai.api_key= os.getenv("OPENAI_API_KEY")



def initialize_conversation(retrieved):
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''
    messages = [
        {"role":"system", "content":"You are an AI assistant to user."},
        {"role":"user", "content":f"""What is the revenue of uber in 2022?. You are provided the filing report of 2022 in'{retrieved}' """},
          ]
    return messages

# Define a Chat Completions API call
# Retry up to 6 times with exponential backoff, starting at 1 second and maxing out at 20 seconds delay
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_chat_model_completions(messages):
    MODEL = 'gpt-4-0613'

    try:
        response = openai.chat.completions.create(
            model = MODEL,
            messages = messages,
            )
    except Exception as e:
        print(e)
        raise Exception(f"Could not communicate to Open AI Server.{e.message}")


    return response.choices[0].message

def rag():

    try:
        print("Enter the query to get revenue of Uber in 2022 eg: What is the revenue of uber in 2022? ")
        query = input()

        results_df = queryResultsFromCache(query)

        retrieved = get_top_3_documents_by_rank(query, results_df)

        messages = initialize_conversation(retrieved=retrieved)

        response = get_chat_model_completions(messages=messages)

        print('\n' + response + '\n')

        return response
    except Exception as e:
        print(e)
        raise Exception(f"RAG could not be queried. {e.message}")

if __name__ == "__main__":
    rag( )
    
    