import sqlite3
import json
from datetime import datetime, time

class Database:
    def __init__(self, location):
        self.conn = sqlite3.connect('news.sqlite') if location == 'global' else sqlite3.connect('news_china.sqlite')
        self.c = self.conn.cursor()
        self.location = location

    def init_db(self):
        """
        Creates the SQLite database and the news table if it does not already exist.
        """
        self.c.execute('''CREATE TABLE IF NOT EXISTS news
                     (title TEXT PRIMARY KEY, date_time TEXT, symbol TEXT, body TEXT)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS news_details
                     (title TEXT PROIMARY KEY,
                      summary TEXT,
                      financial_information TEXT,
                      symbols TEXT,
                      symbol_sentiments TEXT,
                      FOREIGN KEY (title) REFERENCES news(title) ON DELETE CASCADE)''')

        self.conn.commit()

    def is_title_in_db(self, title):
        """
        Checks if a news item exists in the SQLite database.

        Args:
            title (str): The title of the news item.

        Returns:
            bool: True if the news item exists in the database, False otherwise.
        """
        self.c.execute('SELECT * FROM news WHERE title=?', (title,))
        result = self.c.fetchone()

        return result is not None

    def add_news_to_db(self, title, date_time, symbol, body):
        """
        Adds a news item to the SQLite database.

        Args:
            title (str): The title of the news item.
            date_time (str): The date and time of the news item.
            symbol (str): The stock symbol mentioned in the news item.
            body (str): The body of the news item.

        Returns:
            bool: True if the news item was added to the database, False otherwise.
        """
        if self.is_title_in_db(title):
            return False

        self.c.execute('INSERT INTO news VALUES (?, ?, ?, ?)', (title, date_time, symbol, body))
        self.conn.commit()

        return True

    def get_news_from_db(self, date_from=None, date_to=None, symbol=None):
        """
        Retrieves news items from the SQLite database within the specified time range.

        Args:
            date_from (str): The start date for the time range (inclusive), in 'YYYY-MM-DD' format (e.g., '2023-03-01').
            date_to (str): The end date for the time range (inclusive), in 'YYYY-MM-DD' format (e.g., '2023-03-31').
            symbol (str): The symbol to filter the news items by.

        Returns:
            list: A list of dictionaries containing news data.
        """
        def convert_date_time():
            # Convert the date strings to ISO 8601 format with time components
            date_from_iso, date_to_iso = None, None
            if date_from is not None and date_from != '':
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                date_from_iso = datetime.combine(
                    date_from_obj, time.min).isoformat()
            if date_to is not None and date_to != '':
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                date_to_iso = datetime.combine(date_to_obj, time.max).isoformat()
            return date_from_iso, date_to_iso

        date_from, date_to = convert_date_time()

        query = 'SELECT * FROM news'
        if date_from is not None and date_to is not None:
            query += f' WHERE date_time BETWEEN "{date_from}" AND "{date_to}"'
        elif date_from is not None:
            query += f' WHERE date_time > "{date_from}"'
        elif date_to is not None:
            query += f' WHERE date_time < "{date_to}"'

        if symbol is not None and symbol != '':
            if 'WHERE' in query:
                query += f' AND symbol LIKE "%{symbol}%"'
            else:
                query += f' WHERE symbol LIKE "%{symbol}%"'

        self.c.execute(query)
        result = self.c.fetchall()

        news_list = []
        for news in result:
            news_dict = {
                'title': news[0],
                'date_time': news[1],
                'symbol': news[2],
                'body': news[3]
            }
            news_list.append(news_dict)
        return news_list
          
    def is_title_in_details_db(self, title):
        """
        Checks if a news item exists in the SQLite database.

        Args:
            title (str): The title of the news item.

        Returns:
            bool: True if the news item exists in the database, False otherwise.
        """  
        self.c.execute('SELECT * FROM news_details WHERE title=?', (title,))
        result = self.c.fetchone()
        return result is not None

    def add_news_details_to_db(self, title, response):
        """
        
        print('in function')
        Adds the details of a news item to the SQLite database.

        Args:
            title (str): The title of the news item.
            response (dict): A dictionary containing the details of the news item in the 
                                following format:
                                {
                                    "Summary": "", 
                                    "Financial Information": "",
                                    "Symbols": 
                                        {
                                            "Stocks": [], 
                                            "Cryptocurrencies": [], 
                                            "Forex": [], 
                                            "Indices": [], 
                                            "Futures": [], 
                                            "Bonds": []
                                        }, 
                                    "Symbol Sentiments": 
                                        {
                                            [symbol]: [sentiment],
                                            ...     
                                        }
                                }
        """
        if self.is_title_in_details_db(title):
            return False
        
        try:
            summary = response['Summary']
            financial_information = response['Financial Information']
            symbols = json.dumps(response['Symbols'])
            symbol_sentiments = json.dumps(response['Symbol Sentiments'])
        except KeyError:
            print(f'News {title} does not have all the required fields')
            return
        
        self.c.execute('INSERT INTO news_details VALUES (?,?,?,?,?)', (title, summary,
                                                                    financial_information, symbols, symbol_sentiments))
        self.conn.commit()
        return True
        
    def get_news_details_from_db(self, title):
        """
        Retrieves the details of a news item from the SQLite database.

        Args:
            title (str): The title of the news item.

        Returns:
            dict: A dictionary containing the details of the news item.
        """
        self.c.execute('SELECT * FROM news_details WHERE title=?', (title,))
        result = self.c.fetchone()
        if result is None:
            return None
        return {
            'title': result[0],
            'summary': result[1],
            'financial_information': result[2],
            'symbols': json.loads(result[3]),
            'symbol_sentiments': json.loads(result[4])
        }

    def close(self):
        """
        Closes the connection to the SQLite database.
        """
        self.conn.close()