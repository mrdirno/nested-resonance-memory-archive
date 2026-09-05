# SEVEN music player prototype

Author: Aldrin Payopay · Preserved September 4, 2026 · GPL-3.0-only

Status: **dormant integration draft**, excluded from the classic Bridge build.

`SevenPlayer.tsx` and `integration.patch` preserve the inherited unpublished player and its four-line App integration. The intended experience is drinoman's SEVEN album with STILL first, followed by a shuffled playlist. The code depends on signed audio URLs from Persona500.

During the archive review, an anonymous POST to the token endpoint for one listed track, with the GitHub Pages origin, returned HTTP 403 and no `Access-Control-Allow-Origin` header. No token or audio was obtained. This is a specific probe result; it does not establish whether every authorized browser session would fail. The draft also swallows playback/token errors, lacks unmount cleanup, and can report playback before the audio promise resolves.

Before promotion: establish an authorized origin contract with the audio service, surface recoverable errors, cancel stale requests, clean up the audio element on unmount, and test play/pause/track transitions in a real browser. The source and patch remain available for that work. This preservation is not a release or a claim that the player works.
