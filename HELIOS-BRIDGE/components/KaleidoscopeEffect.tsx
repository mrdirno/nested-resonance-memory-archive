/**
 * KaleidoscopeEffect — sacred-geometry n-fold symmetry over the resonance field.
 *
 * Ported from KELIBRO (persona500 "Kaleidoscope + Mandelbrot Interior" engine,
 * dedicated to Kelly Portis). Instead of folding a Mandelbrot, we fold the
 * already-rendered resonance-field texture in screen space — a single texture
 * sample + polar math per pixel. It is GPU-cheap and PERF-POSITIVE: because the
 * fold mirrors one angular wedge across the whole frame, you get the same
 * on-screen richness from FEWER particles (lower particleCount → less CPU
 * physics), so higher symmetry can run faster, not slower.
 *
 * Selections (mode), matching the KELIBRO feature page:
 *   -1 Everything (no fold) · 0 Metatron (6-fold) · 1 Octopus (8-fold)
 *    2 Cubes (4-fold) · 3 Gasket (3-fold) · 4 Spiral (curved 8-fold)
 */
import React, { useMemo, useEffect } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { EffectComposer, RenderPass, ShaderPass } from 'three-stdlib';

const FoldShader = {
  uniforms: {
    tDiffuse: { value: null as any },
    uMode: { value: -1 },
    uAspect: { value: 1 },
    uTime: { value: 0 },
    uSpin: { value: 0.0 },    // no rotation (spin removed — was dizzying)
  },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }
  `,
  fragmentShader: /* glsl */`
    precision highp float;
    uniform sampler2D tDiffuse;
    uniform int   uMode;
    uniform float uAspect;
    uniform float uTime;
    uniform float uSpin;
    varying vec2  vUv;

    const float PI = 3.14159265359;

    void main(){
      // mode -1: "Everything" — the raw resonance field, untouched
      if (uMode < 0) { gl_FragColor = texture2D(tDiffuse, vUv); return; }

      // aspect-correct, center at origin
      vec2 p = vUv - 0.5;
      p.x *= uAspect;
      float r   = length(p);
      float ang = atan(p.y, p.x) + uTime * uSpin;

      // sector per symmetry order
      float sector = PI / 4.0;                       // default / spiral base (8-fold)
      if      (uMode == 0) sector = PI / 3.0;        // Metatron  6-fold
      else if (uMode == 1) sector = PI / 4.0;        // Octopus   8-fold
      else if (uMode == 2) sector = PI / 2.0;        // Cubes     4-fold
      else if (uMode == 3) sector = 2.0 * PI / 3.0;  // Gasket    3-fold
      if (uMode == 4) ang += r * 4.0;                // Spiral twist

      // THE FOLD — mirror one wedge across the whole frame (the kaleidoscope)
      ang = abs(mod(ang, sector) - sector * 0.5);

      // reconstruct the folded sample coordinate
      vec2 fp = vec2(cos(ang), sin(ang)) * r;
      fp.x /= uAspect;
      vec2 uv = fp + 0.5;

      // mirror-clamp keeps corners (r>0.5) reading edge content (dark starfield)
      uv = abs(uv);
      if (uv.x > 1.0) uv.x = 2.0 - uv.x;
      if (uv.y > 1.0) uv.y = 2.0 - uv.y;

      gl_FragColor = texture2D(tDiffuse, uv);
    }
  `,
};

export const KaleidoscopeEffect: React.FC<{ mode: number }> = ({ mode }) => {
  const { gl, scene, camera, size } = useThree();

  const composer = useMemo(() => {
    const c = new EffectComposer(gl);
    c.addPass(new RenderPass(scene, camera));
    const fold = new ShaderPass(FoldShader);
    fold.renderToScreen = true;
    c.addPass(fold);
    return c;
  }, [gl, scene, camera]);

  useEffect(() => {
    composer.setPixelRatio(gl.getPixelRatio());
    composer.setSize(size.width, size.height);
  }, [composer, gl, size]);

  // take over the render loop (priority > 0 disables R3F's auto-render)
  useFrame((state, delta) => {
    const fold = composer.passes[1] as ShaderPass;
    fold.uniforms.uMode.value = mode;
    fold.uniforms.uAspect.value = size.width / size.height;
    fold.uniforms.uTime.value = state.clock.elapsedTime;
    composer.render(delta);
  }, 1);

  return null;
};

export const KALEIDO_MODES: { id: number; label: string; hint: string }[] = [
  { id: -1, label: 'Everything', hint: 'raw resonance field' },
  { id: 0,  label: 'Metatron',   hint: '6-fold hexagonal' },
  { id: 1,  label: 'Octopus',    hint: '8-fold octagonal' },
  { id: 2,  label: 'Cubes',      hint: '4-fold square' },
  { id: 3,  label: 'Gasket',     hint: '3-fold triangular' },
  { id: 4,  label: 'Spiral',     hint: 'curved organic' },
];
