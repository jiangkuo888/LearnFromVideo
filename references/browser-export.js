// Pass this function to a browser tool's page evaluation on a normally playable
// Bilibili video. Save the returned object as PRIVATE JSON, not chat text.
// No cookies, user identity or full player responses are exported.
async () => {
  const video = window.__INITIAL_STATE__?.videoData;
  const play = window.__playinfo__?.data;
  if (!video || !play?.dash) throw new Error("No accessible Bilibili DASH video in this page");
  const videoTrack = play.dash.video.filter(x => x.codecs.startsWith("avc"))
    .sort((a, b) => b.height - a.height)[0];
  const audioTrack = play.dash.audio[0];
  if (!videoTrack || !audioTrack) throw new Error("Playable audio/video tracks unavailable");
  const source = {
    schema: "learnfromvideo.browser-source@1",
    url: `https://www.bilibili.com/video/${video.bvid}/`,
    id: video.bvid, title: video.title, duration: video.duration,
    author: video.owner.name, video_url: videoTrack.baseUrl,
    audio_url: audioTrack.baseUrl, user_agent: navigator.userAgent
  };
  const endpoint = performance.getEntriesByType("resource").map(x => x.name)
    .find(u => u.includes("/x/player/wbi/v2"));
  if (!endpoint) throw new Error("Player subtitle metadata request not observed; let player initialize");
  const response = await (await fetch(endpoint, {credentials: "include"})).json();
  if (response.code !== 0) throw new Error(`Player metadata failed: ${response.code}`);
  const subs = response.data.subtitle?.subtitles || [];
  const subtitle = subs.find(s => s.lan === "zh-CN" || s.lan === "zh") ||
    subs.find(s => s.lan === "ai-zh") || subs[0];
  const subtitles = subtitle?.subtitle_url
    ? await (await fetch(new URL(subtitle.subtitle_url, location.href))).json() : null;
  document.querySelector("video")?.pause();
  return {source, subtitles};
}
