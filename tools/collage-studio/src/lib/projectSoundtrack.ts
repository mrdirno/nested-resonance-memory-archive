// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
// Manual .collage files carry the source container, never decoded/re-encoded audio.
import type { SoundtrackSpec } from './soundtrack';

export const MAX_PROJECT_SOUNDTRACK_BYTES = 256 * 1024 * 1024;
export const PROJECT_SOUNDTRACK_PATH = 'soundtrack/original';

/** Archive metadata only: browser URLs and monitor/solo state never travel. */
export interface ProjectSoundtrack {
  version: 1;
  storageFilename: 'original';
  originalName: string;
  mimeType: string;
  sizeBytes: number;
  sha256: string;
  durationSec: number;
  muted?: boolean;
  level?: number;
  inSec?: number;
  outSec?: number;
  fadeSec?: number;
}

const FIELDS = new Set([
  'version', 'storageFilename', 'originalName', 'mimeType', 'sizeBytes', 'sha256',
  'durationSec', 'muted', 'level', 'inSec', 'outSec', 'fadeSec',
]);
const finite = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value);
const invalid = (detail: string): never => { throw new Error(`Invalid project soundtrack: ${detail}.`); };

/** No mutation or coercion: a damaged authored setting cannot become a default. */
export const normalizeProjectSoundtrack = (value: unknown): ProjectSoundtrack | null => {
  if (value === undefined) return null; // Every archive written before this field.
  if (!value || typeof value !== 'object' || Array.isArray(value)) return invalid('metadata must be an object');
  const entry = value as Record<string, unknown>;
  if (Object.keys(entry).some(key => !FIELDS.has(key))) return invalid('unknown metadata field');
  if (entry.version !== 1) return invalid('unsupported metadata version');
  if (entry.storageFilename !== 'original') return invalid('source must be the embedded original');
  if (typeof entry.originalName !== 'string' || !entry.originalName.length
    || entry.originalName.length > 1024 || entry.originalName.includes('\0')) return invalid('original filename');
  // File.type may be empty (common on mobile). Preserve that absence, as well as
  // audio or video containers imported through the music picker. It is data,
  // not permission to fetch a URL or execute the container's content.
  if (typeof entry.mimeType !== 'string' || entry.mimeType.length > 255
    || (entry.mimeType !== '' && !/^[a-z0-9!#$&^_.+-]+\/[a-z0-9!#$&^_.+-]+(?:;[\x20-\x7e]*)?$/i.test(entry.mimeType))) return invalid('original MIME type');
  if (!Number.isSafeInteger(entry.sizeBytes) || (entry.sizeBytes as number) <= 0) return invalid('original must contain bytes');
  if ((entry.sizeBytes as number) > MAX_PROJECT_SOUNDTRACK_BYTES) {
    throw new Error('The soundtrack original exceeds the 256 MiB project limit. Your work is still open; use a smaller source file.');
  }
  if (typeof entry.sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(entry.sha256)) return invalid('SHA-256 checksum');
  if (!finite(entry.durationSec) || entry.durationSec < 0) return invalid('duration');
  if (entry.muted !== undefined && typeof entry.muted !== 'boolean') return invalid('mute setting');
  if (entry.level !== undefined && (!finite(entry.level) || entry.level < 0 || entry.level > 1)) return invalid('level');
  for (const key of ['inSec', 'outSec', 'fadeSec']) {
    if (entry[key] !== undefined && (!finite(entry[key]) || entry[key] < 0)) return invalid(key);
  }
  // The editor presents a pair. A lone IN would play a trimmed range while its
  // inspector showed the whole track, so do not accept half of that decision.
  if ((entry.inSec === undefined) !== (entry.outSec === undefined)) return invalid('trim endpoints must travel together');
  if (entry.outSec !== undefined && (entry.outSec as number) <= ((entry.inSec as number | undefined) ?? 0)) return invalid('trim window');
  if (entry.inSec !== undefined && entry.durationSec > 0) {
    // Preserve tiny endpoint rounding without moving either authored value.
    // IN cannot start at the end. Unknown duration (0) is probed after restore.
    if ((entry.inSec as number) >= entry.durationSec
      || (entry.outSec as number) > entry.durationSec + 1e-6) return invalid('trim exceeds the original duration');
  }

  return {
    version: 1, storageFilename: 'original', originalName: entry.originalName,
    mimeType: entry.mimeType, sizeBytes: entry.sizeBytes as number, sha256: entry.sha256,
    durationSec: entry.durationSec,
    ...(entry.muted === undefined ? {} : { muted: entry.muted as boolean }),
    ...(entry.level === undefined ? {} : { level: entry.level as number }),
    ...(entry.inSec === undefined ? {} : { inSec: entry.inSec as number }),
    ...(entry.outSec === undefined ? {} : { outSec: entry.outSec as number }),
    ...(entry.fadeSec === undefined ? {} : { fadeSec: entry.fadeSec as number }),
  };
};

export const projectSoundtrackHash = async (bytes: Uint8Array | ArrayBuffer): Promise<string> => {
  if (!globalThis.crypto?.subtle) throw new Error('This browser cannot verify project soundtrack checksums.');
  // Typed arrays can view SharedArrayBuffer; Web Crypto requires an ordinary
  // ArrayBuffer. Copy views instead of claiming their backing store is safe.
  const input = bytes instanceof ArrayBuffer ? bytes : new Uint8Array(bytes).buffer;
  const hash = await globalThis.crypto.subtle.digest('SHA-256', input);
  return Array.from(new Uint8Array(hash), byte => byte.toString(16).padStart(2, '0')).join('');
};

export const createProjectSoundtrackMetadata = async (
  soundtrack: SoundtrackSpec, original: Blob,
): Promise<ProjectSoundtrack> => {
  // Validate size and authored values BEFORE allocating a hash input buffer.
  const meta = normalizeProjectSoundtrack({
    version: 1, storageFilename: 'original', originalName: soundtrack.name,
    mimeType: original.type, sizeBytes: original.size, sha256: '0'.repeat(64),
    durationSec: soundtrack.durationSec,
    ...(soundtrack.muted === undefined ? {} : { muted: soundtrack.muted }),
    ...(soundtrack.level === undefined ? {} : { level: soundtrack.level }),
    ...(soundtrack.inSec === undefined ? {} : { inSec: soundtrack.inSec }),
    ...(soundtrack.outSec === undefined ? {} : { outSec: soundtrack.outSec }),
    ...(soundtrack.fadeSec === undefined ? {} : { fadeSec: soundtrack.fadeSec }),
  })!;
  return { ...meta, sha256: await projectSoundtrackHash(await original.arrayBuffer()) };
};

export const verifyProjectSoundtrackBytes = async (meta: ProjectSoundtrack, bytes: Uint8Array | ArrayBuffer): Promise<void> => {
  if (bytes.byteLength !== meta.sizeBytes) return invalid('original byte count does not match');
  if (await projectSoundtrackHash(bytes) !== meta.sha256) return invalid('original checksum does not match');
};

/** The caller mints/owns the URL only after the entire archive passes preflight. */
export const restoreProjectSoundtrack = (meta: ProjectSoundtrack, url: string): SoundtrackSpec => ({
  url, name: meta.originalName, durationSec: meta.durationSec,
  ...(meta.muted === undefined ? {} : { muted: meta.muted }),
  ...(meta.level === undefined ? {} : { level: meta.level }),
  ...(meta.inSec === undefined ? {} : { inSec: meta.inSec }),
  ...(meta.outSec === undefined ? {} : { outSec: meta.outSec }),
  ...(meta.fadeSec === undefined ? {} : { fadeSec: meta.fadeSec }),
});
