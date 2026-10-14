#!/usr/bin/env python3
"""gRPC benchmark: python grpc-client.py HOST METHOD REPS"""
import argparse
import base64
import random
import time
from pathlib import Path

import grpc
import lab6_pb2
import lab6_pb2_grpc

METHODS = ('add', 'rawImage', 'dotProduct', 'jsonImage')
IMAGE_PATH = Path(__file__).with_name('Flatirons_Winter_Sunrise_edit_2.jpg')


def main():
    parser = argparse.ArgumentParser(description='Lab 6 gRPC client')
    parser.add_argument('host', help='localhost or server INTERNAL IP')
    parser.add_argument('cmd', choices=METHODS)
    parser.add_argument('reps', type=int)
    parser.add_argument('-p', '--port', type=int, default=50051)
    args = parser.parse_args()
    if args.reps < 1:
        parser.error('reps must be >= 1')

    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]
    expected_dot = sum(x * y for x, y in zip(a, b))
    image = IMAGE_PATH.read_bytes() if args.cmd in ('rawImage', 'jsonImage') else None
    encoded = base64.b64encode(image).decode('ascii') if image is not None else None
    with grpc.insecure_channel(f'{args.host}:{args.port}') as channel:
        grpc.channel_ready_future(channel).result(timeout=30)
        stub = lab6_pb2_grpc.Lab6Stub(channel)
        if args.cmd == 'add':
            request = lab6_pb2.AddRequest(a=5, b=10)
            rpc = stub.Add
        elif args.cmd == 'rawImage':
            request = lab6_pb2.RawImageRequest(img=image)
            rpc = stub.RawImage
        elif args.cmd == 'dotProduct':
            request = lab6_pb2.DotProductRequest(a=a, b=b)
            rpc = stub.DotProduct
        else:
            request = lab6_pb2.JsonImageRequest(img=encoded)
            rpc = stub.JsonImage

        warmup = rpc(request, timeout=30)
        if args.cmd == 'add':
            assert warmup.sum == 15
        elif args.cmd == 'dotProduct':
            assert abs(warmup.dotproduct - expected_dot) < 0.001
        else:
            assert warmup.width > 0 and warmup.height > 0

        # Reuse one HTTP/2 channel for all calls.
        start = time.perf_counter()
        for _ in range(args.reps):
            rpc(request, timeout=30)
        avg_ms = (time.perf_counter() - start) * 1000 / args.reps

    print(f'gRPC {args.cmd}: {avg_ms:.3f} ms/op ({args.reps} requests, server={args.host})')


if __name__ == '__main__':
    main()
