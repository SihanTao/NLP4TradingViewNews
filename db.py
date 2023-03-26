import sqlite3
from datetime import datetime, time

def init_db():
    """
    Creates the SQLite database and the news table if it does not already exist.
    """
    conn = sqlite3.connect('news.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (title TEXT PRIMARY KEY, date_time TEXT, symbol TEXT, body TEXT)''')
    conn.commit()
    conn.close()

def is_title_in_db(title):
    """
    Checks if a news item exists in the SQLite database.
    
    Args:
        title (str): The title of the news item.
        
    Returns:
        bool: True if the news item exists in the database, False otherwise.
    """
    conn = sqlite3.connect('news.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM news WHERE title=?', (title,))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_news_to_db(title, date_time, symbol, body):
    """
    Adds a news item to the SQLite database if the title does not already exist.

    Args:
        title (str): The title of the news item.
        date_time (str): The date and time of the news item.
        symbol (str): The symbols associated with the news item.
        body (str): The body text of the news item.

    Returns:
        bool: True if the news item was added to the database, False otherwise.
    """
    if is_title_in_db(title):
        return False
    conn = sqlite3.connect('news.sqlite')
    c = conn.cursor()
    
    # Convert the date_time string to a datetime object
    date_time_obj = datetime.strptime(date_time, '%a, %d %b %Y %H:%M:%S %Z')
    data_time_iso = date_time_obj.isoformat()
    
    c.execute('INSERT INTO news VALUES (?,?,?,?)', (title, data_time_iso, symbol, body))
    conn.commit()
    conn.close()
    return True

def get_news_from_db(date_from=None, date_to=None, symbol=None):
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
        if date_from is not None:            
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_from_iso = datetime.combine(date_from_obj, time.min).isoformat()
        if date_to is not None:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_iso = datetime.combine(date_to_obj, time.max).isoformat()
        return date_from_iso, date_to_iso
    
    conn = sqlite3.connect('news.sqlite')
    c = conn.cursor()
    
    date_from, date_to = convert_date_time()
    
    query = 'SELECT * FROM news'
    if date_from is not None and date_to is not None:
        query += f' WHERE date_time BETWEEN "{date_from}" AND "{date_to}"'
    elif date_from is not None:
        query += f' WHERE date_time > "{date_from}"'
    elif date_to is not None:
        query += f' WHERE date_time < "{date_to}"'
        
    if symbol is not None:
        if 'WHERE' in query:
            query += f' AND symbol LIKE "%{symbol}%"'
        else:
            query += f' WHERE symbol LIKE "%{symbol}%"'
            
    c.execute(query)
    result = c.fetchall()
    conn.close()
    
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