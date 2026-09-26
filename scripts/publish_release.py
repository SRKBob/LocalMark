#!/usr/bin/env python
"""Publish a GitHub Release with build artifacts.

Usage:
    python scripts/publish_release.py --tag v1.0.0 --notes-file RELEASE_NOTES.md \
        --assets release-v1.0.0/LocalMark-Portable-1.0.0.exe \
                 release-v1.0.0/LocalMark-Setup-1.0.0.exe

The GitHub token is resolved from the local git credential helper
(`git credential fill`), so no secret is ever stored in this repository.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
import urllib.error
import urllib.request

OWNER = "SRKBob"
REPO = "LocalMark"
API = "https://api.github.com"
UPLOAD_API = "https://uploads.github.com"


def resolve_token() -> str:
    """Read the stored github.com credential via git's credential helper."""
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("No github.com credential found in git credential store.")


def api_request(method: str, url: str, token: str, payload: dict | None = None,
                data: bytes | None = None, content_type: str | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "localmark-release-script",
    }
    body = data
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if content_type:
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"GitHub API {exc.code} on {method} {url}\n{detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--name", default=None)
    parser.add_argument("--notes-file", default=None)
    parser.add_argument("--assets", nargs="*", default=[])
    parser.add_argument("--prerelease", action="store_true")
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()

    token = resolve_token()

    notes = ""
    if args.notes_file:
        with open(args.notes_file, encoding="utf-8") as fh:
            notes = fh.read()

    # Reuse an existing release for the tag, otherwise create one.
    release = None
    try:
        release = api_request("GET", f"{API}/repos/{OWNER}/{REPO}/releases/tags/{args.tag}", token)
        print(f"Found existing release id={release['id']}")
    except SystemExit:
        pass

    if release is None:
        release = api_request("POST", f"{API}/repos/{OWNER}/{REPO}/releases", token, payload={
            "tag_name": args.tag,
            "name": args.name or args.tag,
            "body": notes,
            "draft": args.draft,
            "prerelease": args.prerelease,
        })
        print(f"Created release id={release['id']} tag={args.tag}")

    existing = {a["name"]: a["id"] for a in release.get("assets", [])}

    for path in args.assets:
        name = path.replace("\\", "/").split("/")[-1]
        if name in existing:
            api_request("DELETE",
                        f"{API}/repos/{OWNER}/{REPO}/releases/assets/{existing[name]}", token)
            print(f"  removed previous asset {name}")

        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        with open(path, "rb") as fh:
            blob = fh.read()
        asset = api_request(
            "POST",
            f"{UPLOAD_API}/repos/{OWNER}/{REPO}/releases/{release['id']}/assets?name={name}",
            token, data=blob, content_type=ctype,
        )
        print(f"  uploaded {name} ({asset.get('size', 0) / 1048576:.1f} MB)")

    print(f"\nRelease URL: {release['html_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
