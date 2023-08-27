import csv
import requests
from bs4 import BeautifulSoup
import os
# from selenium import webdriver
import json
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
import re
import boto3
import time
import dotenv
# service = Service()
# chrome_options = Options()
# chrome_options.add_argument("--headless") # Ensure GUI is off
# chrome_options.add_argument("--no-sandbox")

# driver = webdriver.Chrome(service=service, options=chrome_options)
MAIN_URL = 'https://my.uq.edu.au'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

session = boto3.session.Session(region_name='ap-southeast-2', aws_secret_access_key=dotenv.get_key('.env', 'AWS_SECRET_ACCESS_KEY'), aws_access_key_id=dotenv.get_key('.env', 'AWS_ACCESS_KEY_ID'))
dynamodb = session.resource('dynamodb')
degree_table = dynamodb.Table('degree')
major_table = dynamodb.Table('major')
course_table = dynamodb.Table('courses')

def get_course_prereq(course):

    course_url = MAIN_URL + course
    response = requests.get(course_url, headers=headers, verify=False)  # Setting verify to False skips SSL verification (Not recommended for production use!)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the h1 tag with id 'course-title'
    course_title_tag = soup.find('h1', {'id': 'course-title'})
    if course_title_tag is None:
        return [], ""
    course_title = course_title_tag.text
    print(course_title)
    
    # find the p tag with id 'course-prerequisite'
    course_prerequisite_tag = soup.find('p', {'id': 'course-prerequisite'})
    if course_prerequisite_tag is None:
        return [], course_title

    if hasattr(course_prerequisite_tag, "text") and course_prerequisite_tag.text:
        course_prerequisite = course_prerequisite_tag.text
    else:
        # find the next p tag
        next_p_tag = course_prerequisite_tag.find_next('p')
        course_prerequisite = next_p_tag.text
    if course_prerequisite is None:
        return [], course_title

    # find the next p tag
    next_p_tag = course_prerequisite_tag.find_next('p')
    if next_p_tag is None:
        return [], course_title
    print(next_p_tag.text)
    matches = re.findall(r'\b([a-zA-Z]{4}\d{4}|\d{4})\b', next_p_tag.text)

    course_prefix = ""
    for index, match in enumerate(matches):
        if len(match) == 8:
            course_prefix = match[:4]
        if len(match) == 4:
            matches[index] = course_prefix + match
    print(matches)
    time.sleep(0.3)
    return matches, course_title

# response_items = course_table.scan()['Items']

# for index, item in enumerate(response_items):
main_list = []
with open("all courses.csv", "r") as file:
    
    for item in csv.reader(file):
        main_list.append(item[0])


for index, item in enumerate(main_list):
    # course = item['course']
    course = item
    # course_url = item['href']
    course_url = ''
    if len(course) != 8:
        continue
    print(course)

    prereqs, title = get_course_prereq(f"/programs-courses/course.html?course_code={course}")
    item = {
        'course': course,
        'prereqs': prereqs,
        'href': course_url,
        'title': title
    }
    course_table.put_item(Item=item)


