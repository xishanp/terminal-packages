# Terminal native package v1

Terminal command-line tools use a signed-code/private-data model. They are not
Termux packages, PRoot images or Linux distribution containers.

Android 10-16 does not provide a portable contract for executing newly
downloaded machine code from an app-writable directory. Therefore:

- Android/Bionic machine code is delivered in a split APK signed exactly like
  the installed `com.terminal` base APK.
- Standard libraries, headers, scripts, certificates and other writable data
  are installed from a `.tpkg` into the private application prefix.
- A `.tpkg` must never contain executable machine code.

## Runtime prefix

The client owns this layout below `Context.filesDir`:

```text
usr/bin
usr/lib
usr/include
usr/share
usr/etc
var/lib/terminal/packages
var/cache/terminal/packages
```

Uninstalling `com.terminal` removes the complete private prefix. The public
`/storage/emulated/0/APK` workspace is unrelated and remains user-owned.

## Catalogue artifact

An available tool has one artifact for each supported Android ABI:

```json
{
  "id": "python",
  "artifactFormat": "terminal-native-runtime-v1",
  "state": "available",
  "version": "3.x.y",
  "dependencies": [],
  "codeArtifacts": [
    {
      "abi": "arm64-v8a",
      "minApi": 29,
      "name": "terminal-python-code-3.x.y-arm64-v8a.apk",
      "url": "https://github.com/xishanp/terminal-packages/releases/download/...",
      "size": 123,
      "sha256": "lowercase_payload_sha256",
      "signerSha256": "uppercase_android_signer_sha256"
    }
  ],
  "dataArtifacts": [
    {
      "abi": "arm64-v8a",
      "minApi": 29,
      "name": "python-3.x.y-arm64-v8a.tpkg",
      "url": "https://github.com/xishanp/terminal-packages/releases/download/...",
      "size": 123,
      "sha256": "lowercase_payload_sha256"
    }
  ]
}
```

`building` entries are roadmap metadata and have no downloadable artifacts.
Code APK installation uses PackageInstaller inherit-existing mode and retains
Android's required user confirmation in NORMAL mode.

## Container

A `.tpkg` is a ZIP/Deflate container. It contains exactly one
`terminal-package.json` plus payload paths rooted at `usr/`.

```json
{
  "schemaVersion": 1,
  "id": "python",
  "version": "3.x.y",
  "abi": "arm64-v8a",
  "minApi": 29,
  "dependencies": [],
  "files": [
    {
      "path": "usr/bin/python3",
      "size": 123,
      "sha256": "lowercase_file_sha256",
      "executable": false
    }
  ]
}
```

Paths must be normalized relative paths under `usr/`. Absolute paths, `..`,
symlinks, devices, duplicate entries, executable payloads and undeclared files
are rejected.

## Installation transaction

1. Download to a private `.part` file.
2. Verify declared length and SHA-256.
3. Select artifacts matching the device ABI and Android API.
4. Verify the code APK package identity, base version and Android signer before
   requesting its installation.
5. Validate the data manifest before extracting.
6. Extract into a private staging directory and verify every file.
7. Reject files owned by another installed package.
8. Back up replaced files, commit the staged files, then write the ownership
   manifest atomically. Roll back on any failure.
9. Remove only files owned by that package during uninstall.

Native executables must be built for Android/Bionic and packaged in the signed
code APK. Renamed Termux packages and binaries built for glibc are not accepted.
