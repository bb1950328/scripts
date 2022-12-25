#!/usr/bin/env python3
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pprint import pprint
from typing import Optional


def group_versions_hierarchically(versions: list[tuple[str, str]]) -> dict[int, dict[int, dict[int, str]]]:
    result = defaultdict(lambda: defaultdict(dict))
    for v in versions:
        if v[1].endswith(".tgz") or v[1].endswith(".tar.gz"):
            numbers = list(map(int, v[0].split(".")))
            major = numbers[0]
            minor = numbers[1] if len(numbers) > 1 else 0
            patch = numbers[2] if len(numbers) > 2 else 0
            result[major][minor][patch] = v
    return result


def try_parse_version_prompt(grouped_versions: dict[int, dict[int, dict[int, str]]], prompt: str) -> Optional[
    tuple[str, str]]:
    words = None
    try:
        words = list(map(int, prompt.split("."))) if prompt else []
    except ValueError:
        return None

    in_question = grouped
    try:
        while words:
            in_question = in_question[words.pop(0)]

        while isinstance(in_question, dict):
            in_question = in_question[sorted(in_question.keys())[-1]]
    except (IndexError, KeyError):
        return None

    return in_question


def check_exit_code(exit_code: int, task_description: str) -> None:
    if exit_code != 0:
        print(task_description, "failed with exit code", exit_code, file=sys.stderr)
        sys.exit(1)


def run_command(command: str, description: Optional[str] = None) -> None:
    check_exit_code(os.system(command), description if description is not None else command)


if __name__ == "__main__":
    versions: list[tuple[str, str]] = []
    with urllib.request.urlopen("https://www.python.org/downloads/source/") as response:
        html = response.read().decode("utf-8")
        for match in re.finditer(r"https://www\.python\.org/ftp/python/([\d.]*)/Python-\1\.tgz", html):
            versions.append((match.group(1), match.group()))
    grouped = group_versions_hierarchically(versions)
    chosen_version = None
    if len(sys.argv) == 1:
        print("available versions:")
        for m0 in reversed(sorted(grouped.keys())):
            for m1 in reversed(sorted(grouped[m0])):
                for m2 in reversed(sorted(grouped[m0][m1])):
                    print(grouped[m0][m1][m2][0], end=" ")
                print()
            print()

        while chosen_version is None:
            chosen = input("choose a version: ")
            chosen_version = try_parse_version_prompt(grouped, chosen)
    else:
        chosen_version = try_parse_version_prompt(grouped, sys.argv[1])
        if chosen_version is None:
            print(f"Version {sys.argv[1]} does not exist", file=sys.stderr)
            sys.exit(1)

    before = time.perf_counter()

    tgz_path = f"/tmp/Python{chosen_version[0]}.tgz"
    if not os.path.exists(tgz_path):
        run_command(f"wget -O {tgz_path} {chosen_version[1]}", f"Download of {chosen_version[1]}")

    source_folder_path = f"/tmp/Python{chosen_version[0]}"
    if os.path.exists(source_folder_path):
        run_command(f"rm -rf {source_folder_path}")
    run_command(f"mkdir {source_folder_path}")
    run_command(f"tar -xvzf {tgz_path} -C {source_folder_path}")
    source_folder_path += ("/" + os.listdir(source_folder_path)[0])

    cwd_backup = os.getcwd()
    try:
        os.chdir(source_folder_path)
        run_command("sudo ./configure --enable-optimizations --with-lto --enable-shared")
        run_command("make -j$(nproc)")
        run_command("sudo make altinstall")
    finally:
        os.chdir(cwd_backup)
    run_command(f"rm {tgz_path}")
    run_command(f"sudo rm -rf {source_folder_path}")

    print(f"Successfully installed Python {chosen_version[0]} in {time.perf_counter() - before}s.")
