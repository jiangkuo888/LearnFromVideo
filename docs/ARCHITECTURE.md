# Architecture

Watch2Skill has two layers: deterministic local evidence tools and a skill that
guides a multimodal agent. The CLI does not call a reasoning-model API or silently
turn extraction into learned knowledge.

| Module | Responsibility |
|---|---|
| core | JSON persistence, source URLs, subprocesses and time formatting |
| acquisition | yt-dlp or explicit browser-export acquisition |
| transcripts | Subtitle normalization, rolling-VTT cleanup and optional ASR |
| media | ffprobe, timestamped frame extraction and overview sheets |
| pipeline | Empty-run initialization and evidence preparation |
| learning | Lexical retrieval and evidence-reference validation |
| cli | Argument parsing and command dispatch |

A run advances through acquiring → media-ready → evidence-ready (or
needs-transcript / needs-frames) → learning-reviewed. Failures retain a manifest
and any completed media. `frames` and `transcribe` can complete missing evidence;
`prepare` never overwrites a run. Frame extraction precedes optional ASR so model
failure does not discard available visual evidence.

Evidence uses the local source clock. Frame indexes store requested seek times,
not native-frame PTS. Captions may be inaccurate. YouTube rolling-caption context
is removed only for VTT with inline timestamps; ordinary repeated cues remain.

Agent-written learning.json separates observation and inference, reviewed frame
paths, limitations and practice status. Validation checks bounds, paths and
references. It cannot verify that an agent really inspected an image or that a
claim is true. Source media and public reports are stored separately.

The repository has one authoritative tool source tree. Skill ZIP builds include a
runtime snapshot, lockfile and attribution; generated runtimes are ignored by Git.
Source skill launchers work from a complete checkout; standalone installation uses
the built ZIP or package_skill.py. A copied SKILL.md by itself is insufficient.
