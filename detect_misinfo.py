import secret_values
import requests
# subscription_key = secret_values.SEARCH_KEY

# assert subscription_key



# search_url = "https://api.bing.microsoft.com/v7.0/search"



# search_term = "Did Trump win 2024 election?"

# # test search

# headers = {"Ocp-Apim-Subscription-Key": subscription_key}
# params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
# response = requests.get(search_url, headers=headers, params=params)
# response.raise_for_status()
# search_results = response.json()

# result_lst = []
# i = 0
# for v in search_results["webPages"]["value"]:
#     if i == 5:
#         break
#     i += 1
#     result_lst.append((v["name"], v["snippet"]))




# print(result_lst)


def if_misinfo(message):
    pass


def gen_search_phrase(message):
    pass

def search_result(message):
    pass

