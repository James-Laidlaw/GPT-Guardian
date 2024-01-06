import secret_values
import requests
from openai import OpenAI

# gpt =================
gpt_key = secret_values.GPT_KEY
gpt_client = OpenAI(api_key=gpt_key)

# search ========================
subscription_key = secret_values.SEARCH_KEY
assert subscription_key
search_url = "https://api.bing.microsoft.com/v7.0/search"





# print(result_lst)


def if_misinfo(message):
    result = ""
    search_phrase = gen_search_phrase(message)
    info_on_web = search_result(message)
    info_on_web = str(info_on_web)
    prompt = f"given this search phrase: {search_phrase}\nand this results:{info_on_web},\n tell me if this message:{message} is misleading or ."
    stream = gpt_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            word = chunk.choices[0].delta.content 
            result += word
    return result 


def gen_search_phrase(message):
    new_message = "is " + message + " correct?"
    new_message = "correct this sentence:" + new_message
    search_phrase = ""
    stream = gpt_client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": new_message}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            word = chunk.choices[0].delta.content 
            search_phrase += word
    search_phrase = search_phrase.replace('"', '')
    search_phrase = search_phrase.replace("'", '')

    return search_phrase


def search_result(message):
    search_term = gen_search_phrase(message)
    print(search_term)
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    print(search_results)
    result_lst = []
    i = 0
    for v in search_results["webPages"]["value"]:
        if i == 5:
            break
        i += 1
        result_lst.append((v["name"], v["snippet"]))
    return result_lst

# print(if_misinfo("TRUMP WON 2024 WOOO"))
