#!/usr/bin/env python3
"""Remove obsolete distro releases and APT packages not referenced by Packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

import boto3


def binary_pool_keys(packages: str) -> set[str]:
    return {
        "apt/" + line.split(":", 1)[1].strip()
        for line in packages.splitlines()
        if line.startswith("Filename:")
    }


def source_pool_keys(sources: str) -> set[str]:
    """Return source artifacts referenced by a Debian Sources index."""
    active: set[str] = set()
    for paragraph in sources.split("\n\n"):
        fields: dict[str, list[str]] = {}
        current_field: str | None = None
        for line in paragraph.splitlines():
            if line.startswith((" ", "\t")) and current_field:
                fields[current_field].append(line.strip())
                continue
            if ":" not in line:
                current_field = None
                continue
            name, value = line.split(":", 1)
            current_field = name
            fields[current_field] = [value.strip()] if value.strip() else []

        directory_values = fields.get("Directory", [])
        if not directory_values:
            continue
        directory = directory_values[0].rstrip("/")
        checksum_lines = fields.get("Files") or fields.get("Checksums-Sha256", [])
        for checksum_line in checksum_lines:
            parts = checksum_line.split()
            if len(parts) >= 3:
                active.add(f"apt/{directory}/{parts[-1]}")
    return active


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


def list_prefix(client, bucket: str, prefix: str) -> list[dict]:
    paginator = client.get_paginator("list_objects_v2")
    objects: list[dict] = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        objects.extend(page.get("Contents", []))
    return objects


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    value = args.token_file.read_text(encoding="utf-8").strip()
    client = boto3.client(
        "s3",
        endpoint_url=args.endpoint,
        aws_access_key_id=token_id(value),
        aws_secret_access_key=hashlib.sha256(value.encode("utf-8")).hexdigest(),
        region_name="auto",
    )

    packages = client.get_object(
        Bucket=args.bucket,
        Key="apt/dists/umbra/main/binary-amd64/Packages",
    )["Body"].read().decode("utf-8")
    sources = client.get_object(
        Bucket=args.bucket,
        Key="apt/dists/umbra/main/source/Sources",
    )["Body"].read().decode("utf-8")
    active_binary = binary_pool_keys(packages)
    active_sources = source_pool_keys(sources)
    active_pool = active_binary | active_sources
    if not active_binary:
        raise RuntimeError("Active Packages index contains no filenames; refusing to prune")
    if not active_sources:
        raise RuntimeError("Active Sources index contains no filenames; refusing to prune")

    release_prefix = f"releases/shadowfetch-{args.version}-amd64.iso"
    obsolete = [
        item
        for item in list_prefix(client, args.bucket, "releases/")
        if not item["Key"].startswith(release_prefix)
    ]
    obsolete.extend(
        item
        for item in list_prefix(client, args.bucket, "apt/pool/")
        if item["Key"] not in active_pool
    )
    obsolete.sort(key=lambda item: item["Key"])
    bytes_to_remove = sum(item["Size"] for item in obsolete)
    print(
        json.dumps(
            {
                "apply": args.apply,
                "active_packages": len(active_pool),
                "active_binary_packages": len(active_binary),
                "active_source_files": len(active_sources),
                "objects_to_remove": len(obsolete),
                "bytes_to_remove": bytes_to_remove,
            }
        )
    )
    for item in obsolete:
        print(f"{'DELETE' if args.apply else 'WOULD_DELETE'} {item['Key']}")

    if args.apply:
        for offset in range(0, len(obsolete), 1000):
            batch = obsolete[offset : offset + 1000]
            if batch:
                client.delete_objects(
                    Bucket=args.bucket,
                    Delete={"Objects": [{"Key": item["Key"]} for item in batch]},
                )
        print("Prune complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
