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
        if not source.get("name"):
            fail(f"{source_id} has no display name")
        fingerprint = source.get("certificateSha256", "")
        if not re.fullmatch(r"[0-9A-F]{64}", fingerprint):
            fail(f"{source_id} has no pinned SHA-256 certificate")
        urls = source.get("indexUrls", [])
        if not urls:
            fail(f"{source_id} has no index URL")
        for value in urls:
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
    if tool.get("artifactFormat") != "terminal-native-runtime-v1":
        fail(f"{tool_id} is not declared as a Terminal native runtime")
    if not tool.get("category") or not tool.get("abis"):
        fail(f"{tool_id} is missing category or ABI metadata")
    if state == "available":
        for key in ("version", "codeArtifacts"):
            if not tool.get(key):
                fail(f"available tool {tool_id} is missing {key}")
        for artifact in tool["codeArtifacts"]:
            if not artifact.get("name", "").endswith(".apk"):
                fail(f"{tool_id} contains a non-APK code artifact")
            if artifact.get("abi") not in tool["abis"]:
                fail(f"{tool_id} artifact ABI is not declared by the package")
            if not isinstance(artifact.get("minApi"), int) or artifact["minApi"] < 29:
                fail(f"{tool_id} artifact has an invalid minApi")
            if urlparse(artifact.get("url", "")).scheme != "https":
                fail(f"{tool_id} artifact URL is not HTTPS")
            if not isinstance(artifact.get("size"), int) or artifact["size"] <= 0:
                fail(f"{tool_id} artifact has an invalid size")
            if not re.fullmatch(r"[0-9a-f]{64}", artifact.get("sha256", "")):
                fail(f"{tool_id} artifact has an invalid SHA-256")
            if not re.fullmatch(r"[0-9A-F]{64}", artifact.get("signerSha256", "")):
                fail(f"{tool_id} code artifact has an invalid signer SHA-256")
        for artifact in tool.get("dataArtifacts", []):
            if not artifact.get("name", "").endswith(".tpkg"):
                fail(f"{tool_id} contains a non-tpkg data artifact")
            if artifact.get("abi") not in tool["abis"]:
                fail(f"{tool_id} data artifact ABI is not declared by the package")
            if not isinstance(artifact.get("minApi"), int) or artifact["minApi"] < 29:
                fail(f"{tool_id} data artifact has an invalid minApi")
            if urlparse(artifact.get("url", "")).scheme != "https":
                fail(f"{tool_id} data artifact URL is not HTTPS")
            if not isinstance(artifact.get("size"), int) or artifact["size"] <= 0:
                fail(f"{tool_id} data artifact has an invalid size")
            if not re.fullmatch(r"[0-9a-f]{64}", artifact.get("sha256", "")):
                fail(f"{tool_id} data artifact has an invalid SHA-256")

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
