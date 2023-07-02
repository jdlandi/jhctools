# def verify_input():
#     pass

# def create_user(): 
#     return {
#         "username": "",
#         "password": "",
#         "flashcards" : "",
#         "portfolios": ""
#     }

import requests

import openai
openai.organization = "org-XBgyex0IxY9JO9E4jyMua7ZM"
openai.api_key =  "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"
models = openai.Model.list()

# def chatgpt(question):
#     chat_completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo", 
#                                                    messages = [{"role":"system", "content":"You are a financial learning assistant. Please answer the following question in 15 words or less. "}, 
#                                                                {"role": "user", "content":question}])

#     return chat_completion.choices[0].message.content

# print(chatgpt("What is forex?"))


prompts = {
  "flashcard" : "You are a financial learning assistant charged with the role of providing easy to understand examples to a college level student learning about finance and economics. Please answer the following question with as much brevity as you can while still providing high-quality teaching. MAX 20 WORDS:",
  "analyze_news" : "Your job is to analyze the following news regarding a financial object, whether it be a stock, currency, or anything else. Based on the following output, respond ONLY in one of three ways: [bad], [neutral], or [good]. Your response is taking into account the news and whether or not it will increase, decrease, or have no effect on the value of the financial asset. Again, you are only allowed to respond in these three ways and by no means are you allowed to deviate from this rule: [bad], [neutral], or [good]",
  "summ_news" : "You are a financial assistant with the task of understanding and summarizing news relating to a certain financial object, such as a stock, currency, or bond. Given the following news articles, respond in an html format highlighting the key points of the news you receive and most importantly, analyze the impact they will have on the market, the financial object itself, and anything else you think may be important. Respond only in the following format: <ul>\n <li> [insert point 1]</li> \n <li> [insert point 2] </li> \n [more <li> elements here as necessary] \n </ul> <p>  [insert analysis here]</p> ",
  "stock_input" : "Your role is to do your best to link a company name to it's corresponding finance symbol, for example, you would replace 'apple' with 'AAPL' and 'nvidia geforce' with 'NVDA'. Please keep the format exactly as is. Here is an example input: \"google\". Here is the output: \"GOOG\". Please interpret the following company/stock name into their stock symbol. Return ONLY a single stock symbol:  ",
  "format_currencies":
  "You will receive a forex rate, that is, a profit between two currencies that can be gained by trading USD to the first currency, the first currency to the second currency, then back to USD. It will look something like: HKD, JEP:1.00000032345. Please format exactly like this [currency1 name]([currency1 Symbol]) -> [currency2 name]([currency2 symbol]) : [rate] . The formatted version of the example input is like so: Hong Kong Dollars(HKD) -> Jersey Pounds(JEP):1.00000032345. Please format the following (or set of following) currencies:"
}
def ask_ai(question:str, prompt:str):
  chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompts[prompt]}, 
                                                                                  {"role": "user","content": question }])
  return chat_completion.choices[0].message.content

# print(ask_ai("USD,EUR: 1.0024", "format_currencies"))


def get_search(query:str, num: int):
  url = 'https://newsapi.org/v2/everything?' + f'q="{query}"&' + 'from=2023-05-20&' + 'sortBy=relevancy&' + f'pageSize={num}&' + 'searchIn=title&' + "language=en&" + 'apiKey=20178bc4c5624a8eb12652874011bc05'
  response = requests.get(url).json()
  simple = []
  for article in response["articles"]:
    #print(article)
    simple.append({
      "title": article["title"],
      "description": article['description'],
      "url": article["url"]
    })
  return simple

#print(get_search("elon", 3))