import openai
from config import OPENAI_API_KEY
from db import Database
import json
import os
from tqdm import tqdm

openai.api_key = OPENAI_API_KEY


def generate_prompt(news_article):
    return """Please analyze the following news article, provide a summary, determine the sentiment (positive or negative or neutral) towards each mentioned financial symbol, and extract key financial information.:
News article:
""" + news_article + """\n
Return in the following json format (you must wrap the key and value in "") and don't provide any comments if sth is missing :
{
"Summary": "",
"Financial Information": "",
"Symbols":
{
 {
"Stocks": [], "Cryptocurrencies": [], "Forex": [], "Indices": [], "Futures": [], "Bonds": []
 }
},
"Symbol Sentiments": {"symbols": "sentiment"}
}\n\n
"""


def generate_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        stop=['\n\n']
    )
    return response


def parse_response(response):
    response = response['choices'][0]['message']['content']
    try:
        response = json.loads(response)
    except:
        response = {}
    return response


def main():
    date_from = input('Enter date from (YYYY-MM-DD): ')
    date_to = input('Enter date to (YYYY-MM-DD): ')
    query_symbol = input('Enter a symbol: ')
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    db = Database('global')
    db.init_db()

    news_from_db = db.get_news_from_db(date_from, date_to, query_symbol)

    print('Generating prompts and responses...')
    print('Total news items: ', len(news_from_db))
    print('*' * 50)
    for news in tqdm(news_from_db):
        print('Processing news: ', news['title'])
        if db.is_title_in_details_db(news['title']):
            print('News already in db: ', news['title'])
            continue
        prompt = generate_prompt(news['body'])
        try:
            response = generate_completion(prompt)
        except openai.APIError:
            print('API Error, skipping...')
            print(response['error']['message'])
            continue
        except:
            print('Unknown error, skipping...')
            continue
        
        response = generate_completion(prompt)
        response_dict = parse_response(response)
        # Save prompt and response to file
        try:
            with open(os.path.join(data_dir, 'prompts.txt'), 'a') as f:
                f.write(prompt)
            with open(os.path.join(data_dir, 'responses.txt'), 'a') as f:
                f.write(response['choices'][0]['message']['content'])
        except:
            pass
        
        print('Adding news details to db: ', news['title'])
        if db.add_news_details_to_db(news['title'], response_dict):
            print('Added news details to db: ', news['title'])
    print('Finished adding news details to db')
    print('*' * 50)
        
if __name__ == '__main__':
    main()
        