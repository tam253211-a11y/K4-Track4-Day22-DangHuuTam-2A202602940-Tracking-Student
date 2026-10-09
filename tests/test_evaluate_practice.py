"""Tests for build_trackeval_cmd() without TrackEval or lab data."""

import subprocess
import sys
from pathlib import Path

from evaluate_practice import PRACTICE_VIDEO, build_trackeval_cmd


def test_cmd_targets_practice_video_only(tmp_path: Path) -> None:
    cmd = build_trackeval_cmd("python", tmp_path, "nhom01", "LAB", "train")
    assert cmd[0] == "python"
    assert cmd[3] == str(tmp_path / "scripts" / "run_mot_challenge.py")
    assert cmd[cmd.index("--SEQ_INFO") + 1] == PRACTICE_VIDEO
    assert cmd[cmd.index("--TRACKERS_TO_EVAL") + 1] == "nhom01"
    assert cmd[cmd.index("--BENCHMARK") + 1] == "LAB"
    assert cmd[cmd.index("--SPLIT_TO_EVAL") + 1] == "train"


def test_bootstrap_patches_numpy_in_child_process(tmp_path: Path) -> None:
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    probe = scripts_dir / "run_mot_challenge.py"
    probe.write_text(
        "import sys\n"
        "import numpy as np\n"
        "print(np.float is float, np.int is int, sys.argv[1])\n",
        encoding="utf-8",
    )
    cmd = build_trackeval_cmd(sys.executable, tmp_path, "nhom01", "LAB", "train")
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    assert out.split() == ["True", "True", "--GT_FOLDER"]
