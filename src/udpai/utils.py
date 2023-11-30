#!/usr/bin/env python3

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-ip", type=str, required=True)
    parser.add_argument("--local-port", type=int, required=True)
    parser.add_argument("--remote-ip", type=str, required=True)
    parser.add_argument("--remote-port", type=int, required=True)
    parser.add_argument("--file", type=str, required=True)
    return parser.parse_args()

def print_args(args):
    print("=" * 10 + " Arguments " + "=" * 10)
    print("local_ip:", args.local_ip)
    print("local_port:", args.local_port)
    print("remote_ip:", args.remote_ip)
    print("remote_port:", args.remote_port)
    print("file:", args.file)
    print("=" * 10 + " Arguments " + "=" * 10)