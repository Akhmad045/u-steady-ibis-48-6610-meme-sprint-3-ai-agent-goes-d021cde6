#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

The meme image is drawn at build time and committed as entry.png
(the grading sandbox is stdlib-only, so this program simply copies
the finished image to /output/entry.png).
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(src, "/output/entry.png")


if __name__ == "__main__":
    main()
