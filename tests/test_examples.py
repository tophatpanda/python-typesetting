import hashlib
import os
import re
import subprocess

test_dir = os.path.dirname(__file__)


def generate_example(name, script_file="typeset.py"):
    os.makedirs(os.path.join(test_dir, ".render"), exist_ok=True)

    script_path = os.path.join(test_dir, "..", "examples", name, script_file)
    out_path = os.path.join(test_dir, ".render", name + ".pdf")
    subprocess.run(["python", script_path, out_path], check=True)

    return out_path


def test_pylondinium():
    path = generate_example("pylondinium")
    assert os.path.getsize(path) == 374743


def test_frames_and_floats():
    path = generate_example("frames-and-floats")
    assert os.path.getsize(path) == 46387


def test_frames_and_floats():
    path = generate_example("jre")
    assert os.path.getsize(path) == 46387
