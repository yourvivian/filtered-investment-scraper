from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import os
import json

app = Flask(__name__, template_folder='Templates')

def get_search_strings():
    # Replace 'your_file.xlsx' with the actual file path and 'Sheet1' with the sheet name
    file_name = 'funds-list.xlsx'
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name) # Heroku deploy
    #file_path = '/Users/viviannguyen/Documents/Archive/Inv_Office/github-demo/funds-list.xlsx' # REPLACE THIS PATH
    sheet_name = 'managers'

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Extract search strings from a specific column (replace 'Column_Name' with the actual column name)
    search_strings_column = 'keywords'
    search_strings = set(df[search_strings_column].dropna().astype(str).str.lower())
    return search_strings

def scrape_deals():
    # Set Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.binary_location = r"/Applications/Chrome.app" # local host use this
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")  # heroku use this
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    

    # Set Chrome WebDriver path
    # chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    # Initialize Chrome WebDriver with service and options
    #service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

    driver = webdriver.Chrome(options=chrome_options) #service=service
    '''
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    # Set Chrome WebDriver path
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    #driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=chrome_options)
    '''
    # Maximize window
    #driver.maximize_window()

    # Navigate to the URL
    driver.get("https://www.axios.com/newsletters/axios-pro-rata")
    # Print the current URL
    print("Current URL:", driver.current_url)

    # Print the page source
    print("Page Source:", driver.page_source)

    # Perform scraping operations here

    # Close the WebDriver
    #driver.quit()
    
    '''
    BROWSER_PATH = r"/Applications/Chrome.app"
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument("--headless=new")
    OPTIONS.binary_location = BROWSER_PATH
    OPTIONS.add_experimental_option("detach", True)

    URL = 'https://www.axios.com/newsletters/axios-pro-rata'

    driver = webdriver.Chrome(options=OPTIONS)
    driver.get(URL)
    '''
    master_list = []

    for i in range(2, 15):
        try:
            story_id = f'story{i}'
            articles = driver.find_element(By.ID, story_id)
            titles = articles.find_elements(By.CSS_SELECTOR, 'div p')
            article_titles = [title.text for title in titles]
            master_list.extend(article_titles)
            for title in article_titles:
                print(title)
            print("Article titles:", article_titles)
        except Exception as e:
            print(f"Error processing story with ID {story_id}: {e}")
            break
    print("All deals:", master_list)

    # Filter and print
    relevant_deals = []
    for title in master_list:
        relevant_deals.append(title)
        '''
        for search_string in search_strings:
            if search_string.lower() in title.lower():
                relevant_deals.append(f"[{search_string}] -- {title}")
        '''
    print("Scraped deals:", relevant_deals)
    output_file = 'scraped_data.json'
    with open(output_file, 'w') as json_file:
        #json_file.truncate(0)  # Clear the file before writing
        for deal in relevant_deals:
            json.dump({'scraped_deal': deal}, json_file)
            json_file.write('\n')  # Add a newline after each JSON object

    # Close the WebDriver
    driver.quit()

    return relevant_deals

def read_json_file(file_path):
    data = []
    with open(file_path, 'r') as json_file:
        for line in json_file:
            data.append(json.loads(line))
    return data

def filter_data(search_strings, scraped_data):
    filtered_data = []
    for deal in scraped_data:
        for search_string in search_strings:
            if search_string.lower() in deal['scraped_deal'].lower():
                filtered_data.append(deal)
    return filtered_data

'''
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape')
def scrape_data():
    relevant_deals = scrape_deals()

    # Read the contents of the JSON file
    with open('scraped_data.json', 'r') as json_file:
        json_data = [json.loads(line) for line in json_file]
        #json_data = json_file.read()

    return render_template('index.html', json_data=json_data)

if __name__ == '__main__':
    app.run(debug=True)
'''
@app.route('/')
def index():
    scrape_deals()
    # Read the contents of the JSON file
    search_strings = get_search_strings()
    scraped_data = read_json_file('scraped_data.json')
    filtered_data = filter_data(search_strings, scraped_data)

    return render_template('index.html', data=scraped_data) #filtered_data

if __name__ == '__main__':
    app.run(debug=True)