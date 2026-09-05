// Timed, portable plain-text captions. Author: Aldrin Payopay <aldrin.gdf@gmail.com>
import { planTitle, type Measure, type TitlePlan } from './title';

export interface CaptionCue { id: string; start: number; end: number; text: string }
export interface CaptionTrack { cues: CaptionCue[]; place: 'bc' | 'tc'; size: 'sm' | 'md' | 'lg' }
export interface PlannedCaption extends CaptionCue { plan: TitlePlan }
export const MAX_CAPTION_CUES = 200;
export const MAX_CAPTION_TIME = 3600;
export const MIN_CAPTION_DURATION = 0.05;
export const EMPTY_CAPTION_TRACK: CaptionTrack = { cues: [], place: 'bc', size: 'md' };

export class CaptionError extends Error {
  constructor(message: string) { super(message); this.name = 'CaptionError'; }
}
const fail = (message: string): never => { throw new CaptionError(message); };
const millis = (n: number): number => Math.round(n * 1000);

/** Reject unsupported content rather than silently clipping or dropping a cue. */
export const cleanCaptionText = (raw: unknown): string => {
  if (typeof raw !== 'string') return fail('Caption text must be plain text.');
  const text = raw.replace(/\r\n?/g, '\n').replace(/\t/g, ' ').trim();
  if (!text) return fail('Each caption needs text.');
  if (text.length > 240) return fail('A caption can contain at most 240 characters. Split it into shorter cues.');
  if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/.test(text)) return fail('Caption text contains unsupported control characters.');
  if (/\n\s*\n/.test(text)) return fail('Use single line breaks within a cue; blank lines separate subtitle cues.');
  // Unpaired UTF-16 surrogates cannot survive a UTF-8 download faithfully.
  for (let i = 0; i < text.length; i++) {
    const c = text.charCodeAt(i);
    if (c >= 0xd800 && c <= 0xdbff) {
      const next = text.charCodeAt(++i);
      if (!(next >= 0xdc00 && next <= 0xdfff)) return fail('Caption text contains an incomplete Unicode character.');
    } else if (c >= 0xdc00 && c <= 0xdfff) return fail('Caption text contains an incomplete Unicode character.');
  }
  return text;
};

export const normalizeCaptionTrack = (raw: unknown): CaptionTrack => {
  if (raw == null) return { cues: [], place: 'bc', size: 'md' };
  if (typeof raw !== 'object' || Array.isArray(raw)) return fail('The caption track must be an object.');
  const value = raw as Record<string, unknown>;
  if (!Array.isArray(value.cues)) return fail('The caption track needs a cue list.');
  if (value.cues.length > MAX_CAPTION_CUES) return fail('A track can contain at most 200 captions.');
  const place = value.place ?? 'bc';
  const size = value.size ?? 'md';
  if (place !== 'bc' && place !== 'tc') return fail('Choose top or bottom caption placement.');
  if (size !== 'sm' && size !== 'md' && size !== 'lg') return fail('Choose a valid caption font size.');
  const ids = new Set<string>();
  const cues = value.cues.map((entry: unknown, index: number): CaptionCue => {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return fail(`Caption ${index + 1} is invalid.`);
    const cue = entry as Record<string, unknown>;
    if (typeof cue.id !== 'string' || !cue.id.trim() || cue.id.length > 120 || /[\u0000-\u001f]/.test(cue.id)) return fail(`Caption ${index + 1} needs a valid identifier.`);
    if (ids.has(cue.id)) return fail('Caption identifiers must be unique.');
    ids.add(cue.id);
    if (typeof cue.start !== 'number' || typeof cue.end !== 'number' || !Number.isFinite(cue.start) || !Number.isFinite(cue.end)) return fail(`Caption ${index + 1} needs finite start and end times.`);
    if (cue.start < 0 || cue.end > MAX_CAPTION_TIME || cue.end - cue.start < MIN_CAPTION_DURATION - 1e-9) return fail(`Caption ${index + 1} must last at least 0.05 seconds, between 0 and 3600 seconds.`);
    const start = millis(cue.start) / 1000;
    const end = millis(cue.end) / 1000;
    if (millis(end) - millis(start) < 50) return fail(`Caption ${index + 1} must last at least 0.05 seconds.`);
    return { id: cue.id, start, end, text: cleanCaptionText(cue.text) };
  }).sort((a, b) => a.start - b.start || a.end - b.end);
  for (let i = 1; i < cues.length; i++) {
    if (cues[i].start < cues[i - 1].end) return fail(`Captions ${i} and ${i + 1} overlap. Adjust their times before saving.`);
  }
  return { cues, place, size };
};

const parseTimestamp = (raw: string, format: 'srt' | 'vtt'): number => {
  const pattern = format === 'srt' ? /^(\d{2,}):(\d{2}):(\d{2}),(\d{3})$/ : /^(?:(\d{2,}):)?(\d{2}):(\d{2})\.(\d{3})$/;
  const m = raw.match(pattern);
  if (!m || Number(m[2]) > 59 || Number(m[3]) > 59) return fail(`Invalid ${format.toUpperCase()} timestamp: ${raw}`);
  return Number(m[1] || 0) * 3600 + Number(m[2]) * 60 + Number(m[3]) + Number(m[4]) / 1000;
};
const decodeText = (text: string): string => text.replace(/&(amp|lt|gt|quot|apos|nbsp|#\d+|#x[\da-f]+);/gi, (whole, entity: string) => {
  const names: Record<string, string> = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: '\u00a0' };
  if (entity[0] !== '#') return names[entity.toLowerCase()] ?? whole;
  const n = entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : parseInt(entity.slice(1), 10);
  return n > 0 && n <= 0x10ffff && !(n >= 0xd800 && n <= 0xdfff) ? String.fromCodePoint(n) : fail('A subtitle contains an invalid character entity.');
});
const escapeText = (text: string): string => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Plain SRT/WebVTT only. Styling, cue settings and karaoke markup are explicit errors. */
export const parseCaptions = (input: string, format?: 'srt' | 'vtt'): CaptionCue[] => {
  if (typeof input !== 'string' || input.length > 256_000) return fail('Choose a subtitle file smaller than 256 KB.');
  const text = input.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n').trim();
  const detected = /^WEBVTT(?:[ \t\n]|$)/.test(text) ? 'vtt' : 'srt';
  const kind = format ?? detected;
  if (kind === 'vtt' && detected !== 'vtt') return fail('A WebVTT file must start with WEBVTT.');
  if (kind === 'srt' && detected === 'vtt') return fail('This is WebVTT content; use a .vtt file.');
  let blocks = text.split(/\n[ \t]*\n/);
  if (kind === 'vtt') {
    const header = blocks.shift() ?? '';
    if (header.includes('\n')) return fail('WebVTT header metadata is not supported. Leave a blank line after WEBVTT.');
  }
  const cues: CaptionCue[] = [];
  for (const block of blocks) {
    if (!block.trim()) continue;
    if (kind === 'vtt' && /^NOTE(?:[ \t\n]|$)/.test(block)) continue;
    if (kind === 'vtt' && /^(STYLE|REGION)(?:[ \t\n]|$)/.test(block)) return fail('WebVTT STYLE and REGION blocks are not supported. Export plain subtitles.');
    const lines = block.split('\n');
    let timing = lines.shift() ?? '';
    if (!timing.includes('-->')) {
      if (kind === 'srt' && !/^\d+$/.test(timing.trim())) return fail('SRT cue numbers must be numeric.');
      timing = lines.shift() ?? '';
    }
    const match = timing.trim().match(/^(\S+)\s+-->\s+(\S+)(.*)$/);
    if (!match) return fail(`Caption ${cues.length + 1} needs a start --> end timestamp line.`);
    if (match[3].trim()) return fail('Subtitle positioning and cue settings are not supported. Import plain subtitles, then choose placement here.');
    const body = lines.join('\n');
    if (/<[^>]*>/.test(body)) return fail('Subtitle formatting or karaoke tags are not supported. Export plain text subtitles first.');
    cues.push({ id: `caption-${cues.length + 1}`, start: parseTimestamp(match[1], kind), end: parseTimestamp(match[2], kind), text: decodeText(body) });
    if (cues.length > MAX_CAPTION_CUES) return fail('A track can contain at most 200 captions.');
  }
  if (!cues.length) return fail('No timed captions were found in this file.');
  return normalizeCaptionTrack({ cues }).cues;
};

const timestamp = (time: number, separator: ',' | '.'): string => {
  const ms = millis(time);
  const pad = (n: number, length = 2): string => String(n).padStart(length, '0');
  return `${pad(Math.floor(ms / 3600000))}:${pad(Math.floor(ms / 60000) % 60)}:${pad(Math.floor(ms / 1000) % 60)}${separator}${pad(ms % 1000, 3)}`;
};
export const serializeSrt = (track: CaptionTrack): string => normalizeCaptionTrack(track).cues.map((cue, i) => `${i + 1}\n${timestamp(cue.start, ',')} --> ${timestamp(cue.end, ',')}\n${escapeText(cue.text)}\n`).join('\n');
export const serializeVtt = (track: CaptionTrack): string => `WEBVTT\n\n${normalizeCaptionTrack(track).cues.map((cue) => `${timestamp(cue.start, '.')} --> ${timestamp(cue.end, '.')}\n${escapeText(cue.text)}\n`).join('\n')}`;

/** Even spacing is an editable draft, never claimed to transcribe or align a song. */
export const draftCaptions = (lyrics: string, duration: number): CaptionCue[] => {
  if (typeof lyrics !== 'string' || lyrics.length > 256_000) return fail('Paste up to 200 short lyric lines.');
  const lines = lyrics.replace(/\r\n?/g, '\n').split('\n').filter((line) => line.trim()).map(cleanCaptionText);
  if (!lines.length) return fail('Paste at least one lyric line.');
  if (lines.length > MAX_CAPTION_CUES) return fail('A track can contain at most 200 captions.');
  if (!Number.isFinite(duration) || duration <= 0 || duration > MAX_CAPTION_TIME || millis(duration) < lines.length * 50) return fail('This take is too short for these lyric lines, or exceeds 3600 seconds.');
  return normalizeCaptionTrack({ cues: lines.map((text, i) => ({ id: `caption-${i + 1}`, text, start: millis(duration * i / lines.length) / 1000, end: millis(duration * (i + 1) / lines.length) / 1000 })) }).cues;
};

export const captionAt = (track: CaptionTrack | null | undefined, time: number): CaptionCue | null => {
  if (!Number.isFinite(time) || time < 0) return null;
  return track?.cues.find((cue) => time >= cue.start && time < cue.end) ?? null;
};

export const planCaptions = (track: CaptionTrack | null | undefined, aspect: number, measure: Measure): PlannedCaption[] => {
  if (!track?.cues.length) return [];
  return normalizeCaptionTrack(track).cues.map((cue) => {
    let ratio = 1;
    let plan = planTitle({ ...track, text: cue.text }, aspect, measure);
    // Captions cannot silently end in an ellipsis. Retain the title's shared
    // geometry and safe margins; reduce actual glyph size until every word fits.
    const splitUnicode = (p: TitlePlan): boolean => p.lines.some((line) => /[\ud800-\udbff]$|^[\udc00-\udfff]/.test(line.text));
    // The shared title wrapper hard-splits long tokens by UTF-16 units. A line
    // boundary must not turn a caption's emoji into two replacement glyphs.
    for (let step = 0; plan && (plan.truncated || splitUnicode(plan)) && step < 30; step++) {
      ratio *= 0.85;
      plan = planTitle({ ...track, text: cue.text }, aspect, (text, px) => measure(text, px * ratio));
    }
    if (!plan || plan.truncated || splitUnicode(plan)) return fail('A caption could not fit this frame. Shorten its text.');
    return { ...cue, plan: ratio === 1 ? plan : { ...plan, fontPx: plan.fontPx * ratio } };
  });
};
export const captionPlanAt = (planned: readonly PlannedCaption[] | null | undefined, time: number): TitlePlan | null => {
  if (!Number.isFinite(time) || time < 0) return null;
  return planned?.find((cue) => time >= cue.start && time < cue.end)?.plan ?? null;
};
