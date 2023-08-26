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


        for index, section in enumerate(soup.find_all('div', class_='program-rules__part')):
            
            # Extract the h4 content within the current section
            
            # Extract the part__rule part__rule--selection content within the current section
            rule_content = section.find('p', class_='part__rule part__rule--selection')

            data[section.get('id')] = {
                "rule": rule_content.text if rule_content else None,
            }
            courses = []
            # Loop through each reference link within the current section
            for ref_link in section.find_all('a', class_='selection-list__row curriculum-reference'):
                try:
                    course_code = ref_link.find('span', class_='curriculum-reference__code').text
                    units = ref_link.find('span', class_='curriculum-reference__units').text
                    href = ref_link['href']
                except Exception:
                    course_code = "Elective"
                    units = "N/A"
                    href = "N/A"



                course_data = {
                            "course_code": course_code,
                            "units": units,
                            "href": href
                }
                courses.append(course_data)
                if course_code not in encounted_coures:
                    new_course.append({"course":course_code,
                                            "href": href})
                encounted_coures.add(course_code)
            data[section.get('id')]["courses"] = courses

        return data
    except Exception as e:
        print(e)
        return None

def get_major_degree_info(major):
    global new_course
    try:
        major_url = MAIN_URL + major
        driver.get(major_url)
        driver.implicitly_wait(5)
        

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        script_content = None
        for script in soup.find_all("script", type="text/javascript"):
            if "window.AppData" in script.string:
                script_content = script.string
                break

        category_types = ["A","B","C","D"]
        data = {}    

        for index, part_div in enumerate(soup.find_all('div', class_='program-rules__part part selection-list')):
            if index == 4:
                break
            
            h3_primary_content = part_div.find('h3', class_='part__title')

            rule_content = part_div.find('p', class_='part__rule part__rule--selection')


            part_content = part_div.find('div', class_='part__content')

            data[category_types[index]] = {
                        "primary_title": h3_primary_content.text,
                        "rule": rule_content.text,
                    }
            
            # If part_content exists, iterate over its children
            if part_content:
                courses = []
                for child in part_content.children:
                    if child.name == 'h3':  # For secondary h3
                        print(f"Secondary Title: {child.text}\n")
                    elif child.name == 'a' and child.has_attr('class') and 'curriculum-reference' in child['class']:
                        href = child['href']
                        course_code = child.find('span', class_='curriculum-reference__code').text
                        units = child.find('span', class_='curriculum-reference__units').text
                        course_data = {
                            "course_code": course_code,
                            "units": units,
                            "href": href
                        }
                        courses.append(course_data)
                        if course_code not in encounted_coures:
                            new_course.append({"course":course_code,
                                            "href": href})
                        encounted_coures.add(course_code)
    
                data[category_types[index]]["courses"] = courses

        # Now you can access the data like a regular dictionary
        program_requirements = 0

        return data
    except Exception as e:
        print(e)
        return None

def main_loop():
    global new_course
    with open('table_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        lines = list(reader)
    seen_degrees = set()
    degree_major = {}
    flag = True
    count =0
    for line in lines[1:]:
        original_line = line
        try:
            count += 1
            print(count)

            line = line[3]
            line = line.split(",")[-1]

            major = line.split("=")[-1]
       
            core_degree = major[-4:]
            print(original_line[0])
            if core_degree in seen_degrees:
                
                continue

            if original_line[4] == "Bachelor (Dual Degree)" or original_line[4] == "Diploma" :
                print("skipping dual degree/diploma", core_degree)
                continue

            response = degree_table.get_item(Key={'degree': core_degree})
            if response.get('Item') and response['Item'].get('degree_components'):
                seen_degrees.add(core_degree)
                print("Degree already in table ", core_degree)
                time.sleep(0.2)
                continue
                
  
            if core_degree not in degree_major:
                degree_info = {}
                data = get_core_degree_info(core_degree)
                degree_info["degree_components"] = data
                degree_info["degree"] = core_degree
                
                
                if data is None:
                    continue
                degree = original_line[0]
                major = original_line[2]
                url = original_line [3]
                degree_type = original_line[4]

               
                print("Attempting to put degree into table ", core_degree)
                degree_info["degree_title"] = degree
                degree_info["url"] = url
                degree_info["degree_type"] = degree_type
                degree_table.put_item(Item=degree_info)
                

            # flag = False
            if len(major) > 4:
                data_major = get_major_degree_info(major)
                data_major["major"] = major
                data_major["degree"] = core_degree
                if data_major is not None:
                    print("Attempting to put major into table ", major)
                    major_table.put_item(Item=data_major)
   
            
            with course_table.batch_writer() as batch:
                for course in new_course:
                    batch.put_item(Item=course)
            new_course = []
 


        except Exception as e:
            print(e)
            pass

    
main_loop()