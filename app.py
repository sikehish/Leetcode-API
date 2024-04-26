from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from bson.json_util import dumps
from dotenv import load_dotenv
import requests,os
import traceback
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


load_dotenv

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["leetcode-api"]
problems_collection = db["problems"]

ALGORITHMS_LINK = 'https://leetcode.com/api/problems/algorithms/'
PROBLEMS_URL = "https://leetcode.com/problems/"

@app.route('/leetcode')
def get_leetcode_questions():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(ALGORITHMS_LINK, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            problems = [
                {
                    "title_slug": child["stat"]["question__title_slug"],
                    "difficulty": "Easy" if child["difficulty"]["level"] == 1 else 
                      "Medium" if child["difficulty"]["level"] == 2 else 
                      "Hard",
                    "question_id": child["stat"]["frontend_question_id"],
                    "title": child["stat"]["question__title"]
                }
                for child in data["stat_status_pairs"] if not child["paid_only"]
            ]

            driver = webdriver.Chrome()
            driver.maximize_window()
            
            for problem in problems:
                existing_problem = problems_collection.find_one({"title_slug": problem["title_slug"]})
                if existing_problem:
                    continue  

                url = PROBLEMS_URL + problem["title_slug"]

                driver.get(url)
                driver.implicitly_wait(60)

                html_content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                sleep(5)
                driver.find_elements(By.CLASS_NAME, 'text-gray-4')[0].click()
                topics_section = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'mt-2.flex.flex-wrap.gap-1.pl-7'))
                )

                topics_elements = topics_section.find_elements(By.TAG_NAME, 'a')
                topics_text = [topic.text for topic in topics_elements]

                problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
                problem["description"] = problem_description.text

                problem["topics"]=topics_text
                problems_collection.insert_one(problem)

            driver.quit()
            return jsonify({"message": "Problems fetched and stored successfully"})
        else:
            return jsonify({'error': 'Failed to fetch LeetCode questions', 'message': response.text}), response.status_code
    except Exception as e:
        traceback.print_exc()
        driver.quit()
        return jsonify({'error': 'An error occurred while processing the request','message':repr(e)}), 500
    
    
# For testing purposes
@app.route('/html')
def get_leetcode_html():
    driver = webdriver.Chrome() 
    # driver.minimize_window()

    driver.get('https://leetcode.com/problems/minimum-falling-path-sum-ii/')

    # waiting for the page to load completely
    driver.implicitly_wait(10)

    html_content=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # sleep(5)
    driver.find_elements(By.CLASS_NAME, 'text-gray-4')[0].click()
    problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
    topics_elements = driver.find_element(By.CLASS_NAME, 'mt-2.flex.flex-wrap.gap-1.pl-7').find_elements(By.TAG_NAME, 'a')
    
    topics_text = [topic.text for topic in topics_elements]

    return jsonify({"content": problem_description.text, "topics": topics_text})

@app.route('/get-random-question')
def get_random_question():
    try:
        random_cursor = problems_collection.aggregate([{ '$sample': { 'size': 1 } }])
        random_problem = list(random_cursor)[0]
        print(random_problem)

        problem_details = {
            "title_slug": random_problem["title_slug"],
            "difficulty": random_problem["difficulty"],
            "question_id": random_problem["question_id"],
            "title": random_problem["title"],
            "description": random_problem["description"],
            "topics": random_problem["topics"]
        }

        return jsonify({"problem": problem_details})
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching the random question', 'message': repr(e)}), 500


@app.route('/update-topics', methods=['PUT'])
def update_topics():
    try:
        # Find documents where the first element in the topics list is empty
        query = {"topics.0": ""}
        documents_to_update = list(problems_collection.find(query))
        print(len(documents_to_update))
        driver = webdriver.Chrome()
        driver.maximize_window()

        for document in documents_to_update:
            url = PROBLEMS_URL + document["title_slug"]

            driver.get(url)
            driver.implicitly_wait(10) 

            html_content=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            sleep(5)
            driver.find_elements(By.CLASS_NAME, 'text-gray-4')[0].click()
            

            topics_section = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'mt-2.flex.flex-wrap.gap-1.pl-7'))
            )

            # Fetch topics
            topics_elements = topics_section.find_elements(By.TAG_NAME, 'a')
            topics_text = [topic.text for topic in topics_elements]
            print(topics_text)

            # Update topics array for the document
            problems_collection.update_one({"_id": document["_id"]}, {"$set": {"topics": topics_text}})

        driver.quit()
        return jsonify({"message": "Topics updated successfully"})
    except Exception as e:
        traceback.print_exc()
        driver.quit()
        return jsonify({'error': 'An error occurred while updating topics', 'message': repr(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)

