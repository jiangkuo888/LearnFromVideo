# Bilibili browser fallback

Use this only when the supplied video normally plays in the user's available browser. Navigate to the video and allow the player to initialize. If login, CAPTCHA, purchase or region restrictions prevent normal playback, ask for the required user action or an authorized local file; do not claim acquisition succeeded.

Evaluate the function in [browser-export.js](browser-export.js) on that page with the available browser automation tool. It reads only the current video's metadata and playable tracks, then uses the already-observed player metadata request to obtain subtitles. It returns `{source, subtitles}`. Save the result directly to private JSON with the browser tool's output-file feature, keeping signed media addresses out of the chat. If the browser tool's writable roots differ from the destination project, export inside an allowed private staging directory and copy the resulting file using the filesystem tools.

Split and sanitize the export with:

```powershell
python "<skill>/scripts/watch2skill.py" import-browser "export.json" --out ".private/video-id"
python "<skill>/scripts/watch2skill.py" prepare "https://www.bilibili.com/video/VIDEO_ID/" --out "runs/video-id" --browser-source ".private/video-id/browser-source.json" --subtitles ".private/video-id/subtitles.json"
```

If the export has no subtitles, omit `--subtitles` and use the optional ASR path after acquisition. Canonical URL and export must identify the same video. Signed addresses can expire or be bound to a network location. Refresh only through normal page playback when needed; otherwise use an authorized local file or media saved in the browser's network environment.

Do not export browser cookies, user profiles or whole player API responses. Keep private exports out of version control. `import-browser` retains only expected source fields. Downloader uses standard byte ranges with four workers and at most two attempts per block; it does not manipulate authentication or platform access controls.
