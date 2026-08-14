[Deutsch](iso-builds.md) | [English](iso-builds.en.md)

# ISO builds

Built live/installation images (`eggs produce`, see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 16) are **not**
versioned in Git - several GB per file, and GitHub blocks individual
files over 100 MB anyway. Instead: the file lives in Stephan's
self-hosted Nextcloud (same idea as the encrypted key backups, see
[sicherheit-datenschutz.en.md](sicherheit-datenschutz.en.md)), and this
repo only holds this lightweight ledger - so it stays traceable which
ISO belongs to which code state, without versioning the file itself.

## Fill in when building a new ISO

```bash
sha256sum DialOS-Live-X.Y.Z.iso
git log -1 --format=%H
```

| Version | Filename | Date | Commit | SHA256 | Location |
|---|---|---|---|---|---|
| _(template)_ | `DialOS-Live-X.Y.Z.iso` | YYYY-MM-DD | `abcdef1` | `…` | Nextcloud path |

## Builds so far

Not yet backfilled - the two 0.5.0 test ISOs built so far
(`DialOS-Live-0.5.0.iso`, `DialOS-Live-0.5.0-clone.iso`, see the
[README changelog](../README.en.md#changelog)) no longer exist locally,
so checksum/commit mapping can't be reliably reconstructed after the
fact. Fill in the table above starting with the next build.
