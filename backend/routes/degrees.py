import json
import os
from flask import Blueprint, jsonify, request, Response, jsonify
import uuid
import boto3
from .common_utils import *
api_degrees = Blueprint('degrees', __name__, url_prefix='/api/v1/degree') 

@api_degrees.route('/health', methods=['GET']) 
def health():
    return jsonify({"status": "ok"})

@api_degrees.route('', methods=['GET']) 
def get_all_degrees():
    response = degree_table.scan()
    conversion_list = []
    for item in response['Items']:
        if item.get("degree") is None or item.get("degree_title") is None:
            continue
        conversion_list.append({
            "value": item["degree"],
            "label": item["degree_title"]
        })
       
    return jsonify(conversion_list), 200

@api_degrees.route('/<degree>', methods=['GET']) 
def get_degree(degree):
    print(degree)
    response = degree_table.get_item(
        Key={
            'degree': degree
        }
    )
    item = response['Item']
    return jsonify(item), 200