import json
import os
from flask import Blueprint, jsonify, request, Response, jsonify
import uuid
import boto3
from .common_utils import *
from functools import lru_cache
import csv

api_major = Blueprint('majors', __name__, url_prefix='/api/v1/majors') 

@api_major.route('/health', methods=['GET']) 
def health():
    return jsonify({"status": "ok"})

@api_major.route('/<major>', methods=['GET']) 
def get_major_route(major):
    item = get_major(major)
    return jsonify(item), 200

@api_major.route('/degree/<degree>', methods=['GET']) 
def get_major_from_degree_only(degree):
    mapping = get_mapping()[degree]
    return jsonify(mapping), 200



@lru_cache
def get_mapping():
    mapping = {}
    with open("degree_major_title_mapping.csv", "r") as file:
        reader = csv.reader(file)
        
        for row in reader:
            if row[-2] not in mapping:
                mapping[row[-2]] = []
            else:
                mapping[row[-2]].append({
                    "balue": row[-1],
                    "label": row[3]
                })
    return mapping