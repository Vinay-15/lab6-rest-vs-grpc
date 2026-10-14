#!/usr/bin/env python3
"""REST benchmark: python rest-client.py HOST METHOD REPS"""
import argparse
import base64
import random
import time
from pathlib import Path

import requests

METHODS = ('add', 'rawImage', 'dotProduct', 'jsonImage')
IMAGE_PATH = Path(__file__).with_name('Flatirons_Winter_Sunrise_edit_2.jpg')


def main():
    parser = argparse.ArgumentParser(description='Lab 6 REST client')
    parser.add_argument('host', help='localhost or server INTERNAL IP')
    parser.add_argument('cmd', choices=METHODS)
    parser.add_argument('reps', type=int)
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    if args.reps < 1:
        parser.error('reps must be >= 1')

    base_url = f'http://{args.host}:{args.port}'
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]
    expected_dot = sum(x * y for x, y in zip(a, b))
    image = IMAGE_PATH.read_bytes() if args.cmd in ('rawImage', 'jsonImage') else None
    encoded = base64.b64encode(image).decode('ascii') if image is not None else None

    def call():
        # Each requests.post call uses a new connection (no persistent Session).
        if args.cmd == 'add':
            response = requests.post(f'{base_url}/api/add/5/10', timeout=30)
        elif args.cmd == 'rawImage':
            response = requests.post(f'{base_url}/api/rawimage', data=image,
                                     headers={'Content-Type': 'image/jpeg'}, timeout=30)
        elif args.cmd == 'dotProduct':
            response = requests.post(f'{base_url}/api/dotproduct',
                                     json={'a': a, 'b': b}, timeout=30)
        else:
            response = requests.post(f'{base_url}/api/jsonimage',
                                     json={'image': encoded}, timeout=30)
        response.raise_for_status()
        return response.json()

    warmup = call()
    if args.cmd == 'add':
        assert int(warmup['sum']) == 15
    elif args.cmd == 'dotProduct':
        assert abs(warmup['dotproduct'] - expected_dot) < 0.001
    else:
        assert warmup['width'] > 0 and warmup['height'] > 0

    start = time.perf_counter()
    for _ in range(args.reps):
        call()
    avg_ms = (time.perf_counter() - start) * 1000 / args.reps
    print(f'REST {args.cmd}: {avg_ms:.3f} ms/op ({args.reps} requests, server={args.host})')


if __name__ == '__main__':
    main()
