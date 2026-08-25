# Terminal Packages

Official package catalogue for the native Android Terminal app.

The repository has two responsibilities:

- Describe trusted Android application sources without republishing their APKs.
- Publish Terminal native tool modules built for a specific Android ABI.

The app exposes this as one source named `Terminal Official`. F-Droid and
IzzyOnDroid payloads continue to be verified with their upstream repository
certificates. Native tool modules are published only after an APK with the
same application signature as Terminal has been built and checksummed.

Development environments are distributed as Terminal module APKs, never as
download-and-execute ZIP archives. The initial catalogue tracks Python,
Node.js, Git, Clang, CMake, Ninja, GNU Make, OpenJDK, AAPT2, Apktool and
smali/baksmali.

The curated Android development list includes editors, IDEs, package inspection,
release tracking, Shizuku, Termux and its API/Widget integrations. Their APKs
remain hosted and signed by their upstream projects; this repository records
identity and routing only.

Terminal Official pins every repository certificate in the Android client.
The catalogue includes F-Droid, IzzyOnDroid, MicroG, NewPipe, KDE, Bitwarden,
Briar, Molly, Collabora Office, CalyxOS, Fedilab, Cryptomator and SimpleX. A
remote catalogue may change HTTPS endpoints but cannot add a new trust anchor
to an installed app.

## Client commands

```sh
apk update
apk source list
apk source status
apk search <name>
apk install <package-or-file.apk>
```

## Files

- `catalog-v1.json`: machine-readable source and tool catalogue.
- `schema/catalog-v1.schema.json`: catalogue format.
- `scripts/validate_catalog.py`: dependency-free validation used by CI.
- `docs/module-apk-v1.md`: identity, signing and installation contract for tools.

Entries with `state: building` are visible roadmap entries, not downloadable
packages. Clients must never attempt to install them.
Official package catalog and native tool modules for Android Terminal
