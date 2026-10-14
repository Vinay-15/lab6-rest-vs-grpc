#!/usr/bin/env python3
"""REST endpoints required by CSCI 5253 Lab 6."""
import argparse
import base64
import io
import logging

from flask import Flask, jsonify, request
from PIL import Image

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)


def image_size(data):
    with Image.open(io.BytesIO(data)) as image:
        width, height = image.size
    return {'width': width, 'height': height}


@app.route('/api/add/<int:a>/<int:b>', methods=['GET', 'POST'])
def add(a, b):
    return jsonify({'sum': str(a + b)})


@app.route('/api/rawimage', methods=['POST'])
def rawimage():
    try:
        return jsonify(image_size(request.data))
    except Exception:
        return jsonify({'width': 0, 'height': 0}), 400


@app.route('/api/dotproduct', methods=['POST'])
def dotproduct():
    payload = request.get_json(silent=True) or {}
    a = payload.get('a')
    b = payload.get('b')
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return jsonify({'error': 'a and b must be lists of equal length'}), 400
    try:
        value = sum(float(x) * float(y) for x, y in zip(a, b))
    except (TypeError, ValueError):
        return jsonify({'error': 'Vectors must contain numbers'}), 400
    return jsonify({'dotproduct': value})


@app.route('/api/jsonimage', methods=['POST'])
def jsonimage():
    payload = request.get_json(silent=True) or {}
    try:
        encoded = payload['image']
        data = base64.b64decode(encoded, validate=True)
        return jsonify(image_size(data))
    except Exception:
        return jsonify({'width': 0, 'height': 0}), 400


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lab 6 REST server')
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=False)
