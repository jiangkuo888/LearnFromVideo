# Contributing

Read LICENSE and NOTICE before contributing. This is source-available under the
Hypit license with additional conditions; contribution does not change those terms.

## Development

Install uv, Python 3.11+, FFmpeg/ffprobe and optionally Node.js for YouTube.
From a checkout:

```sh
uv sync --locked
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run python -m unittest discover -s tests -v
uv build
uv run python scripts/package_skill.py
uv run python scripts/check_release.py
uv run python scripts/check_repository.py
uv run python scripts/smoke_release.py
```

Use `uv sync --extra asr` for speech recognition. Unit/integration tests use
generated media and do not fetch external videos or models. Installation smoke
checks can access the package index. Real platform tests are opt-in because
availability can vary independently of code.

Changes should preserve observable behavior and carry a regression test when fixing
a bug. Document actual video/sample provenance, command, tool versions, evidence
coverage and limitations for real-world tests. Do not report unobserved frames,
unverified practice, or schema validity as semantic accuracy.

Treat installed skill updates as complete managed-tree replacements. The installer
keeps a backup outside the skills directory; do not remove it until the new skill
is verified. Do not assign maintainer ownership or contact details to someone who
has not agreed. Follow CODE_OF_CONDUCT.md when collaborating.

Never submit cookies, signed media URLs, API credentials, personal absolute paths,
model caches, third-party media or full transcripts. Use synthetic subtitle fixtures
and generated videos for automated tests. See docs/ARCHITECTURE.md for boundaries.
