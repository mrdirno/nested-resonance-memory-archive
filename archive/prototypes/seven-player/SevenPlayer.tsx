/**
 * SevenPlayer — background music for the NRM kaleidoscope page.
 *
 * Plays drinoman's SEVEN album (persona500 LLC). Order: "STILL" first, then the
 * rest of the album shuffled, looping. Audio is token-protected: the NRM archive
 * is an approved child origin of persona500.com and fetches short-lived signed
 * URLs from /api/audio/token (same pattern as the persona500 StickyPlayer) — the
 * raw files are never exposed. Browser autoplay policy requires a user gesture,
 * so playback starts on the play button.
 */
import React, { useCallback, useRef, useState } from 'react';

const API = 'https://persona500.com';

type Track = { key: string; title: string };
const SEVEN: Track[] = [
  { key: 'seven/01-still', title: 'STILL' },
  { key: 'seven/02-next-season', title: 'NEXT SEASON' },
  { key: 'seven/03-seven', title: 'SEVEN' },
  { key: 'seven/04-strawberry-margarita-remix', title: 'STRAWBERRY MARGARITA (remix)' },
  { key: 'seven/05-im-so-frozen', title: "I'M SO FROZEN" },
  { key: 'seven/06-worth-it-bau-bau', title: 'WORTH IT ((BAU BAU))' },
  { key: 'seven/07-my-plug-is-shady', title: 'MY PLUG IS SHADY' },
  { key: 'seven/08-ive-heard-it-all', title: "I'VE HEARD IT ALL" },
  { key: 'seven/09-screenshot-this-feeling', title: 'SCREENSHOT THIS FEELING' },
  { key: 'seven/10-im-late', title: "I'M LATE" },
  { key: 'seven/11-text-me-when-you', title: 'TEXT ME WHEN YOU' },
  { key: 'seven/12-passenger-side', title: 'PASSENGER SIDE' },
  { key: 'seven/13-slowly-then-suddenly', title: 'SLOWLY THEN SUDDENLY' },
  { key: 'seven/14-tiffany', title: 'TIFFANY' },
];

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// STILL first, then the remaining 13 shuffled.
const buildPlaylist = (): Track[] => [SEVEN[0], ...shuffle(SEVEN.slice(1))];

export const SevenPlayer: React.FC = () => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const tokensRef = useRef<Record<string, { url: string; expires: number }>>({});
  const playlistRef = useRef<Track[]>(buildPlaylist());
  const idxRef = useRef(0);
  const [started, setStarted] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [title, setTitle] = useState('');

  const fetchTokens = useCallback(async () => {
    const res = await fetch(`${API}/api/audio/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracks: SEVEN.map((t) => t.key) }),
    });
    if (!res.ok) throw new Error(`token ${res.status}`);
    const data = await res.json();
    tokensRef.current = data.tokens || {};
  }, []);

  const playIndex = useCallback(async (i: number) => {
    const now = Date.now() / 1000;
    const track = playlistRef.current[i];
    if (!track) return;
    let tok = tokensRef.current[track.key];
    if (!tok || tok.expires <= now + 5) {
      await fetchTokens();
      tok = tokensRef.current[track.key];
    }
    if (!tok || !audioRef.current) return;
    audioRef.current.src = tok.url;
    setTitle(track.title);
    try { await audioRef.current.play(); setPlaying(true); } catch { /* */ }
  }, [fetchTokens]);

  const start = useCallback(async () => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.volume = 0.7;
      audioRef.current.addEventListener('ended', () => {
        idxRef.current += 1;
        if (idxRef.current >= playlistRef.current.length) {
          // album finished — reshuffle the non-STILL tracks and loop
          idxRef.current = 0;
          playlistRef.current = [SEVEN[0], ...shuffle(SEVEN.slice(1))];
        }
        playIndex(idxRef.current);
      });
    }
    setStarted(true);
    try {
      await fetchTokens();
      idxRef.current = 0;
      await playIndex(0); // STILL
    } catch { /* token/CORS unavailable (e.g. local preview) — stays idle */ }
  }, [fetchTokens, playIndex]);

  const toggle = useCallback(() => {
    if (!started) { start(); return; }
    const a = audioRef.current;
    if (!a) return;
    if (a.paused) { a.play(); setPlaying(true); }
    else { a.pause(); setPlaying(false); }
  }, [started, start]);

  return (
    <button
      onClick={toggle}
      title="drinoman — SEVEN (STILL, then shuffle)"
      className="absolute bottom-3 right-3 z-20 flex items-center gap-2 px-3 py-2 rounded-full
                 bg-black/45 backdrop-blur-md border border-fuchsia-500/25 text-xs text-gray-200
                 hover:bg-black/70 transition-colors max-w-[60vw]"
    >
      <span className="text-fuchsia-400">{!started ? '♪' : playing ? '❚❚' : '►'}</span>
      <span className="truncate">
        {!started ? 'Play SEVEN — drinoman' : `${playing ? '' : 'Paused · '}${title || 'SEVEN'}`}
      </span>
    </button>
  );
};
