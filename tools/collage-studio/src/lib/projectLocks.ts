// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only

/** A file may pin any generated cell, including cells beyond the requested
 * count. This bound protects readers from pathological indices without tying
 * the file to a generator's requested count instead of its actual geometry. */
export const MAX_PROJECT_LOCK_SLOTS = 4096;

/** Normalize the file representation of manual placement. A swap is retained
 * by its two pins, so the same representation preserves both gestures.
 *
 * Older files have no locks. Unknown sources and malformed entries cannot
 * claim a cell; repeated source IDs are valid when a composition repeats a
 * photograph. Duplicate cells follow Map's last-write-wins rule. Sorting makes
 * equivalent Maps serialize identically regardless of gesture order. */
export function normalizeProjectLocks(
  value: unknown,
  images: readonly { id: string }[],
): Array<[number, string]> {
  if (!Array.isArray(value)) return [];
  const known = new Set(images.map((image) => image.id));
  const cells = new Map<number, string>();
  for (const entry of value) {
    if (!Array.isArray(entry) || entry.length !== 2) continue;
    const [slot, id] = entry;
    if (!Number.isSafeInteger(slot) || slot < 0 || slot >= MAX_PROJECT_LOCK_SLOTS) continue;
    if (typeof id !== 'string' || !known.has(id)) continue;
    cells.set(slot === 0 ? 0 : slot, id);
  }
  return [...cells.entries()].sort(([a], [b]) => a - b);
}
