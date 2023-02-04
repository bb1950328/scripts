#!/usr/bin/env python3
import datetime
import os
import pathlib
import re
from typing import Optional, Sequence

DIRECTORY_PATH = pathlib.Path("/tmp")


def extract_datetime(filename: str) -> Optional[datetime.datetime]:
    search = re.search(r"(20\d{2})(\d{2})(\d{2})", filename)
    if search:
        return datetime.datetime(int(search.group(1)), int(search.group(2)), int(search.group(3)))


if __name__ == '__main__':
    changed = 0
    for f in DIRECTORY_PATH.rglob("*"):
        dt = extract_datetime(f.name)
        if dt:
            os.utime(f, (dt.timestamp(), dt.timestamp()))
            changed += 1
        else:
            print(f"WARN: no date found for {f}")
    print(f"INFO: changed {changed} files.")
