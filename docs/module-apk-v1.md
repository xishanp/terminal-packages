# Terminal module APK v1

Native command-line environments are Android split APKs inherited by the
installed `com.terminal` package. A ZIP, tar archive or standalone application
is not a Terminal module.

## Required identity

- Package name: `com.terminal`
- Version code: exactly the installed base APK version code
- Signing certificate: exactly the installed base APK signer set
- Split name: stable tool id from `catalog-v1.json`
- ABI: one supported ABI or `all` for architecture-independent bytecode/data

## Catalogue artifact

An available tool has one artifact per supported ABI:

```json
{
  "id": "python",
  "state": "available",
  "version": "3.x.y",
  "signerSha256": "UPPERCASE_CERTIFICATE_SHA256",
  "artifacts": [
    {
      "abi": "arm64-v8a",
      "name": "terminal-python-3.x.y-arm64-v8a.apk",
      "url": "https://github.com/xishanp/terminal-packages/releases/download/...",
      "size": 123,
      "sha256": "lowercase_payload_sha256"
    }
  ]
}
```

The client must reject an artifact before installation when any identity,
version, signer, ABI, size or SHA-256 field differs. Installation uses Android
`PackageInstaller` in inherit-existing mode and therefore retains Android's
required user confirmation in NORMAL mode.

## Runtime layout

Executable ELF files remain in Android's read-only native library directory.
Standard libraries, headers and scripts may be compressed in the module and
expanded into the app-private environment directory after their manifest and
hashes have been verified.

Removing the main application removes all private runtime state. The shared
`/storage/emulated/0/APK` workspace remains user-owned and is never silently
deleted.
