# Four root artifacts: preservation and cleanup

Author: Aldrin Payopay · GPL-3.0-only · September 5, 2026

This review covers four tracked root artifacts at commit `20b62dcc92e54d622c2481db2158c5a6f093b9ba`. The four former root paths were removed after their retained copies were verified.

| Original root path | Preservation and retained location |
| --- | --- |
| `The Anisotropic Gyroid Prismatic Helix.md` | Byte-identical to [papers/AGPH_General.md](../../papers/AGPH_General.md); the paper is retained and the duplicate root copy was removed. |
| `The Anisotropic Gyroid Prismatic Helix - Engineering.md` | Exactly [papers/AGPH_Engineering.md](../../papers/AGPH_Engineering.md) plus one final newline; the paper is retained and the duplicate root copy was removed. |
| `current_error_screenshot.png` | Byte-preserved under [dated visual evidence](../artifacts/2025-12-08-visual-verification/current_error_screenshot.png); the former root copy was removed after synchronization. |
| `current_error_screenshot_2.png` | Byte-preserved under [dated visual evidence](../artifacts/2025-12-08-visual-verification/current_error_screenshot_2.png); the former root copy was removed after synchronization. |

Both exact original manuscript byte streams, including the engineering copy's extra newline, are preserved privately in the development workspace with a provenance manifest. The canonical papers were not edited. This report reproduces no manuscript content or manufacturing details and makes no new validation claim about those papers.

| Original root file | Bytes | SHA-256 |
| --- | ---: | --- |
| General manuscript | 4,847 | `03fce3ce10fd8150dc0f735aa7e9bb32690c3193d8e8d7a648c6416e33e72a76` |
| Engineering manuscript | 5,678 | `b0b3223da149b2bebd93fa3bd196271af99e8bb89bae2fe147511568aae45d48` |
| First screenshot | 21,545 | `9cd9bf4ae3b48accb9f3c32a33de3ce8ce105e2e0744ddc9a0a7b83a65208cb5` |
| Second screenshot | 156,249 | `24411a6f9b8e800c2cca64aaae73184a9971888912ca2461997e2abda9f38211` |

The canonical engineering paper is 5,677 bytes, SHA-256 `8e89ea932993352d6541b3932cda055fd9914569d8603326c45e5b884daa7080`. The general paper's hash equals its root copy. Every preserved copy was checked against the original bytes before removal.

An exact-filename `git grep -n -I -F` over tracked text found zero references to the four original paths or the two canonical paper filenames before adding this report. This does not inspect external links, untracked callers or dynamically constructed paths. The manuscript copies last changed in `c5cff138` on December 2, 2025; both screenshots entered the repository in `0ebd7f53` on December 8, 2025.

All four root paths were unclassified in the lifecycle registry at review time. The retained papers are covered by `papers-and-theory` with experimental status; the dated screenshot destination falls under `historical-archive`. The [screenshot note](../artifacts/2025-12-08-visual-verification/README.md) describes historical evidence without treating it as a current bug report. No broad cleanup or content-validity review was performed.
