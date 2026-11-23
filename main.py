#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

The meme image is drawn at build time and committed as entry.png
(the grading sandbox is stdlib-only, so this program simply copies
the finished image to /output/entry.png).

Before copying, it validates entry.png against the competition gate
so a bad image fails loudly here instead of silently scoring 0:
a whole PNG, at most 1 MiB (1,048,576 bytes) and at most
1024 by 1024 pixels. Validation is stdlib-only (struct + zlib).
"""
import os
import shutil
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))

MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def validate_png(path):
    """Check path is a whole PNG within the gate; return (width, height)."""
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")
    if size > MAX_BYTES:
        fail(f"entry.png is {size} bytes, over the 1 MiB gate ({MAX_BYTES})")
    if size == 0:
        fail("entry.png is empty")

    with open(path, "rb") as fh:
        data = fh.read()

    if data[:8] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG signature")
    if len(data) < 33 or data[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one is expected")

    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0:
        fail(f"entry.png has zero dimension ({width}x{height})")
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail(
            f"entry.png is {width}x{height}, over the "
            f"{MAX_WIDTH}x{MAX_HEIGHT} gate"
        )

    # Walk the chunk list to confirm the file is a whole PNG, not a
    # truncated prefix: every chunk header must be in bounds and the
    # IEND chunk must be present and complete.
    pos = 8
    saw_iend = False
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        end = pos + 12 + length
        if end > len(data):
            fail(f"entry.png is truncated inside the {chunk_type!r} chunk")
        crc = zlib.crc32(data[pos + 4 : pos + 8 + length]) & 0xFFFFFFFF
        stored = struct.unpack(">I", data[pos + 8 + length : end])[0]
        if crc != stored:
            fail(f"entry.png has a bad CRC in the {chunk_type!r} chunk")
        if chunk_type == b"IEND":
            saw_iend = True
            break
        pos = end
    if not saw_iend:
        fail("entry.png has no IEND chunk (truncated file)")

    return width, height


def main():
    src = os.path.join(HERE, "entry.png")
    width, height = validate_png(src)
    size = os.path.getsize(src)
    print(
        f"entry.png OK: {width}x{height} px, {size} bytes "
        f"(gate: <= {MAX_WIDTH}x{MAX_HEIGHT} px, <= {MAX_BYTES} bytes)"
    )
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(src, "/output/entry.png")
    copied = os.path.getsize("/output/entry.png")
    if copied != size:
        fail(f"copy mismatch: wrote {copied} bytes, expected {size}")
    print(f"wrote /output/entry.png ({copied} bytes)")


if __name__ == "__main__":
    main()
