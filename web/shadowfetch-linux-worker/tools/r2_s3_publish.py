#!/usr/bin/env python3
"""Publish a large R2 object using an existing scoped Cloudflare API token."""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import urllib.request
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig


class Progress:
    def __init__(self, total: int) -> None:
        self.total = total
        self.seen = 0
        self.next_percent = 10
        self.lock = threading.Lock()

    def __call__(self, amount: int) -> None:
        with self.lock:
            self.seen += amount
            percent = int(self.seen * 100 / self.total)
            if percent >= self.next_percent:
                print(f"Upload progress: {percent}%", flush=True)
                self.next_percent = ((percent // 10) + 1) * 10


def token_id(value: str) -> str:
    request = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/user/tokens/verify",
        headers={"Authorization": f"Bearer {value}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if not body.get("success") or body.get("result", {}).get("status") != "active":
        raise RuntimeError("Cloudflare API token is not active")
    return body["result"]["id"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("key")
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--part-mib", type=int, default=64)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--abort-existing", action="store_true")
    args = parser.parse_args()

    path = args.file.resolve()
    if not path.is_file():
        raise SystemExit(f"Not a file: {path}")

    value = args.token_file.read_text(encoding="utf-8").strip()
    access_key = token_id(value)
    secret_key = hashlib.sha256(value.encode("utf-8")).hexdigest()
    client = boto3.client(
        "s3",
        endpoint_url=args.endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )

    if args.abort_existing:
        marker = None
        aborted = 0
        while True:
            params = {"Bucket": args.bucket, "Prefix": args.key}
            if marker:
                params["KeyMarker"] = marker
            result = client.list_multipart_uploads(**params)
            for upload in result.get("Uploads", []):
                if upload["Key"] == args.key:
                    client.abort_multipart_upload(
                        Bucket=args.bucket,
                        Key=args.key,
                        UploadId=upload["UploadId"],
                    )
                    aborted += 1
            if not result.get("IsTruncated"):
                break
            marker = result.get("NextKeyMarker")
        print(f"Aborted {aborted} incomplete upload(s)", flush=True)

    part_size = args.part_mib * 1024 * 1024
    config = TransferConfig(
        multipart_threshold=part_size,
        multipart_chunksize=part_size,
        max_concurrency=args.workers,
        use_threads=True,
    )
    client.upload_file(
        str(path),
        args.bucket,
        args.key,
        ExtraArgs={
            "ContentType": "application/x-iso9660-image",
            "ContentDisposition": f'attachment; filename="{path.name}"',
            "CacheControl": "public, max-age=3600",
            "Metadata": {"release": "1.9.0"},
        },
        Config=config,
        Callback=Progress(path.stat().st_size),
    )
    head = client.head_object(Bucket=args.bucket, Key=args.key)
    if head["ContentLength"] != path.stat().st_size:
        raise RuntimeError("Published object size does not match the source")
    print(json.dumps({"key": args.key, "size": head["ContentLength"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
