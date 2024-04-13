from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/leetcode')
def get_leetcode_questions():
    url = 'https://leetcode.com/api/problems/algorithms/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        return jsonify(data['stat_status_pairs'])
    else:
        return jsonify({'error': 'Failed to fetch LeetCode questions'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
