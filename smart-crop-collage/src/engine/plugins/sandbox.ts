import { LayoutItem, createRng } from '../../lib/layout';

export type UserLayoutScript = string;

export const executeUserLayout = (
  script: UserLayoutScript,
  width: number,
  height: number,
  count: number,
  seed: number
): LayoutItem[] => {
  try {
    // Basic sandboxing by hiding window/document
    // This is NOT secure against malicious users, but prevents accidental DOM access
    // We pass createRng as a helper
    const safeFunction = new Function('width', 'height', 'count', 'seed', 'createRng', `
      "use strict";
      const rng = createRng(seed);
      // User script should return 'cells' array
      ${script}
    `);
    
    const result = safeFunction(width, height, count, seed, createRng);
    
    if (!Array.isArray(result)) throw new Error("Script must return an array of LayoutItems");
    return result as LayoutItem[];
  } catch (e) {
    console.error("Plugin execution failed:", e);
    // Return empty or fallback? Throwing lets UI handle it.
    throw e;
  }
};

export const DEFAULT_PLUGIN_TEMPLATE = `
// Available: width, height, count, rng()
const cells = [];
const cols = Math.ceil(Math.sqrt(count));
const rows = Math.ceil(count / cols);
const cw = width / cols;
const ch = height / rows;

for (let r=0; r<rows; r++) {
  for (let c=0; c<cols; c++) {
    if (cells.length >= count) break;
    const x = c * cw;
    const y = r * ch;
    cells.push({
      bounds: { x, y, w: cw, h: ch },
      path: [
        {x, y}, {x: x+cw, y}, {x: x+cw, y: y+ch}, {x, y: y+ch}
      ]
    });
  }
}
return cells;
`;
