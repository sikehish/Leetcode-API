from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests

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
        # for link in links:
        link=links[0]
        response=requests.get(PROBLEMS_URL + link["title_slug"], headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        file = open("output.html", "w")
        file.write(response.text)
        file.close()

        # box = soup.find('div', class_='elfjS')
        # if box:
        #     link["problem"] = box.get_text()
        # else:
        #     link["problem"] = "Problem description not found"

        return jsonify(links)
    else:
        return jsonify({'error': 'Failed to fetch LeetCode questions'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
