// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// Exercise shipped helpers. The decoder seam tests its lifecycle contract;
// the browser suite must prove actual PNG decode, HTML parsing and sandboxing.
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { runInNewContext } from 'node:vm';

const temp = mkdtempSync(join(tmpdir(), 'art-room-invariants-'));
const saved = { Image: globalThis.Image,
  create: URL.createObjectURL, revoke: URL.revokeObjectURL,
  setTimeout: globalThis.setTimeout, clearTimeout: globalThis.clearTimeout };
try {
  const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
  const out = join(temp, 'artRoom.mjs');
  await esbuild.build({ entryPoints: [join(root, 'src/lib/artRoom.ts')], outfile: out,
    bundle: true, platform: 'neutral', format: 'esm', logLevel: 'silent' });
  const A = await import(pathToFileURL(out).href);

  assert.equal(A.ART_ROOM_SANDBOX, 'allow-scripts', 'opaque frame must not gain origin, navigation or device permissions');
  for (const directive of ["default-src 'none'", "frame-src 'none'", "object-src 'none'", "form-action 'none'", "base-uri 'none'"])
    assert.ok(A.ART_ROOM_POLICY.split('; ').includes(directive));
  assert.ok(!/https?:|\*/.test(A.ART_ROOM_POLICY), 'resource policy must not authorize remote hosts');

  for (const [w,h] of [[1,1], [4096,1], [1,4096], [4000,4000], [4096,3906]])
    assert.equal(A.validArtDimensions(w,h), true, `${w}×${h}`);
  for (const x of [undefined,null,false,true,'1',[],{},NaN,Infinity,-Infinity,0,-1,.5,4097,Number.MAX_SAFE_INTEGER]) {
    assert.equal(A.validArtDimensions(x,1), false);
    assert.equal(A.validArtDimensions(1,x), false);
  }
  for (const [w,h] of [[4000,4001],[4096,3907],[4096,4096]]) assert.equal(A.validArtDimensions(w,h), false);
  for (let side=1; side<=4096; side+=37) {
    const other=Math.min(4096,Math.floor(A.MAX_ART_PIXELS/side));
    assert.equal(A.validArtDimensions(side,other), true);
    assert.equal(A.validArtDimensions(side,other+1), false, 'one pixel beyond side or area budget');
  }

  assert.equal(A.artFilename('../../song.html'), 'song.png');
  assert.equal(A.artFilename('C:\\instruments\\雪と海.htm'), '雪と海.png');
  assert.equal(A.artFilename('folder/'), 'art-room.png');
  for (const input of [undefined,null,'', '\u0000<>:"|?*', '/../../a<b>.svg', 'a'.repeat(200)+'.html']) {
    const name=A.artFilename(input);
    assert.ok(name.endsWith('.png'));
    assert.ok(name.length<=104);
    assert.ok(!/[\\/\u0000-\u001f\u007f<>:"|?*]/.test(name));
  }
  for (const bad of [undefined,null,false,[],{},'', ' \n ', 'plain words', '<svg></svg>'])
    assert.throws(()=>A.validateArtSource(bad));
  for (const good of ['<canvas></canvas>', '<!doctype html><html><head></head><body></body></html>', '<SCRIPT>void 0</SCRIPT>'])
    assert.doesNotThrow(()=>A.validateArtSource(good));
  const ascii='<canvas>'+' '.repeat(A.MAX_ART_HTML_BYTES-8);
  assert.doesNotThrow(()=>A.validateArtSource(ascii));
  assert.throws(()=>A.validateArtSource(ascii+'x'), /8 MiB/);
  const unicode='<canvas>'+'é'.repeat((A.MAX_ART_HTML_BYTES-8)/2);
  assert.doesNotThrow(()=>A.validateArtSource(unicode));
  assert.throws(()=>A.validateArtSource(unicode+'x'), /8 MiB/, 'bound UTF-8 bytes, not JS string length');

  // Preparation is pure. Imported source remains only in the child document;
  // trusted policy/bootstrap must precede every byte of that source.
  const hostile='<html><head><base href="https://example.invalid"><meta http-equiv="refresh" content="0;url=https://example.invalid"></head><body><canvas></canvas></body></html>';
  for (const nonce of ['normal-nonce', '</script><script>globalThis.injected=true</script>', '\"\\\n世界\u2028\u2029']) {
    const result=A.prepareArtInstrument(hostile,nonce);
    assert.ok(result.startsWith('<!doctype html>'));
    const policy=result.indexOf('http-equiv="Content-Security-Policy"');
    const start=result.indexOf('<script>'),end=result.indexOf('</script>');
    const imported=result.indexOf(hostile);
    assert.ok(policy>0&&start>policy&&end>start&&imported>end);
    assert.ok(result.slice(0,start).includes(`content="${A.ART_ROOM_POLICY}"`));
    assert.ok(result.endsWith(hostile+'</body></html>'), 'preserve imported HTML solely after trusted bootstrap');
    const bridge=result.slice(start+8,end);
    assert.ok(!/<\/script/i.test(bridge), 'nonce must not terminate the serialized bootstrap script');
    let hello;
    const context={addEventListener(){},parent:{postMessage(value){hello=value;}},window:{}};
    runInNewContext(bridge,context,{timeout:1000});
    assert.equal(hello.nonce,nonce, 'escaping preserves exact nonce value');
    assert.equal(hello.protocol,A.ART_ROOM_PROTOCOL);
    assert.equal(hello.type,'hello');
    assert.equal(context.injected,undefined);
  }

  const original=Uint8Array.from(Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6ZAAAAABJRU5ErkJggg==','base64'));
  const png=(bytes=original,type='image/png')=>new Blob([bytes],{type});
  let allocations=0;
  globalThis.Image=class {constructor(){allocations++;throw new Error('Unexpected decode allocation');}};
  const rejectBeforeDecode=async(blob)=>{
    const count=allocations;
    await assert.rejects(()=>A.validateArtPng(blob));
    assert.equal(allocations,count, 'reject malformed headers and bounds before allocating pixels');
  };
  for(const bad of [null,{}, {type:'image/png',size:100}, png(original,''),png(original,'image/jpeg'),png(new Uint8Array(32)),png(new Uint8Array(A.MAX_ART_PNG_BYTES+1))])
    await rejectBeforeDecode(bad);
  for(let length=0;length<33;length++) await rejectBeforeDecode(png(original.slice(0,length)));
  for(let offset=0;offset<16;offset++) {
    const bytes=original.slice();bytes[offset]^=1;
    await rejectBeforeDecode(png(bytes));
  }
  const withDimensions=(w,h)=>{
    const bytes=original.slice(), view=new DataView(bytes.buffer);
    view.setUint32(16,w);view.setUint32(20,h);return bytes;
  };
  for(const [w,h] of [[0,1],[1,0],[4097,1],[1,4097],[4096,4096],[4000,4001],[0xffffffff,1]])
    await rejectBeforeDecode(png(withDimensions(w,h)));

  // Mock only the browser decoder to prove actual validation waits for its
  // verdict, checks decoded dimensions, and releases resources on every path.
  let created=0, revoked=[], mode='load', width=1,height=1,lastImage,timerId=0;
  const timers=new Map();
  URL.createObjectURL=()=>`blob:art-test-${++created}`;
  URL.revokeObjectURL=url=>revoked.push(url);
  globalThis.setTimeout=(fn,ms)=>{const id=++timerId;timers.set(id,{fn,ms});return id;};
  globalThis.clearTimeout=id=>timers.delete(id);
  globalThis.Image=class {
    constructor(){allocations++;lastImage=this;this.naturalWidth=width;this.naturalHeight=height;}
    set src(value){this.source=value;if(value&&mode!=='hang')queueMicrotask(()=>mode==='load'?this.onload?.():this.onerror?.());}
    get src(){return this.source;}
  };
  const clean=()=>{
    assert.equal(revoked.length,created);
    assert.equal(lastImage.src,'');assert.equal(lastImage.onload,null);assert.equal(lastImage.onerror,null);
    assert.equal(timers.size,0);
  };
  assert.deepEqual(await A.validateArtPng(png()),{width:1,height:1});clean();
  mode='error';await assert.rejects(()=>A.validateArtPng(png()),/decode/);clean();
  mode='load';width=2;await assert.rejects(()=>A.validateArtPng(png()),/dimensions/);clean();
  width=1;height=2;await assert.rejects(()=>A.validateArtPng(png()),/dimensions/);clean();
  height=1;mode='hang';
  const pending=A.validateArtPng(png());
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(timers.size,1);
  const [{fn,ms}]=timers.values();assert.equal(ms,8000);fn();
  await assert.rejects(()=>pending,/time/);clean();

  // Exercise the actual response validators without launching an iframe.
  const list=value=>A.ArtRoomSession.prototype.list.call({request:async()=>value});
  const row={id:'canvas-1',label:'世界 <literal>',width:960,height:960};
  assert.deepEqual(await list({type:'canvases',canvases:[row]}),[row]);
  for(const value of [{type:'image',canvases:[]},{type:'canvases',canvases:{}},
    {type:'canvases',canvases:Array.from({length:33},()=>row)},
    ...[null,{...row,id:'canvas-0'},{...row,id:'canvas-1x'},{...row,label:'x'.repeat(101)},{...row,width:'960'},{...row,height:4097}].map(bad=>({type:'canvases',canvases:[bad]})),
    {type:'canvases',canvases:[row,row]}]) await assert.rejects(()=>list(value));
  console.log('ART ROOM invariants PASS: bounds, bytes, bootstrap escaping, decode lifecycle and reply validation. Browser integration still verifies real pixels and sandboxing.');
} finally {
  if(saved.Image===undefined)delete globalThis.Image;else globalThis.Image=saved.Image;
  URL.createObjectURL=saved.create;URL.revokeObjectURL=saved.revoke;
  globalThis.setTimeout=saved.setTimeout;globalThis.clearTimeout=saved.clearTimeout;
  rmSync(temp,{recursive:true,force:true});
}
