from flask import Flask, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
import requests,os,json
from time import sleep
from selenium.webdriver.common.by import By

app = Flask(__name__)

@app.route('/leetcode')
def get_leetcode_questions():

    ALGORITHMS_LINK = 'https://leetcode.com/api/problems/algorithms/'
    PROBLEMS_URL = "https://leetcode.com/problems/"

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
        # # for link in links:
        # link=links[0]
        # url=PROBLEMS_URL + link["title_slug"]+"/description"
        # response=requests.get(url, headers=headers)
        # soup = BeautifulSoup(response.content)
        # file = open("output.html", "w")
        # file.write(response.text)
        # file.close()

        # box = soup.find('div', class_='elfjS')
        # if box:
        #     link["problem"] = box.get_text()
        # else:
        #     link["problem"] = "Problem description not found"

        return jsonify(links)
    else:
        return jsonify({'error': 'Failed to fetch LeetCode questions'}), response.status_code
    
@app.route('/html')
def get_leetcode_html():
    driver=webdriver.Chrome()
    driver.get('https://leetcode.com/problems/two-sum/')
    # Wait for the page to load completely (you might need to adjust the wait time)
    driver.implicitly_wait(30)

    html_content=driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    # sleep(5)

    problem_description = driver.find_element(By.CLASS_NAME, 'elfjS')
    print(problem_description.text)
    return jsonify({"content":problem_description.text})


if __name__ == '__main__':
    app.run(debug=True)
