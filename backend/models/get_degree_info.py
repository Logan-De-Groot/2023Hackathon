import csv
import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import boto3
import dotenv
import time
service = Service()
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=service, options=chrome_options)


encounted_coures = set()
new_course = []
MAIN_URL = 'https://my.uq.edu.au/programs-courses/requirements/plan/'
MAJOR_URL = ''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

session = boto3.session.Session(region_name='ap-southeast-2', aws_secret_access_key=dotenv.get_key('.env', 'AWS_SECRET_ACCESS_KEY'), aws_access_key_id=dotenv.get_key('.env', 'AWS_ACCESS_KEY_ID'))
dynamodb = session.resource('dynamodb')
degree_table = dynamodb.Table('degree')
major_table = dynamodb.Table('major')
course_table = dynamodb.Table('courses')
def get_core_degree_info(degree):
    global new_course
    try:
        degree_url = MAIN_URL + degree
        driver.get(degree_url)
        driver.implicitly_wait(1)
        

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        category_types = ["A","B","C","D"]
        data = {}    

        for index, part_div in enumerate(soup.find_all('div', class_='program-rules__parts')):
            if index == 4:
                break
            
            part_content = part_div.find('div', class_='part__content')


            # data[section.get('id')] = {
            #     "rule": rule_content.text if rule_content else None,
            # }
            if part_content:
                courses = []
                for a_tag in part_content.find_all('a', class_='curriculum-reference'):
                    href = a_tag['href']
                    course_code = a_tag.find('span', class_='curriculum-reference__code').text
                    units = a_tag.find('span', class_='curriculum-reference__units').text
                    title = a_tag.find('h5', class_='curriculum-reference__name').text
                    course_data = {
                        "course_code": course_code,
                        "units": units,
                        "title": title,
                        "href": href
                    }
                    print(course_code)
                    courses.append(course_data)
                    # if course_code not in encountered_courses:
                    #     new_course.append({"course": course_code, "href": href})
                    # encountered_courses.add(course_code)

                data[category_types[index]]["courses"] = courses


        return data
    except Exception as e:
        print(e)
        return None

def get_major_degree_info(major):
    global new_course

    major_url = "https://my.uq.edu.au/programs-courses/requirements/plan/" + major
    print(major_url)
    driver.get(major_url)
    driver.implicitly_wait(5)
    

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)
    script_content = None
    for script in soup.find_all("script", type="text/javascript"):
        if "window.AppData" in script.string:
            script_content = script.string
            break

    category_types = ["A","B","C","D"]
    data = {}    
    # category_types = ["Introductory Elective Courses", "Compulsory Courses"]
    
    for index, part_div in enumerate(soup.find_all('div', class_='program-rules__parts')):
        if index == 4:
            break
        data[category_types[index]] = {}

        
        part_content = part_div.find('div', class_='part__content')

        if part_content:
            courses = []
            for a_tag in part_content.find_all('a', class_='curriculum-reference'):
                href = a_tag['href']
                course_code = a_tag.find('span', class_='curriculum-reference__code').text
                units = a_tag.find('span', class_='curriculum-reference__units').text
                title = a_tag.find('h5', class_='curriculum-reference__name').text
                course_data = {
                    "course_code": course_code,
                    "units": units,
                    "title": title,
                    "href": href
                }
                print(course_code)
                courses.append(course_data)
                # if course_code not in encountered_courses:
                #     new_course.append({"course": course_code, "href": href})
                # encountered_courses.add(course_code)
            print("ADDING", courses)
            data[category_types[index]]["courses"] = courses

    # Now you can access the data like a regular dictionary
    program_requirements = 0

    return data


def main_loop():
    global new_course
    with open('table_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        lines = list(reader)
    seen_degrees = set()
    degree_major = {}
    flag = True
    count =0

    lines = [
        ["Computer Science","","Cyber Security","/programs-courses/plan.html?acad_plan=CYBERC2451","Bachelor"],
        ["Computer Science","","Data Science","/programs-courses/plan.html?acad_plan=DATASC2451","Bachelor"],
        ["Computer Science","","Data Science","/programs-courses/plan.html?acad_plan=DATASD2451","Bachelor"],
        ["Computer Science","","Machine Learning","/programs-courses/plan.html?acad_plan=MACHDC2451","Bachelor"],
        ["Computer Science","","Programming Languages","/programs-courses/plan.html?acad_plan=PROLAC2451","Bachelor"],
        ["Computer Science","","Scientific Computing","/programs-courses/plan.html?acad_plan=SCCOMC2451","Bachelor"],
        ["Computer Science (Honours)","","Computer Science (Honours)","/programs-courses/program.html?acad_prog=2452","Bachelor Honours"]
    ]
    for line in lines[1:]:
        original_line = line
        # try:
        count += 1
        print(count)

        line = line[3]
        line = line.split(",")[-1]

        major = line.split("=")[-1]
    
        core_degree = major[-4:]
        print(original_line[0])
            

        # if core_degree not in degree_major:
        #     degree_info = {}
        #     data = get_core_degree_info(core_degree)
        #     degree_info["degree_components"] = data
        #     degree_info["degree"] = core_degree
            
            
        #     if data is None:
        #         continue
        #     degree = original_line[0]
        #     major = original_line[2]
        #     url = original_line [3]
        #     degree_type = original_line[4]

            
        #     print("Attempting to put degree into table ", core_degree)
        #     degree_info["degree_title"] = degree
        #     degree_info["url"] = url
        #     degree_info["degree_type"] = degree_type
        #     degree_table.put_item(Item=degree_info)
            

        # flag = False
        major = original_line[3]
        if len(major) > 4:
            print(major)
            print(major.split("=")[-1])
            data_major = get_major_degree_info(major.split("=")[-1])
            print(json.dumps(data_major,indent=4))
            print(major)

            data_major["major"] = major
            data_major["degree"] = core_degree
            print(data_major)
            print(json.dumps(data_major,indent=4))
            
            # if data_major is not None:
            #     print("Attempting to put major into table ", major)
            #     major_table.put_item(Item=data_major)

        
        with course_table.batch_writer() as batch:
            for course in new_course:
                batch.put_item(Item=course)
        new_course = []
 


        # except Exception as e:
        #     print(e)
        #     pass

    
main_loop()