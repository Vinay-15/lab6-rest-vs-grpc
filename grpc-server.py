#!/usr/bin/env python3
"""Lab 6 gRPC server (port 50051)."""
import argparse
import base64
import io
from concurrent import futures

import grpc
from PIL import Image

import lab6_pb2
import lab6_pb2_grpc


def dimensions(raw):
    with Image.open(io.BytesIO(raw)) as image:
        width, height = image.size
    return lab6_pb2.ImageReply(width=width, height=height)


class Lab6Service(lab6_pb2_grpc.Lab6Servicer):
    def Add(self, request, context):
        return lab6_pb2.AddReply(sum=request.a + request.b)

    def RawImage(self, request, context):
        return dimensions(request.img)

    def DotProduct(self, request, context):
        if len(request.a) != len(request.b):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'Vector lengths differ')
        value = sum(x * y for x, y in zip(request.a, request.b))
        return lab6_pb2.DotProductReply(dotproduct=value)

    def JsonImage(self, request, context):
        try:
            return dimensions(base64.b64decode(request.img, validate=True))
        except Exception as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=50051)
    args = parser.parse_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    lab6_pb2_grpc.add_Lab6Servicer_to_server(Lab6Service(), server)
    server.add_insecure_port(f'0.0.0.0:{args.port}')
    server.start()
    print(f'gRPC server running on port {args.port}', flush=True)
    server.wait_for_termination()


if __name__ == '__main__':
    main()
