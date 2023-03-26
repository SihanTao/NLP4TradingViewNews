# NLP4TradingViewNews
This is a project to extract news from TradingView and use OpenAI API to analyse the news on it.
To use it, you need to have a TradingView account and an OpenAI API key.
Please refer to the following link to get your API key: https://beta.openai.com/docs/api-reference/authentication
Also, you need to create a file named "config.py" in the same directory as the news.py file.
In this file, you need to add the following lines:
```python
# TradingView account
login_data = {
    'username': 'your TradingView username or email',
    'password': 'your TradingView password',
}

openai_api_key = 'your OpenAI API key'
```
Then, you can run the news.py file to get the news and analyse it. Note the login function is only for email sign in. If you use Google or Facebook to sign in, you need to change the code in the login function.