from flask import Flask, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
import requests,os,json
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/leetcode')
def get_leetcode_questions():

    ALGORITHMS_LINK = 'https://leetcode.com/api/problems/algorithms/'
    PROBLEMS_URL = "https://leetcode.com/problems/"
    driver=webdriver.Chrome()
    # driver.minimize_window()
    

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(ALGORITHMS_LINK, headers=headers)
    
    if response.status_code == 200:
        data = response.json() #OR json.loads(response.text)
        links = [
            {
                "title_slug": child["stat"]["question__title_slug"],
                "difficulty": child["difficulty"]["level"],
                "question_id": child["stat"]["frontend_question_id"],
                "title": child["stat"]["question__title"]
            }
            for child in data["stat_status_pairs"] if not child["paid_only"]
        ]
        for link in links:
            url=PROBLEMS_URL + link["title_slug"]
            print(url, " ", link["question_id"])
            driver.get(url)
            # waiting for the page to load completely 
            driver.implicitly_wait(60)

            html_content=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            # sleep(5)

            problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
            link["description"]=problem_description.text

        return jsonify(links)
    else:
        return jsonify({'error': 'Failed to fetch LeetCode questions'}), response.status_code
    
# For testing purposes
@app.route('/html')
def get_leetcode_html():
    driver = webdriver.Chrome() 
    driver.minimize_window()

    driver.get('https://leetcode.com/problems/harshad-number')

    # waiting for the page to load completely
    driver.implicitly_wait(10)

    html_content=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # sleep(5)

    problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
    return jsonify({"content":problem_description.text})


if __name__ == '__main__':
    app.run(debug=True)



if __name__ == '__main__':
    app.run(debug=True)
