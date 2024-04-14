from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from bson.json_util import dumps
from dotenv import load_dotenv
import requests,os

load_dotenv

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["leetcode-api"]
problems_collection = db["problems"]

@app.route('/leetcode')
def get_leetcode_questions():
    ALGORITHMS_LINK = 'https://leetcode.com/api/problems/algorithms/'
    PROBLEMS_URL = "https://leetcode.com/problems/"
    driver = webdriver.Chrome()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(ALGORITHMS_LINK, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        problems = [
            {
                "title_slug": child["stat"]["question__title_slug"],
                "difficulty": child["difficulty"]["level"],
                "question_id": child["stat"]["frontend_question_id"],
                "title": child["stat"]["question__title"]
            }
            for child in data["stat_status_pairs"] if not child["paid_only"]
        ]
        for problem in problems:
            existing_problem = problems_collection.find_one({"title_slug": problem["title_slug"]})
            if existing_problem:
                continue  

            url = PROBLEMS_URL + problem["title_slug"]
            driver.get(url)
            driver.implicitly_wait(60)

            html_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
            problem["description"] = problem_description.text
            
            problems_collection.insert_one(problem)

        driver.quit()
        return jsonify({"message": "Problems fetched and stored successfully"})
    else:
        driver.quit()
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
