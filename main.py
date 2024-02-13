from openai import OpenAI
import base64
import requests
from flask import request,jsonify
import json
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup

UPLOAD_FOLDER = 'Images'
def upload_images():
    if 'file' not in request.files:
        return jsonify({'error':'Image not uploaded'}),400
    file = request.files['file']
    if file.filename == "":
        return jsonify({'error':'no file selected'}),400
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    # return jsonify({'msg':'Image uploaded successfully'})
    return f'Images/{filename}'

def configure():
    load_dotenv()

def index():
    return "Hello, World!"
#first column output
def getDataFromGPT(image_name):
    # OpenAI API Key
    configure()
    api_key = os.getenv('api_key')

    # image_name = request.args.get('image', 'test1.jpeg')
    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Getting the base64 string
    base64_image = encode_image(image_name)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Identify the image and suggest ways for the user to recycle. Please give response in normal text fonts."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 1000 
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # ans = response.json()['choices'][0]['message']['content']
    ans = response.json()['choices'][0]['message']
    app_json = json.dumps(ans)
    return app_json
    # return response.json()

def getCategoryFromGPT(image_name):
    configure()
    # OpenAI API Key
    api_key = os.getenv('api_key')

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Path to your image
    # image_path = "test1.jpeg"
    # image_path = "pepsi.jpeg"


    # image_path = request.args.get('image', 'test1.jpeg')
    # Getting the base64 string
    base64_image = encode_image(image_name)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Identify the image and suggest from the given category in which category the product belongs to :\
            categories = [AUTOMOTIVE, BATTERIES, CONSTRUCTION, ELECTRONICS, GARDEN, GLASS, HAZARDOUS, HOUSEHOLD, METALS, PAINT, PAPER, PLASTIC]. one word answer should be from AUTOMOTIVE, BATTERIES, CONSTRUCTION, ELECTRONICS, GARDEN, GLASS, HAZARDOUS, HOUSEHOLD, METALS, PAINT, PAPER, PLASTIC"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

#second column output
def getLocations(image_name):
    category = getCategoryFromGPT(image_name)
    print(category)
    # URL to scrape
    url = 'https://search.earth911.com/?what='+ category+ '&where=27606'

    # Send a GET request to the URL
    response = requests.get(url)
    loc = []
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data (this is a generic example, you'll need to tailor it)
        # for example, to find all paragraph tags: soup.find_all('p')
        company_names = soup.find_all('h2')
        names = soup.find_all('div', attrs = {'class':'contact'})
        distances = soup.find_all('span', attrs = {'class':'distance'})
        company_name = []
        address= []
        distance = []
        # Process and print the extracted data
        counter = 0
        for item in company_names:
            name = item.text.replace("ï»¿", "")
            if counter >= 2:
                company_name.append(name)
            counter += 1

        for item in names:
            name = item.text.replace("ï»¿", "")
            address.append(name)

        for item in distances:
            distance.append(item.text)

        for i in range(len(company_name) - len(distance)):
            company_name.pop(0)
            address.pop(0)

        for i in range(len(company_name)):
            recycle_spot = {}
            recycle_spot['Company'] = company_name[i]
            recycle_spot['Distance'] = distance[i]
            recycle_spot['Address'] = address[i]
            loc.append(recycle_spot)
        return loc

    else:
        return "Failed to retrieve the webpage"

def run():
    image_path = upload_images()
    ans = getDataFromGPT(image_path)
    new_response = {'response1': ans}
    new_response['response2'] = getLocations(image_path)
    new_response = json.dumps(new_response)
    os.remove(image_path)
    return new_response

 

