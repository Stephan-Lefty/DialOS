[Deutsch](iso-builds.md) | [English](iso-builds.en.md)

# Image ledger

Backup images (Rescuezilla/Clonezilla, see
[Debian-zu-DialOS.en.md](Debian-zu-DialOS.en.md), step 16) are **not**
versioned in Git - several GB per file, and GitHub blocks individual
files over 100 MB anyway. Only this slim ledger lives here, so it stays
traceable which image belongs to which code state without versioning the
file itself.

## Cleanup on 2026-08-16

**Eight old ISOs were deliberately deleted** (about 59 GB) - not a data
mishap but a decision. All came from the Penguins' Eggs era, dropped the
same day (see step 16), and represented system states that the
2026-08-16 rebuild has substantially superseded. No checksums existed for
any of them, only for the one remaining below.

Deleted: `DialOS-Clone-mit-home.iso`, `DialOS-live.iso`,
`DialOS-Live-0.1.iso`, `DialOS-Live-0.2.0.iso`, `DialOS-Live-0.3.0.iso`,
`DialOS-Live-0.4.0.iso`, `DialOS-Live-0.5.0.iso`,
`DialOS-Live-0.5.0-clone.iso`.

## Current holdings

| Version | Filename | Date | Commit | SHA256 | Location |
|---|---|---|---|---|---|
| 0.5.1 | `DialOS-Live-0.5.1-clone.iso` | 2026-08-16 | `ac89f26` | `73378ae3da384e28ef1123c0efad9e98122c8c12ae4edbd26dc8496ce587ed32` | external drive only, `DialOS-ISOs/` |

**This file deliberately stays until the first Rescuezilla image exists**
(Stephan's decision, 2026-08-16). It was the safety net for the
end-to-end test of the new build path - that test passed, so its purpose
is served. But it exists nowhere else and could not be recreated, because
the build path behind it is gone. Hence: delete only once the replacement
is there, so there is never a moment without any fallback.

## To record when creating a new image

Rescuezilla produces directories rather than a single file, so a checksum
sensibly refers to the archive or is omitted. Worth recording in any case
is the commit state the image belongs to:

```bash
git log -1 --format=%H
```

And **what the image does not contain**: the LUKS partition
`dialos-nutzer-home` is deliberately excluded (rationale in step 16). An
image therefore restores root and EFI, not `nutzer`'s data.
