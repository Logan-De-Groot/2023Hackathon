import json
import os
from flask import Blueprint, jsonify, request, Response, jsonify
import uuid
import boto3
from .common_utils import *

api_courses = Blueprint('courses', __name__, url_prefix='/api/v1/courses') 

@api_courses.route('/health', methods=['GET']) 
def health():
    return jsonify({"status": "ok"})

@api_courses.route('/<course>', methods=['GET']) 
def get_course_route(course):
    item = get_course(course)
    return jsonify(item), 200

COLOURS = {
    "A": {"background-color": "#ff0000", "color": "#ffffff"},
    "B": {"background-color": "#00ff00", "color": "#ffffff"},
    "C": {"background-color": "#0000ff", "color": "#ffffff"},
    "D": {"background-color": "#ffff00", "color": "#ffffff"},
}

@api_courses.route('/mapping/<major>', methods=['GET']) 
def form_course_mapping(major):
    final_nodes, edges = get_data_major(major)
    return jsonify([final_nodes, edges]), 200

@lru_cache
def get_data_major(major):
    degree = major[-4:]
    
    degree_items = get_degree(degree)

    major_item = get_major(major)

    if major == {}:
        return jsonify("Missing Major"), 404

    nodes = []
    edges = []
    course_prereq = {}
    course_part_mapping = {}

    if degree_items is not None:
        for course_part, course_list in degree_items["degree_components"].items():
            if "courses" not in course_list:
                continue

            #print(course_part,course_list)
            if course_part == "degree_title" or course_part == "degree":
                continue

            # form all nodes
            for course in course_list["courses"]:
                print(course)
                course_code = course["course_code"]
                course_item = get_course(course_code)
                course_prereq[course_code] = course_item.get("prereqs", [])
                course_part_mapping[course_code] = course_part

    if major_item is not None:
        for course_part, course_list in major_item.items():
            if course_part == "major" or course_part == "degree":
                continue

            # form all nodes
            for course in course_list["courses"]:
                course_code = course["course_code"]
                course_item = get_course(course_code)
                course_prereq[course_code] = course_item.get("prereqs", [])
                course_part_mapping[course_code] = course_part
                

    full_set_of_courses = {}
    print("FOund prereqs", course_prereq)
    for course in course_prereq.keys():
        if len(course) != 8:
            continue
        form_prereq_list(course_prereq.get(course), full_set_of_courses)

    print(full_set_of_courses)

    for course in course_prereq.keys():
        if len(course) != 8:
            continue

        if course not in full_set_of_courses:
            full_set_of_courses[course] = ([],course)

    for course, (prereqs, title) in full_set_of_courses.items():
        if (title is not None):
            nodes.append({
                    "id": course,
                    "data": {"label": title if title is not None else "Not Indexed"},
                    "position": {"x": 0, "y": 0},
                })
        if prereqs == []:
            continue

        for prereq in prereqs:
            edges.append({
                "id": f"{course}{prereq}",
                "target": course,
                "source": prereq,
                "type": "smoothstep",
                "animated": True,
            })

    final_nodes = []
    for index, item_node in enumerate(nodes):
        found = False
        for item_edge in edges:
            if item_node["id"] == item_edge["target"] or item_node["id"] == item_edge["source"]:
                found = True
        if found:
            final_nodes.append(item_node)
    return final_nodes, edges

def form_prereq_list(prereq, prereq_list):
    if prereq is None:
        return []
    print("Prereq is:", prereq)
    for item in prereq:
        print("Item is", item)
        new_course = get_course(item)
        print("FOund new course", new_course)
        if new_course is None:
            new_course = {
                "course": item,
                "prereqs": "unknown",
                "title": "unknown"
            }
            return 

        if new_course.get("prereqs") is None:
            
            prereq_list[(new_course["course"])] = ([], new_course.get("title"))
        else:
            print("added", new_course["course"])
            prereq_list[(new_course["course"])] = (new_course.get("prereqs"), new_course.get("title"))

        form_prereq_list(new_course.get("prereqs"), prereq_list)



