// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// Canvas2D/OffscreenCanvas painter for the original dimensional scene values.
import type { ArtLayerSample } from './artRack';
import { buildDimensionalScene, projectDimensionalFaces, projectDimensionPoint, type DimensionalKind } from './artDimension';
type Context = CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D;
type RGB = readonly [number, number, number];
const TAU = Math.PI * 2;
const clamp = (n: number, low: number, high: number) => Math.min(high, Math.max(low, n));
const rgb = (hex: string): RGB => [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
const css = (value: RGB) => `rgb(${value.map(n => Math.round(clamp(n, 0, 255))).join(',')})`;
function inkAt(colors: RGB[], ink: number): RGB {
  const n = ((ink % colors.length) + colors.length) % colors.length, i = Math.floor(n), t = n - i;
  const a = colors[i], b = colors[(i + 1) % colors.length];
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
}

export function drawDimensionalArt(ctx: Context, sample: ArtLayerSample, colors: readonly string[], kind: DimensionalKind, seed: number, hx: number, hy: number): void {
  const scene = buildDimensionalScene(kind, sample, seed, hx, hy), inks = colors.map(rgb), alpha = ctx.globalAlpha;
  if (scene.shadow) {
    const { y, width, height, alpha: opacity } = scene.shadow;
    ctx.fillStyle = '#000000';
    for (let ring = 4; ring > 0; ring--) {
      ctx.globalAlpha = alpha * opacity / 5; ctx.beginPath();
      ctx.ellipse(0, y, width * (.6 + ring * .1), height * (.4 + ring * .15), 0, 0, TAU); ctx.fill();
    }
  }
  ctx.globalAlpha = alpha;
  ctx.lineWidth = .00065;
  for (const face of projectDimensionalFaces(scene)) {
    const base = inkAt(inks, face.ink), white = face.specular + face.rim;
    const fill = css([base[0] * face.light + 255 * white, base[1] * face.light + 255 * white, base[2] * face.light + 255 * white]);
    ctx.beginPath(); ctx.moveTo(face.points[0].x, face.points[0].y);
    for (let i = 1; i < face.points.length; i++) ctx.lineTo(face.points[i].x, face.points[i].y);
    ctx.closePath(); ctx.fillStyle = fill; ctx.fill();
    // A same-shade hairline closes antialiasing seams between adjacent faces;
    // depth and light, rather than an opaque wire grid, define the solid.
    ctx.strokeStyle = fill; ctx.stroke();
  }
  for (const line of scene.lines) {
    const projected = line.points.map(point => projectDimensionPoint(point, scene));
    ctx.beginPath(); ctx.moveTo(projected[0].x, projected[0].y);
    for (let i = 1; i < projected.length; i++) ctx.lineTo(projected[i].x, projected[i].y);
    ctx.strokeStyle = css(inkAt(inks, line.ink));
    ctx.globalAlpha = alpha * line.alpha * .15; ctx.lineWidth = line.width * 4; ctx.stroke();
    ctx.globalAlpha = alpha * line.alpha; ctx.lineWidth = line.width; ctx.stroke();
  }
  for (const star of scene.stars) {
    const point = projectDimensionPoint(star.point, scene), tail = projectDimensionPoint(star.tail, scene);
    const radius = star.radius * scene.focal / (scene.camera - star.point.z);
    const color = css(inkAt(inks, star.ink)); ctx.fillStyle = color; ctx.strokeStyle = color;
    ctx.globalAlpha = alpha * star.alpha * .35; ctx.lineWidth = Math.max(.0008, radius * .65);
    ctx.beginPath(); ctx.moveTo(tail.x, tail.y); ctx.lineTo(point.x, point.y); ctx.stroke();
    ctx.globalAlpha = alpha * star.alpha * .12; ctx.beginPath(); ctx.arc(point.x, point.y, radius * 3.5, 0, TAU); ctx.fill();
    ctx.globalAlpha = alpha * star.alpha; ctx.beginPath(); ctx.arc(point.x, point.y, radius, 0, TAU); ctx.fill();
  }
  ctx.globalAlpha = alpha;
}
