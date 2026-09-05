// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only, as the host project.
// The iframe owns execution. Only bounded image data crosses its private port.
export const ART_ROOM_PROTOCOL = 'genart-art-room/1';
export const MAX_ART_HTML_BYTES = 8 * 1024 * 1024;
export const MAX_ART_PNG_BYTES = 16 * 1024 * 1024;
export const MAX_ART_SIDE = 4096;
export const MAX_ART_PIXELS = 16_000_000;
export const ART_ROOM_SANDBOX = 'allow-scripts';
export const ART_ROOM_POLICY = [
  "default-src 'none'", "script-src 'unsafe-inline' 'unsafe-eval' blob: data:",
  "style-src 'unsafe-inline'", 'img-src blob: data:', 'font-src data:',
  'media-src blob: data:', 'connect-src blob: data:', 'worker-src blob: data:',
  "frame-src 'none'", "object-src 'none'", "form-action 'none'", "base-uri 'none'",
].join('; ');

export interface ArtCanvas {
  id: string;
  label: string;
  width: number;
  height: number;
}

export function validArtDimensions(width: unknown, height: unknown): boolean {
  return typeof width === 'number' && typeof height === 'number'
    && Number.isSafeInteger(width) && Number.isSafeInteger(height)
    && width > 0 && height > 0 && width <= MAX_ART_SIDE && height <= MAX_ART_SIDE
    && width * height <= MAX_ART_PIXELS;
}

export function artFilename(name: unknown): string {
  const clean = String(name || 'art-room').split(/[\\/]/).pop()!
    .replace(/[\u0000-\u001f\u007f<>:"|?*]/g, '_').replace(/\.[^.]*$/, '').trim().slice(0,100);
  return `${clean || 'art-room'}.png`;
}

export function validateArtSource(source: unknown): asserts source is string {
  if (typeof source !== 'string' || !source.trim()) throw new Error('This instrument is empty.');
  if (new Blob([source]).size > MAX_ART_HTML_BYTES) throw new Error('Choose an HTML instrument smaller than 8 MiB.');
  if (!/<(?:!doctype\s+html|html|head|body|script|canvas)\b/i.test(source)) throw new Error('Choose a self-contained .html art instrument.');
}

// Runs only inside the opaque child. Keep this source self-contained: no host
// closures, author callbacks or eval of data received through the port.
function bridgeSource(nonce: string): string {
  return `(() => {
    'use strict';
    const nonce = ${JSON.stringify(nonce).replace(/</g,'\\u003c')}, protocol = ${JSON.stringify(ART_ROOM_PROTOCOL)};
    let port = null, dead = false, serial = 0, capturing = false;
    const ids = new WeakMap(), canvases = new Map();
    const post = value => { if (!dead && port) { try { port.postMessage(value); } catch (_) {} } };
    function candidates() {
      const rows = []; canvases.clear();
      for (const canvas of Array.from(document.querySelectorAll('canvas')).slice(0,128)) {
        if (rows.length >= 32) break;
        const w = canvas.width, h = canvas.height, rect = canvas.getBoundingClientRect();
        if (!w || !h || w > 4096 || h > 4096 || w * h > 16000000 || rect.width <= 0 || rect.height <= 0) continue;
        let visible = true;
        for (let node = canvas; node && node.nodeType === 1; node = node.parentElement) {
          const style = getComputedStyle(node);
          if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') { visible = false; break; }
        }
        if (!visible || canvas.dataset.artReady === 'false') continue;
        // Bifurcata's completed bands have finished every crop. A partly lit
        // grove must not be advertised as a finished world capture.
        const band = canvas.closest('.band');
        if (band && !band.classList.contains('ready')) continue;
        let id = ids.get(canvas); if (!id) { id = 'canvas-' + (++serial); ids.set(canvas, id); }
        const title = canvas.dataset.artName || (band && band.dataset.seed ? 'Bifurcata world ' + band.dataset.seed : '') || canvas.getAttribute('aria-label') || canvas.id || 'Canvas ' + (rows.length + 1);
        rows.push({ id, label: String(title).slice(0,100), width:w, height:h }); canvases.set(id, canvas);
      }
      return rows;
    }
    function receive(event) {
      const m = event.data;
      if (dead || !m || typeof m !== 'object') return;
      if (m.type === 'dispose') { dead = true; try { port.close(); } catch (_) {} return; }
      if (!Number.isSafeInteger(m.id) || m.id < 1) return;
      if (m.type === 'list') { post({ id:m.id, type:'canvases', canvases:candidates() }); return; }
      if (m.type === 'focus') {
        candidates();
        const target = canvases.get(m.canvasId) || document.querySelector('.band') || document.querySelector('canvas');
        if (!target) { post({id:m.id,type:'error',message:'No artwork canvas has appeared yet. Try Show artwork after the instrument loads.'}); return; }
        target.scrollIntoView({block:'start',behavior:'auto'});
        post({id:m.id,type:'focused'}); return;
      }
      if (m.type !== 'capture') return;
      if (capturing) { post({id:m.id,type:'error',message:'Another capture is still encoding.'}); return; }
      candidates(); const canvas = canvases.get(m.canvasId);
      if (!canvas) { post({id:m.id,type:'error',message:'That canvas is not ready. Refresh the artwork list.'}); return; }
      capturing = true;
      try {
        const name = canvas.dataset.artExportName || canvas.dataset.artName || 'art-room';
        const width = canvas.width, height = canvas.height;
        canvas.toBlob(blob => {
          capturing = false;
          if (!blob || blob.size < 1 || blob.size > 16777216) { post({id:m.id,type:'error',message:'This PNG could not be captured within the 16 MiB limit.'}); return; }
          post({id:m.id,type:'image',blob,width,height,name:String(name).slice(0,140)});
        }, 'image/png');
      } catch (_) { capturing = false; post({id:m.id,type:'error',message:'This canvas cannot be read. Use an instrument with local, embedded image assets.'}); }
    }
    function boot(event) {
      if (dead || port || event.source !== parent || !event.data || event.data.protocol !== protocol || event.data.nonce !== nonce || event.data.type !== 'boot' || !event.ports[0]) return;
      port = event.ports[0]; port.onmessage = receive; port.start();
      removeEventListener('message', boot); post({type:'connected'});
    }
    addEventListener('message', boot);
    // Resource CSP does not claim to contain every browser navigation. Block
    // ordinary link/form exits; the host retires this frame if its doc reloads.
    addEventListener('click', event => { const a = event.target && event.target.closest && event.target.closest('a'); if (a && a.hasAttribute('href')) event.preventDefault(); }, true);
    addEventListener('submit', event => event.preventDefault(), true);
    window.open = () => null;
    parent.postMessage({protocol, type:'hello', nonce}, '*');
  })();`;
}

export function prepareArtInstrument(source: string, nonce: string): string {
  validateArtSource(source);
  // Install policy BEFORE the browser parses any imported bytes. Even an
  // "inert" DOMParser document can request resources; do not parse here.
  // HTML's parser ignores a second html/head/body wrapper. Imported CSP may
  // further restrict this policy but cannot relax the already active one.
  return '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="'
    + ART_ROOM_POLICY + '"><script>' + bridgeSource(nonce) + '</script></head><body>' + source + '</body></html>';
}

type Pending = { resolve: (value: any) => void; reject: (error: Error) => void; timer: ReturnType<typeof setTimeout> };

/** Owns one iframe. A replaced frame can never answer a new frame's requests. */
export class ArtRoomSession {
  readonly frame: HTMLIFrameElement;
  private nonce = crypto.randomUUID();
  private port: MessagePort | null = null;
  private dead = false;
  private ready = false;
  private sequence = 0;
  private loaded = false;
  private pending = new Map<number, Pending>();
  private helloTimer: ReturnType<typeof setTimeout>;
  private trafficAt = 0;
  private trafficCount = 0;

  constructor(mount: HTMLElement, source: string, name: string, private onReady: () => void, private onError: (message: string) => void) {
    const prepared = prepareArtInstrument(source, this.nonce);
    this.frame = document.createElement('iframe');
    this.frame.title = `${name} — Art Room instrument`;
    this.frame.setAttribute('sandbox', ART_ROOM_SANDBOX);
    this.frame.setAttribute('allow', "camera 'none'; microphone 'none'; midi 'none'; geolocation 'none'; payment 'none'; clipboard-read 'none'; clipboard-write 'none'");
    this.frame.referrerPolicy = 'no-referrer';
    this.frame.className = 'h-full w-full border-0';
    this.frame.addEventListener('load', this.onLoad);
    window.addEventListener('message', this.onHello);
    this.helloTimer = setTimeout(() => this.fail('This instrument did not connect. Try the original starter or another self-contained HTML file.'), 10_000);
    this.frame.srcdoc = prepared;
    mount.replaceChildren(this.frame);
  }

  get active(): boolean { return !this.dead; }
  get connected(): boolean { return this.ready && !this.dead; }
  private onLoad = () => {
    if (this.loaded) this.fail('The instrument navigated away. Open it again to continue.');
    this.loaded = true;
  };
  private onHello = (event: MessageEvent) => {
    if (this.dead || this.port || event.source !== this.frame.contentWindow || event.data?.protocol !== ART_ROOM_PROTOCOL || event.data?.type !== 'hello' || event.data?.nonce !== this.nonce) return;
    // The srcdoc sandbox has an opaque origin. The exact Window and nonce
    // authenticate this single transfer; all later traffic is private.
    const channel = new MessageChannel(); this.port = channel.port1;
    this.port.onmessage = this.onMessage; this.port.start();
    this.frame.contentWindow!.postMessage({ protocol: ART_ROOM_PROTOCOL, type: 'boot', nonce: this.nonce }, '*', [channel.port2]);
    window.removeEventListener('message', this.onHello);
  };
  private onMessage = (event: MessageEvent) => {
    if (this.dead) return;
    const now = performance.now();
    if (now - this.trafficAt > 1000) { this.trafficAt = now; this.trafficCount = 0; }
    if (++this.trafficCount > 60) { this.fail('The instrument sent too many messages and was closed.'); return; }
    const value = event.data;
    if (!value || typeof value !== 'object') return;
    if (value.type === 'connected' && !this.ready) { this.ready = true; clearTimeout(this.helloTimer); this.onReady(); return; }
    if (!Number.isSafeInteger(value.id)) return;
    const wait = this.pending.get(value.id); if (!wait) return;
    clearTimeout(wait.timer); this.pending.delete(value.id);
    if (value.type === 'error') wait.reject(new Error(typeof value.message === 'string' ? value.message.slice(0,200) : 'Capture failed.'));
    else wait.resolve(value);
  };
  private fail(message: string): void { if (this.dead) return; this.dispose(); this.onError(message); }
  private request(type: 'list' | 'capture' | 'focus', extra: Record<string,unknown> = {}): Promise<any> {
    if (!this.connected || !this.port) return Promise.reject(new Error('Wait for the instrument to connect.'));
    if (this.pending.size >= 3) return Promise.reject(new Error('The instrument is still working. Try again in a moment.'));
    const id = ++this.sequence;
    return new Promise((resolve,reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(type === 'capture' ? 'Capture timed out. Try again after the artwork finishes drawing.' : 'The instrument is still drawing. Refresh the artwork list.'));
      }, type === 'capture' ? 12_000 : 4_000);
      this.pending.set(id,{resolve,reject,timer});
      try { this.port!.postMessage({type,id,...extra}); }
      catch { clearTimeout(timer); this.pending.delete(id); reject(new Error('The instrument connection closed. Open it again.')); }
    });
  }
  async list(): Promise<ArtCanvas[]> {
    const value = await this.request('list');
    if (value.type !== 'canvases' || !Array.isArray(value.canvases) || value.canvases.length > 32) throw new Error('The instrument returned an invalid canvas list.');
    const seen = new Set<string>();
    return value.canvases.map((entry: any) => {
      if (!entry || typeof entry.id !== 'string' || !/^canvas-[1-9][0-9]{0,8}$/.test(entry.id) || seen.has(entry.id) || typeof entry.label !== 'string' || entry.label.length > 100 || !validArtDimensions(entry.width,entry.height)) throw new Error('The instrument returned an invalid canvas.');
      seen.add(entry.id); return {id:entry.id,label:entry.label,width:entry.width,height:entry.height};
    });
  }
  async showArtwork(canvasId?: string): Promise<void> {
    const value = await this.request('focus', {canvasId});
    if (value.type !== 'focused') throw new Error('The instrument could not show its artwork.');
  }
  async capture(canvasId: string): Promise<{blob: Blob; name: string; width: number; height: number}> {
    const value = await this.request('capture', {canvasId});
    if (value.type !== 'image' || !(value.blob instanceof Blob) || !validArtDimensions(value.width,value.height)) throw new Error('The instrument did not return a valid image.');
    return {blob:value.blob,name:artFilename(value.name),width:value.width,height:value.height};
  }
  dispose(): void {
    if (this.dead) return; this.dead = true; this.ready = false;
    clearTimeout(this.helloTimer); window.removeEventListener('message', this.onHello);
    this.frame.removeEventListener('load', this.onLoad);
    try { this.port?.postMessage({type:'dispose'}); this.port?.close(); } catch { /* retired */ }
    this.port = null;
    for (const wait of this.pending.values()) { clearTimeout(wait.timer); wait.reject(new Error('The Art Room instrument was closed.')); }
    this.pending.clear(); this.frame.remove();
  }
}

/** Check encoded dimensions BEFORE allocating browser-decoded pixels. */
export async function validateArtPng(blob: Blob): Promise<{width:number;height:number}> {
  if (!(blob instanceof Blob) || blob.type !== 'image/png' || blob.size < 33 || blob.size > MAX_ART_PNG_BYTES) throw new Error('Capture must be a PNG image smaller than 16 MiB.');
  const bytes = new Uint8Array(await blob.slice(0,33).arrayBuffer());
  if (![137,80,78,71,13,10,26,10].every((b,i) => bytes[i] === b)
    || bytes[8] !== 0 || bytes[9] !== 0 || bytes[10] !== 0 || bytes[11] !== 13
    || String.fromCharCode(...bytes.slice(12,16)) !== 'IHDR') throw new Error('The instrument returned invalid PNG bytes.');
  const view = new DataView(bytes.buffer), width = view.getUint32(16), height = view.getUint32(20);
  if (!validArtDimensions(width,height)) throw new Error('Capture must be at most 4096 pixels per side and 16 megapixels.');
  await new Promise<void>((resolve,reject) => {
    const img = new Image(), url = URL.createObjectURL(blob);
    let done = false;
    const finish = (error?: Error) => {
      if (done) return; done = true; clearTimeout(timer); img.onload = null; img.onerror = null;
      URL.revokeObjectURL(url); img.src = ''; error ? reject(error) : resolve();
    };
    const timer = setTimeout(() => finish(new Error('The PNG could not be decoded in time.')), 8_000);
    img.onload = () => finish(img.naturalWidth === width && img.naturalHeight === height ? undefined : new Error('PNG dimensions did not match the decoded artwork.'));
    img.onerror = () => finish(new Error('The browser could not decode this PNG.'));
    img.src = url;
  });
  return {width,height};
}
