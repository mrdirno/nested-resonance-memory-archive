'use strict';
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM_PATH || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-gpu-sandbox', '--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 640, height: 480 } });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  await page.addInitScript(() => { try { localStorage.setItem('resonance-chamber-v2', JSON.stringify({ particles: 65536, quality: 0.5 })); } catch (e) {} });
  await page.goto('file://' + path.resolve(__dirname, 'rc-test.html'));
  await page.waitForSelector('.boot.done', { timeout: 60000 });
  const out = await page.evaluate(() => {
    const r = window.__probe.renderer, gl = r.getContext();
    const names = ['EXT_float_blend', 'EXT_color_buffer_float', 'EXT_color_buffer_half_float', 'OES_texture_float_linear'];
    const o = {}; for (const n of names) o[n] = !!gl.getExtension(n);
    o.webgl2 = r.capabilities.isWebGL2;
    o.supported = gl.getSupportedExtensions();
    // try an actual float render target with additive blending: draw 3000 points into one texel and read back
    try {
      const T = window.THREE;
      const rt = new T.WebGLRenderTarget(4, 4, { minFilter: T.NearestFilter, magFilter: T.NearestFilter, format: T.RGBAFormat, type: T.HalfFloatType, depthBuffer: false, stencilBuffer: false });
      const n = 6000;
      const g = new T.BufferGeometry();
      g.setAttribute('position', new T.BufferAttribute(new Float32Array(n * 3), 3));
      const m = new T.ShaderMaterial({ vertexShader: 'void main(){gl_Position=vec4(-0.75,-0.75,0.0,1.0);gl_PointSize=1.0;}',
        fragmentShader: 'void main(){gl_FragColor=vec4(1.0/1024.0,0.0,0.0,1.0);}',
        blending: T.AdditiveBlending, transparent: true, depthTest: false, depthWrite: false });
      const pts = new T.Points(g, m); pts.frustumCulled = false;
      const sc = new T.Scene(); sc.add(pts);
      const cam = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1);
      r.setRenderTarget(rt); r.setClearColor(0, 0); r.clear(); r.render(sc, cam); r.setRenderTarget(null);
      const raw = new Uint16Array(4 * 4 * 4); r.readRenderTargetPixels(rt, 0, 0, 4, 4, raw);
      const h2f = x => { const s = (x & 0x8000) ? -1 : 1, e = (x & 0x7C00) >> 10, f = x & 0x3FF;
        return e === 0 ? s * Math.pow(2, -14) * (f / 1024) : e === 31 ? NaN : s * Math.pow(2, e - 15) * (1 + f / 1024); };
      o.halfSum = h2f(raw[0]) * 1024; o.halfExpect = n;
      o.glError = gl.getError();
      rt.dispose();
    } catch (e) { o.floatErr = String(e); }
    return o;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})().catch(e => { console.error('crashed:', e); process.exit(2); });
