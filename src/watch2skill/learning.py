"""Watch2Skill learning; Hypit-derived workflow, see LICENSE and PROVENANCE.md."""

import hashlib
import math
import re
from pathlib import Path

from .core import read, save


def search(folder, query):
    terms = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", query.lower())
    if not terms:
        raise ValueError("Search needs words or Chinese characters")
    source = read(folder / "manifest.json")["source"]
    results = []
    for c in read(folder / "chunks.json"):
        score = sum(c["text"].lower().count(t) for t in terms)
        if score:
            results.append(
                c
                | {
                    "score": score,
                    "source_link": source
                    + ("&" if "?" in source else "?")
                    + "t="
                    + str(int(c["start"])),
                }
            )
    return sorted(results, key=lambda c: (-c["score"], c["start"]))[:8]


def safe_evidence(folder, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("Evidence must be a relative path")
    p = (folder / relative).resolve()
    if not p.is_relative_to(folder.resolve()) or not p.is_file():
        raise ValueError(f"Missing or outside-run evidence: {relative}")
    return p


def validate(folder):
    # A failed recheck must never leave an earlier successful report behind.
    (folder / "validation.json").unlink(missing_ok=True)
    manifest, learning = read(folder / "manifest.json"), read(folder / "learning.json")
    if manifest["state"] == "learning-reviewed":
        manifest["state"] = "evidence-ready"
        save(folder / "manifest.json", manifest)
    if manifest["state"] not in ("evidence-ready", "learning-reviewed"):
        raise ValueError("Complete evidence preparation first")
    if (
        not isinstance(learning.get("summary"), str)
        or not learning["summary"].strip()
        or not learning.get("claims")
    ):
        raise ValueError("Learning needs a summary and sourced claims")
    known = {
        f["path"]: f["requested_time"] for index in folder.glob("*/index.json") for f in read(index)
    }
    reviewed = learning.get("reviewed_frames", [])
    if not reviewed:
        raise ValueError("Record frames actually inspected")
    for p in reviewed:
        safe_evidence(folder, p)
        if p not in known:
            raise ValueError(f"Unknown frame: {p}")
    for c in learning["claims"]:
        if (
            not c.get("text")
            or c.get("kind") not in ("observation", "inference")
            or not c.get("evidence")
        ):
            raise ValueError("Claim needs text, kind and evidence")
        if not (
            math.isfinite(c["start"])
            and math.isfinite(c["end"])
            and 0 <= c["start"] < c["end"] <= manifest["duration"] + 2
        ):
            raise ValueError("Claim interval outside source")
        for p in c["evidence"]:
            safe_evidence(folder, p)
            if p not in reviewed or not c["start"] <= known[p] <= c["end"]:
                raise ValueError(f"Claim frame must be reviewed and within interval: {p}")
    if learning.get("practice", {}).get("status") not in (
        "not-run",
        "passed",
        "failed",
    ) or not isinstance(learning.get("limitations"), list):
        raise ValueError("Record practice status and limitations")
    if (
        learning["practice"]["status"] in ("passed", "failed")
        and not learning["practice"].get("details", "").strip()
    ):
        raise ValueError("Practice result needs concrete details and scope")
    result = {
        "schema": "learnfromvideo.validation@1",
        "passed": True,
        "claims": len(learning["claims"]),
        "reviewed_frames": len(reviewed),
        "practice": learning["practice"]["status"],
        "learning_sha256": hashlib.sha256((folder / "learning.json").read_bytes()).hexdigest(),
        "scope": "Structural evidence references only; truth and mastery require agent review.",
    }
    save(folder / "validation.json", result)
    manifest["state"] = "learning-reviewed"
    save(folder / "manifest.json", manifest)
    return result
