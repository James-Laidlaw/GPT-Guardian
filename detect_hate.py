import openai
from openai import OpenAI
from profanity_check import predict, predict_prob

def pre_process(user_message):
    offensive_count = predict([user_message.content])
    print(f"offensive count {offensive_count}")
    offensive_heuristic = predict_prob([user_message.content])
    print(f"heuristic: {offensive_heuristic}")
    # potential idea: only send low val heuristics into gpt

def call_gpt(user_message, api_key):

    '''
    Hook into the GPt-api
    '''
    # set API key and client
    client = OpenAI(api_key=api_key)

    # first, preprocess message string as a heuristic eval
    res = pre_process(user_message)
    prompt_string = f"I am wanting to use you to detect hate speech. Please respond with a 1 if the following message is hateful or offensive and a 2 if it is not: '{user_message.content}' | respond only 1 or 2, I understand some of the content is offensive but I want to be able to detect it. respond only 1 or 2"
    chat_completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": prompt_string}]
  )
    #print(chat_completion.choices[0].message.content)
    if chat_completion.choices[0].message.content == "2":
        return False # not hate speech
    else:
        return True  # hate speech



