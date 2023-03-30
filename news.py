from bs4 import BeautifulSoup
from config import login_data
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db import Database

location = input('Enter a location [China, Global]: ').lower()
BASE_URL = 'https://www.tradingview.com' if location == 'global' else 'https://cn.tradingview.com'

driver = webdriver.Chrome()
# Make a GET request to the login page
driver.get(BASE_URL + '/accounts/signin/')
driver.implicitly_wait(10)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Remove unwanted elements
for elem in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'link']):
    elem.decompose()

html = str(soup)

# Toggle the email button
# element = soup.select_one('span.tv-signin-dialog__social.tv-signin-dialog__toggle-email.js-show-email')
element = driver.find_element(By.CSS_SELECTOR, '.js-show-email')
element.click()

driver.implicitly_wait(10)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

for elem in soup(['script', 'link']):
    elem.decompose()

html = str(soup)
username_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"][id*="email-signin__user-name-input"]'))
)
password_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"][id*="email-signin__password-input"]'))
)

username_input.send_keys(login_data['username'])
password_input.send_keys(login_data['password'])

submit_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"][id*="email-signin__submit-button"]'))
)
submit_button.click()

options = ['topstories', 'stock', 'crypto', 'forex', 'index', 'futures', 'bond', 'economic']
# Read an input from the user
url = ''
user_input = input('Enter a market: ' + str(options) + ' or press enter to get all news: ').lower()
if user_input in options:
    url = BASE_URL + '/news/?market=' + user_input
else:
    url = BASE_URL + '/news/'

driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Unwanted links
unwanted_links = ['/news/', '/news/?market=topstories', '/news/?market=stock', '/news/?market=crypto', '/news/?market=forex',
           '/news/?market=index', '/news/?market=futures', '/news/?market=bond', '/news/?market=economic']

# Use BeautifulSoup to extract the information you need
# For example, to extract all the links on the page:
links = soup.find_all(
    'a', href=lambda href: href and href.startswith('/news/'))
news_links = []
for link in links:
    if link.get('href') not in unwanted_links:
        news_links.append(BASE_URL + link.get('href'))

# Save the information you extracted in a file
# Make a directory called 'data' in the same directory as this file
# and save the file there
cwd = os.getcwd()

data_dir = os.path.join(cwd, 'data')
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

filename = os.path.join(data_dir, 'news.txt')
with open(filename, 'w') as file:
    for link in news_links:
        if link not in unwanted_links:
            file.write(link + '\n')

db = Database(location=location)
db.init_db()

for news in news_links:
    driver.get(news)
    driver.implicitly_wait(10)
    news_html = driver.page_source
    news_soup = BeautifulSoup(news_html, 'html.parser')
    
    article = news_soup.find('article')
    
    if article is None:
        continue
    
    title = article.find('h1').get_text()
    date_time = article.find('time')['datetime']
    
    symbol_elem = news_soup.select('span[class*=description]')
    symbol = []
    for elem in symbol_elem:
        sym = elem.get_text().strip()
        if len(sym) > 0:
            symbol.append(sym)
    symbol = ', '.join(symbol)
    
    body_elem = news_soup.select('div[class*=body]')
    body = []
    for elem in body_elem:
        text = elem.get_text().strip()
        if len(text) > 0:
            body.append(elem.get_text().strip() + '\n')
    body = ''.join(body)
    
    add = db.add_news_to_db(title, date_time, symbol, body)
    if add:
        print(f'Added news "{title}" to database')
    else:
        print(f'News "{title}" already exists in database')
    
        
driver.quit()
# Save the information you extracted in a file
news_filename = os.path.join(data_dir, 'news_content.txt')
news_from_db = db.get_news_from_db()
db.close()
with open(news_filename, 'w') as file:
    for news in news_from_db:
        try:
            file.write(news['title'] + '\n')
            file.write(news['date_time'] + '\n')
            file.write(news['symbol'] + '\n')
            file.write(news['body'])
            file.write('*' * 100 + '\n')
        except:
            continue
