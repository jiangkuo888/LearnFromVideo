# Rename to Watch2Skill — 0.3.0

The project was previously named LearnFromVideo. The repository and documentation
now use Watch2Skill, and the Python distribution/module are `watch2skill`.

| Surface | Current name |
|---|---|
| Repository | jiangkuo888/Watch2Skill |
| CLI | `watch2skill` |
| Skill invocation | `$watch2skill` |
| Skill ZIP | `watch2skill.zip` |
| Python module | `python -m watch2skill` |

`lfv` remains a console-command alias in the new package for existing command
recipes. The old Python import path is not provided by the renamed distribution.
Existing @1 evidence schemas retain their `learnfromvideo.*@1` identifiers;
changing the project name does not invalidate stored runs. Historical example
reports and version records preserve the names under which they were produced.

Install or update the renamed skill, then archive a verified old installation:

```sh
uv run python scripts/package_skill.py --install ~/.codex/skills --update --migrate-legacy
```

Migration only moves an old learn-from-video folder when its skill definition and
runtime project identify the legacy tool, and a new Watch2Skill skill is present.
The old folder is retained in watch2skill-backups beside the skills directory,
outside automatic skill discovery. Unknown directories are never replaced.

The inherited Hypit LICENSE, attribution and additional restrictions are unchanged.
