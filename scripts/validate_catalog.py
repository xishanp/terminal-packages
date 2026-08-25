#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def fail(message: str) -> None:
    raise SystemExit(f"catalog-v1.json: {message}")


root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / "catalog-v1.json").read_text(encoding="utf-8"))

if catalog.get("schemaVersion") != 1:
    fail("schemaVersion must be 1")
if catalog.get("id") != "terminal" or catalog.get("name") != "Terminal Official":
    fail("official source identity changed")

source_ids = set()
for source in catalog.get("androidSources", []):
    source_id = source.get("id")
    if not source_id or source_id in source_ids:
        fail(f"invalid or duplicate source id: {source_id!r}")
    source_ids.add(source_id)
    if source.get("kind") == "fdroid-index-v1":
        fingerprint = source.get("certificateSha256", "")
        if not re.fullmatch(r"[0-9A-F]{64}", fingerprint):
            fail(f"{source_id} has no pinned SHA-256 certificate")
        for value in source.get("indexUrls", []):
            if urlparse(value).scheme != "https":
                fail(f"{source_id} contains a non-HTTPS URL")

tool_ids = set()
for tool in catalog.get("tools", []):
    tool_id = tool.get("id")
    if not tool_id or tool_id in tool_ids:
        fail(f"invalid or duplicate tool id: {tool_id!r}")
    tool_ids.add(tool_id)
    state = tool.get("state")
    if state not in {"building", "available"}:
        fail(f"{tool_id} has invalid state: {state!r}")
    if tool.get("artifactFormat") != "terminal-split-apk":
        fail(f"{tool_id} is not declared as a Terminal module APK")
    if not tool.get("category") or not tool.get("abis"):
        fail(f"{tool_id} is missing category or ABI metadata")
    if state == "available":
        for key in ("version", "artifacts"):
            if not tool.get(key):
                fail(f"available tool {tool_id} is missing {key}")
        for artifact in tool["artifacts"]:
            if not artifact.get("name", "").endswith(".apk"):
                fail(f"{tool_id} contains a non-APK artifact")

app_ids = set()
for app in catalog.get("androidDevelopmentApps", []):
    package_id = app.get("packageId")
    if not package_id or package_id in app_ids:
        fail(f"invalid or duplicate development app id: {package_id!r}")
    app_ids.add(package_id)
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+", package_id):
        fail(f"invalid Android package id: {package_id}")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", app.get("repository", "")):
        fail(f"{package_id} has an invalid GitHub repository")

print(f"OK: {len(source_ids)} Android sources, {len(app_ids)} development apps, {len(tool_ids)} native tools")
