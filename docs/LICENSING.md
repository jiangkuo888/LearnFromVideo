# Licensing and publication

LearnFromVideo retains the Hypit license verbatim. The owner chose to publish
source with these additional restrictions preserved. Do not describe this as MIT,
standard Apache-2.0, or an OSI-approved open-source license.

The license includes conditions on multi-tenant hosting, commercial redistribution,
and Hypit attribution. Read [LICENSE](../LICENSE) for the actual terms; this summary
does not replace them. The [Open Source Definition](https://opensource.org/osd)
requires free redistribution and does not allow restrictions on commercial fields
of use. Consequently this repository uses the term **source-available**.

[PROVENANCE.md](../PROVENANCE.md) maps the upstream source snapshots and adaptations.
Keep LICENSE, NOTICE and provenance with source and skill distributions. A future
move to a different license requires resolving upstream rights; deleting the
vendor directory alone does not change the licensing of existing derived code.

Dependency licenses apply separately. yt-dlp, requests, Pillow and faster-whisper
are installed from their upstream packages, not copied into source. The lockfile
records exact dependencies; model weights are downloaded separately into the model
cache. Distribution operators must account for their selected FFmpeg build and
model licenses.

Example reports reference third-party videos. Source media and full transcripts
are not distributed with this repository. Permission to use this code does not
grant permission to redistribute arbitrary downloaded videos.
