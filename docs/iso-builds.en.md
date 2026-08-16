[Deutsch](iso-builds.md) | [English](iso-builds.en.md)

# ISO builds

Built backup images (Rescuezilla/Clonezilla, see
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
| 0.5.1 | `DialOS-Live-0.5.1-clone.iso` | 2026-08-16 | `ac89f26` | `73378ae3da384e28ef1123c0efad9e98122c8c12ae4edbd26dc8496ce587ed32` | Nextcloud (upload by Stephan still pending) |

## Builds so far

The two originally built 0.5.0 test ISOs
(`DialOS-Live-0.5.0.iso`, `DialOS-Live-0.5.0-clone.iso`, see the
[README changelog](../README.en.md#changelog)) no longer exist locally,
so checksum/commit mapping can't be reliably reconstructed after the
fact.

`DialOS-Live-0.5.1-clone.iso` (see table above) is a backup snapshot of
the complete system state before the planned end-to-end test of the new
install path (`dialos-full-office-setup.sh` +
`dialos-setup-home-partition.sh`, see TODO.md) - if that test goes
wrong, the device can be restored to this known-working state from it
(built with `--clone`, includes `dialosadmin`/`nutzer` with their home
directories).
