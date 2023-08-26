import json
import os
from flask import Blueprint, jsonify, request, Response, jsonify
import uuid
import boto3
from .common_utils import *

api_major = Blueprint('majors', __name__, url_prefix='/api/v1/majors') 

@api_major.route('/health', methods=['GET']) 
def health():
    return jsonify({"status": "ok"})

@api_major.route('/<major>', methods=['GET']) 
def get_major_route(major):
    item = get_major(major)
    return jsonify(item), 200