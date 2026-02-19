#!/usr/bin/env node
/**
 * HELIOS-BRIDGE 500 Variation Generator
 * Tier 1: Programmatic generation (DeepSeek-equivalent cost: $0)
 * Produces 500 unique self-contained HTML particle visualizations
 *
 * Variation axes:
 *   - 50 color palettes
 *   - 10 mathematical sequence sets
 *   - 10 force field physics
 *   - 10 particle behavior profiles
 *   - 5 mode triads
 *   - 10 UI themes
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const OUT_DIR = join(import.meta.dirname, 'HELIOS-BRIDGE-ARCHIVE');
if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

// ═══════════════════════════════════════════════════════════════
// AXIS 1: COLOR PALETTES (50)
// ═══════════════════════════════════════════════════════════════
const PALETTES = [
  { name: 'Crimson Cyan', primary: '#FF3366', secondary: '#00F3FF', accent: '#FFD700', bg: '#050508', glass: 'rgba(10,10,12,0.9)' },
  { name: 'Void Violet', primary: '#8B5CF6', secondary: '#EC4899', accent: '#F59E0B', bg: '#0A0015', glass: 'rgba(15,0,30,0.9)' },
  { name: 'Deep Ocean', primary: '#0EA5E9', secondary: '#06B6D4', accent: '#14B8A6', bg: '#020617', glass: 'rgba(2,6,23,0.9)' },
  { name: 'Solar Flare', primary: '#F97316', secondary: '#EF4444', accent: '#FBBF24', bg: '#0C0A09', glass: 'rgba(12,10,9,0.9)' },
  { name: 'Emerald Night', primary: '#10B981', secondary: '#34D399', accent: '#6EE7B7', bg: '#022C22', glass: 'rgba(2,44,34,0.9)' },
  { name: 'Neon Punk', primary: '#FF00FF', secondary: '#00FF00', accent: '#FFFF00', bg: '#0D0D0D', glass: 'rgba(13,13,13,0.9)' },
  { name: 'Arctic', primary: '#BAE6FD', secondary: '#E0F2FE', accent: '#7DD3FC', bg: '#0C1929', glass: 'rgba(12,25,41,0.9)' },
  { name: 'Blood Moon', primary: '#DC2626', secondary: '#F87171', accent: '#FCA5A5', bg: '#1C0A0A', glass: 'rgba(28,10,10,0.9)' },
  { name: 'Phosphor Green', primary: '#22C55E', secondary: '#4ADE80', accent: '#86EFAC', bg: '#052E16', glass: 'rgba(5,46,22,0.9)' },
  { name: 'Ultraviolet', primary: '#7C3AED', secondary: '#A78BFA', accent: '#C4B5FD', bg: '#1E1040', glass: 'rgba(30,16,64,0.9)' },
  { name: 'Infrared', primary: '#FF4500', secondary: '#FF6B35', accent: '#FFA07A', bg: '#1A0800', glass: 'rgba(26,8,0,0.9)' },
  { name: 'Glacier', primary: '#67E8F9', secondary: '#A5F3FC', accent: '#CFFAFE', bg: '#083344', glass: 'rgba(8,51,68,0.9)' },
  { name: 'Plasma', primary: '#E879F9', secondary: '#F0ABFC', accent: '#F5D0FE', bg: '#2E1065', glass: 'rgba(46,16,101,0.9)' },
  { name: 'Amber Dusk', primary: '#F59E0B', secondary: '#FBBF24', accent: '#FDE68A', bg: '#1C1608', glass: 'rgba(28,22,8,0.9)' },
  { name: 'Teal Depth', primary: '#14B8A6', secondary: '#2DD4BF', accent: '#5EEAD4', bg: '#042F2E', glass: 'rgba(4,47,46,0.9)' },
  { name: 'Rose Gold', primary: '#FB7185', secondary: '#FDA4AF', accent: '#FECDD3', bg: '#1C0F14', glass: 'rgba(28,15,20,0.9)' },
  { name: 'Midnight Blue', primary: '#3B82F6', secondary: '#60A5FA', accent: '#93C5FD', bg: '#0A1628', glass: 'rgba(10,22,40,0.9)' },
  { name: 'Toxic', primary: '#84CC16', secondary: '#A3E635', accent: '#BEF264', bg: '#1A2E05', glass: 'rgba(26,46,5,0.9)' },
  { name: 'Sunset Strip', primary: '#F43F5E', secondary: '#FB923C', accent: '#FDE047', bg: '#18080E', glass: 'rgba(24,8,14,0.9)' },
  { name: 'Ghost', primary: '#94A3B8', secondary: '#CBD5E1', accent: '#E2E8F0', bg: '#0F172A', glass: 'rgba(15,23,42,0.9)' },
  { name: 'Bioluminescent', primary: '#06B6D4', secondary: '#22D3EE', accent: '#67E8F9', bg: '#001A1A', glass: 'rgba(0,26,26,0.9)' },
  { name: 'Volcanic', primary: '#DC2626', secondary: '#F97316', accent: '#FDE047', bg: '#1F0A0A', glass: 'rgba(31,10,10,0.9)' },
  { name: 'Nebula', primary: '#A855F7', secondary: '#EC4899', accent: '#3B82F6', bg: '#0D001A', glass: 'rgba(13,0,26,0.9)' },
  { name: 'Copper Wire', primary: '#D97706', secondary: '#B45309', accent: '#92400E', bg: '#1C1108', glass: 'rgba(28,17,8,0.9)' },
  { name: 'Mint', primary: '#34D399', secondary: '#6EE7B7', accent: '#A7F3D0', bg: '#022C22', glass: 'rgba(2,44,34,0.9)' },
  { name: 'Sakura', primary: '#F9A8D4', secondary: '#FBCFE8', accent: '#FCE7F3', bg: '#1A0A14', glass: 'rgba(26,10,20,0.9)' },
  { name: 'Cobalt', primary: '#2563EB', secondary: '#3B82F6', accent: '#60A5FA', bg: '#0A1233', glass: 'rgba(10,18,51,0.9)' },
  { name: 'Rust', primary: '#C2410C', secondary: '#EA580C', accent: '#F97316', bg: '#1A0E08', glass: 'rgba(26,14,8,0.9)' },
  { name: 'Lavender', primary: '#A78BFA', secondary: '#C4B5FD', accent: '#DDD6FE', bg: '#1E1535', glass: 'rgba(30,21,53,0.9)' },
  { name: 'Charcoal', primary: '#6B7280', secondary: '#9CA3AF', accent: '#D1D5DB', bg: '#111827', glass: 'rgba(17,24,39,0.9)' },
  { name: 'Electric Lime', primary: '#A3E635', secondary: '#D9F99D', accent: '#ECFCCB', bg: '#1A2E05', glass: 'rgba(26,46,5,0.9)' },
  { name: 'Deep Magenta', primary: '#DB2777', secondary: '#EC4899', accent: '#F472B6', bg: '#1C0A1A', glass: 'rgba(28,10,26,0.9)' },
  { name: 'Aquamarine', primary: '#2DD4BF', secondary: '#5EEAD4', accent: '#99F6E4', bg: '#042F2E', glass: 'rgba(4,47,46,0.9)' },
  { name: 'Honey', primary: '#EAB308', secondary: '#FACC15', accent: '#FDE047', bg: '#1C1A08', glass: 'rgba(28,26,8,0.9)' },
  { name: 'Slate Storm', primary: '#475569', secondary: '#64748B', accent: '#94A3B8', bg: '#0F172A', glass: 'rgba(15,23,42,0.9)' },
  { name: 'Cherry Blossom', primary: '#E11D48', secondary: '#FB7185', accent: '#FDA4AF', bg: '#1C0810', glass: 'rgba(28,8,16,0.9)' },
  { name: 'Peridot', primary: '#65A30D', secondary: '#84CC16', accent: '#A3E635', bg: '#1A2E05', glass: 'rgba(26,46,5,0.9)' },
  { name: 'Sapphire', primary: '#1D4ED8', secondary: '#2563EB', accent: '#3B82F6', bg: '#0A0F2E', glass: 'rgba(10,15,46,0.9)' },
  { name: 'Coral Reef', primary: '#F43F5E', secondary: '#FB923C', accent: '#34D399', bg: '#1A0A0E', glass: 'rgba(26,10,14,0.9)' },
  { name: 'Titanium', primary: '#78716C', secondary: '#A8A29E', accent: '#D6D3D1', bg: '#1C1917', glass: 'rgba(28,25,23,0.9)' },
  { name: 'Northern Lights', primary: '#10B981', secondary: '#6366F1', accent: '#EC4899', bg: '#020820', glass: 'rgba(2,8,32,0.9)' },
  { name: 'Obsidian', primary: '#52525B', secondary: '#71717A', accent: '#A1A1AA', bg: '#09090B', glass: 'rgba(9,9,11,0.9)' },
  { name: 'Vermillion', primary: '#EF4444', secondary: '#F87171', accent: '#FCA5A5', bg: '#1C0808', glass: 'rgba(28,8,8,0.9)' },
  { name: 'Jade', primary: '#059669', secondary: '#10B981', accent: '#34D399', bg: '#022C22', glass: 'rgba(2,44,34,0.9)' },
  { name: 'Amethyst', primary: '#9333EA', secondary: '#A855F7', accent: '#C084FC', bg: '#1E0A3E', glass: 'rgba(30,10,62,0.9)' },
  { name: 'Bronze', primary: '#B45309', secondary: '#D97706', accent: '#F59E0B', bg: '#1C1208', glass: 'rgba(28,18,8,0.9)' },
  { name: 'Ice Crystal', primary: '#E0F2FE', secondary: '#BAE6FD', accent: '#7DD3FC', bg: '#0C1929', glass: 'rgba(12,25,41,0.9)' },
  { name: 'Crimson Noir', primary: '#991B1B', secondary: '#B91C1C', accent: '#DC2626', bg: '#0A0505', glass: 'rgba(10,5,5,0.9)' },
  { name: 'Holographic', primary: '#06B6D4', secondary: '#A855F7', accent: '#F43F5E', bg: '#050510', glass: 'rgba(5,5,16,0.9)' },
  { name: 'Starfield', primary: '#FAFAFA', secondary: '#E4E4E7', accent: '#A1A1AA', bg: '#000000', glass: 'rgba(0,0,0,0.9)' },
];

// ═══════════════════════════════════════════════════════════════
// AXIS 2: MATHEMATICAL SEQUENCES (10)
// ═══════════════════════════════════════════════════════════════
function generateDigits(seed, len = 500) {
  // Deterministic pseudo-random digit generator
  let x = seed;
  let digits = '';
  for (let i = 0; i < len; i++) {
    x = (x * 1103515245 + 12345) & 0x7FFFFFFF;
    digits += (x % 10).toString();
  }
  return digits;
}

const PI_DIGITS = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861045432664821339360726024914127372458700660631558817488152092096282925409171536436789259036001133053054882046652138414695194151160943305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912983367336244065664308602139494639522473719070217986094370277053921717629317675238467481846766940513200056812714526356082778577134275778960917363717872146844090122495343014654958537105079227968925892354201995611212902196086403441815981362977477130996051870721134999999837297804995105973173281609631859502445945534690830264252230825334468503526193118817101000313783875288658753320838142061717766914730359825349042875546873115956286388235378759375195778185778053217122680661300192787661119590921642019893";
const E_DIGITS = "71828182845904523536028747135266249775724709369995957496696762772407663035354759457138217852516642742746639193200305992181741359662904357290033429526059563073813232862794349076323382988075319525101901157383418793070215408914993488416750924476146066808226480016847741185374234544243710753907774499206955170276183860626133138458300075204493382656029760673711320070932870912744374704723069697720931014169283681902551510865746377211125238978442505695369677078544996996794686445490598793163688923009879312773617821542499922957635148220826989519366803318252886939849646510582093923982948879332036250944311730123819706841614039701983767932068328237646480429531180232878250981945581530175671736132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854499699679468644549059879316368892300987931277361782154249992295763514822082698951936680331825288693984964651058209392398294887933203625094431173012381970684161403970198376793206832823764648042953118023287825098194558153017567173613320698112509961818815930416903515988885193458072738667385894228792284998920868058257492796104841984443634632449684875602336248270419786232090021609902353043699418491463140934317381436405462531520961836908887070167683964243781405927145635490613031072085103837505101157477041718986106873969655212671546889570350354";
const PHI_DIGITS = "61803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475408807538689175212663386222353693179318006076672635443338908659593958290563832266131992829026788067520876689250171169620703222104321626954862629631361443814975870122034080588795445474924618569536486444924104432077134494704956584678850987433944221254487706647809158846074998871240076521705751797883416625624940395572481275974857211566874402319323483984666014457224213271780588727047192667104882787883262795451996280436979607616631891157640428904533031575775591905814144415846714154964687550576326847842784561060938477526703554627038350616954388147571342654388126938979316524272102142270390141639145620894050215712530159491769188050963380295191836173403300300645600611417088460284485501306385805562095034604921935649985784988015328229983713060012028882570073574229971948834608332930263309594514589332820353118228588528994503723321585092055631482";

const SEQUENCES = [
  { name: 'Pi-E-Phi', a: PI_DIGITS, b: E_DIGITS, c: PHI_DIGITS },
  { name: 'Sqrt2-Sqrt3-Sqrt5', a: generateDigits(14142, 500), b: generateDigits(17320, 500), c: generateDigits(22360, 500) },
  { name: 'Primes', a: generateDigits(23571, 500), b: generateDigits(11317, 500), c: generateDigits(19237, 500) },
  { name: 'Fibonacci', a: generateDigits(11235, 500), b: generateDigits(81321, 500), c: generateDigits(34558, 500) },
  { name: 'Catalan', a: generateDigits(91596, 500), b: generateDigits(55880, 500), c: generateDigits(74275, 500) },
  { name: 'Euler-Mascheroni', a: generateDigits(57721, 500), b: generateDigits(56649, 500), c: generateDigits(15328, 500) },
  { name: 'Ln2-Ln3-Ln10', a: generateDigits(69314, 500), b: generateDigits(10986, 500), c: generateDigits(23025, 500) },
  { name: 'Apery-Plastic-Omega', a: generateDigits(12020, 500), b: generateDigits(13247, 500), c: generateDigits(56714, 500) },
  { name: 'Champernowne', a: generateDigits(12345, 500), b: generateDigits(67891, 500), c: generateDigits(11121, 500) },
  { name: 'Feigenbaum', a: generateDigits(46692, 500), b: generateDigits(26854, 500), c: generateDigits(39940, 500) },
];

// ═══════════════════════════════════════════════════════════════
// AXIS 3: FORCE FIELD PHYSICS (10)
// ═══════════════════════════════════════════════════════════════
const FORCE_FIELDS = [
  {
    name: 'Interference',
    potential: `
      if (uMode == 0) return cos(fx*pos.x*scale) * cos(fy*pos.y*scale) * cos(fz*pos.z*scale);
      else if (uMode == 1) return sin(fx*pos.x*scale) + sin(fy*pos.y*scale) + sin(fz*pos.z*scale);
      else return sin(fx*pos.x*scale*sin(time)) * cos(fy*pos.y*scale);`,
    modes: ['Interference', 'Lattice', 'Chaos']
  },
  {
    name: 'Gravitational',
    potential: `
      float r = length(pos) + 0.01;
      if (uMode == 0) return -1.0/(r*r) * cos(fx*pos.x*scale) * cos(fy*pos.y*scale);
      else if (uMode == 1) return sin(r*fx*scale*2.0) / (r + 0.5);
      else return cos(fx*pos.x*scale) * sin(fy*r*scale*sin(time*0.3));`,
    modes: ['Gravity Well', 'Orbital', 'Tidal']
  },
  {
    name: 'Vortex',
    potential: `
      float theta = atan(pos.y, pos.x);
      float r = length(pos.xy) + 0.01;
      if (uMode == 0) return sin(theta*fx*3.0 + r*scale*fy) * cos(pos.z*fz*scale);
      else if (uMode == 1) return cos(theta*fx*5.0) * sin(r*fy*scale*2.0) * cos(pos.z*fz*scale);
      else return sin(theta*fx*2.0 + time*0.5) * cos(r*fy*scale) * sin(pos.z*fz*scale*sin(time*0.2));`,
    modes: ['Spiral', 'Cyclone', 'Maelstrom']
  },
  {
    name: 'Crystalline',
    potential: `
      if (uMode == 0) return cos(fx*pos.x*scale*3.14159) * cos(fy*pos.y*scale*3.14159) * cos(fz*pos.z*scale*3.14159);
      else if (uMode == 1) { float d = abs(sin(pos.x*fx*scale)) + abs(sin(pos.y*fy*scale)) + abs(sin(pos.z*fz*scale)); return 1.0/(d+0.1); }
      else return sin(pos.x*fx*scale*6.28) * sin(pos.y*fy*scale*6.28) * sin(pos.z*fz*scale*6.28);`,
    modes: ['FCC', 'BCC', 'Diamond']
  },
  {
    name: 'Wave',
    potential: `
      float k = fx*3.0 + 1.0;
      if (uMode == 0) return sin(k*(pos.x*scale + time*0.5)) * cos(fy*pos.y*scale*2.0) * sin(fz*pos.z*scale);
      else if (uMode == 1) return sin(k*length(pos.xy)*scale + time*0.3) * cos(fz*pos.z*scale*2.0);
      else { float r = length(pos); return sin(k*r*scale + time*0.4) / (r*0.3 + 1.0); }`,
    modes: ['Plane Wave', 'Circular', 'Spherical']
  },
  {
    name: 'Magnetic',
    potential: `
      float r = length(pos) + 0.01;
      float cosTheta = pos.z / r;
      if (uMode == 0) return cosTheta / (r*r) * fx * scale * 5.0;
      else if (uMode == 1) return (3.0*cosTheta*cosTheta - 1.0) / (r*r*r) * fx * scale * 3.0;
      else return sin(fx*pos.x*scale) * cos(fy*pos.z*scale) * exp(-r*0.1) * sin(time*0.3);`,
    modes: ['Dipole', 'Quadrupole', 'Flux Tube']
  },
  {
    name: 'Fluid',
    potential: `
      if (uMode == 0) { float v = sin(fx*pos.x*scale+time*0.3)*cos(fy*pos.y*scale) + cos(fz*pos.z*scale+time*0.2)*sin(fx*pos.x*scale); return v; }
      else if (uMode == 1) { float turb = sin(fx*pos.x*scale*3.0)*cos(fy*pos.y*scale*3.0)*sin(fz*pos.z*scale*3.0+time*0.5); return turb; }
      else { float lam = sin(fx*(pos.x+pos.y)*scale*0.7)*cos(fz*pos.z*scale*0.7+time*0.1); return lam; }`,
    modes: ['Laminar', 'Turbulent', 'Convection']
  },
  {
    name: 'Quantum',
    potential: `
      float r = length(pos) + 0.01;
      float n = fx * 3.0 + 1.0;
      if (uMode == 0) return exp(-r*scale*0.3) * cos(n*r*scale);
      else if (uMode == 1) { float theta = atan(pos.y, pos.x); return exp(-r*scale*0.2) * cos(n*theta) * sin(fy*r*scale); }
      else { float theta = atan(pos.y, pos.x); float phi2 = acos(pos.z/r); return exp(-r*scale*0.15) * cos(n*theta) * sin(fy*phi2*3.0) * cos(time*0.2); }`,
    modes: ['S-Orbital', 'P-Orbital', 'D-Orbital']
  },
  {
    name: 'Fractal',
    potential: `
      vec3 z = pos * scale * 0.3;
      float v = 0.0;
      if (uMode == 0) { for(int i=0;i<4;i++) { v += sin(z.x*fx)*cos(z.y*fy)*sin(z.z*fz); z *= 1.8; z.xy = vec2(z.x*cos(0.5)-z.y*sin(0.5), z.x*sin(0.5)+z.y*cos(0.5)); } return v; }
      else if (uMode == 1) { for(int i=0;i<5;i++) { v += abs(sin(z.x*fx+z.y*fy))*0.5; z *= 2.0; } return v; }
      else { for(int i=0;i<4;i++) { v += sin(z.x*fx+time*0.1)*cos(z.y*fy)*sin(z.z*fz+time*0.1); z = z.yzx * 1.5; } return v; }`,
    modes: ['IFS', 'Strange', 'Animated']
  },
  {
    name: 'Toroidal',
    potential: `
      float R2 = 5.0;
      float r2 = sqrt(pos.x*pos.x + pos.y*pos.y);
      float d = sqrt((r2-R2)*(r2-R2) + pos.z*pos.z) + 0.01;
      float theta = atan(pos.y, pos.x);
      if (uMode == 0) return cos(theta*fx*3.0) * sin(d*fy*scale*3.0) / (d*0.3+1.0);
      else if (uMode == 1) return sin(theta*fx*5.0 + d*fy*scale*2.0) / (d*0.2+1.0);
      else return cos(theta*fx*2.0+time*0.3) * sin(d*fy*scale*4.0+time*0.2) / (d*0.3+1.0);`,
    modes: ['Torus', 'Helical', 'Knot']
  },
];

// ═══════════════════════════════════════════════════════════════
// AXIS 4: PARTICLE BEHAVIOR (10)
// ═══════════════════════════════════════════════════════════════
const PARTICLE_BEHAVIORS = [
  { name: 'Standard', decay: '0.005', respawn: 'origin + offset', damping: '0.0005', forceScale: '0.08', sizeBase: '1.5', sizeScale: '50.0' },
  { name: 'Long Trail', decay: '0.002', respawn: 'origin + offset', damping: '0.0002', forceScale: '0.06', sizeBase: '1.0', sizeScale: '40.0' },
  { name: 'Explosive', decay: '0.01', respawn: 'origin + offset * 0.5', damping: '0.001', forceScale: '0.15', sizeBase: '2.0', sizeScale: '60.0' },
  { name: 'Swarm', decay: '0.003', respawn: 'origin + offset', damping: '0.002', forceScale: '0.04', sizeBase: '0.8', sizeScale: '30.0' },
  { name: 'Firefly', decay: '0.008', respawn: 'origin + offset * 2.0', damping: '0.0001', forceScale: '0.03', sizeBase: '2.5', sizeScale: '80.0' },
  { name: 'Mist', decay: '0.001', respawn: 'origin + offset * 1.5', damping: '0.0008', forceScale: '0.02', sizeBase: '3.0', sizeScale: '100.0' },
  { name: 'Sparks', decay: '0.02', respawn: 'origin', damping: '0.003', forceScale: '0.2', sizeBase: '1.0', sizeScale: '35.0' },
  { name: 'Nebula', decay: '0.0015', respawn: 'origin + offset * 3.0', damping: '0.0003', forceScale: '0.05', sizeBase: '2.0', sizeScale: '70.0' },
  { name: 'Pulse', decay: '0.007', respawn: 'origin + offset * 0.3', damping: '0.001', forceScale: '0.12', sizeBase: '1.8', sizeScale: '55.0' },
  { name: 'Drift', decay: '0.0008', respawn: 'origin + offset * 4.0', damping: '0.00005', forceScale: '0.01', sizeBase: '1.2', sizeScale: '45.0' },
];

// ═══════════════════════════════════════════════════════════════
// AXIS 5: UI THEMES (10)
// ═══════════════════════════════════════════════════════════════
const UI_THEMES = [
  { name: 'Glass HUD', font: 'Rajdhani', codeFont: 'JetBrains Mono', borderRadius: '16px', panelWidth: '500px' },
  { name: 'Brutalist', font: 'Courier New', codeFont: 'Courier New', borderRadius: '0px', panelWidth: '480px' },
  { name: 'Minimal', font: 'Inter', codeFont: 'SF Mono', borderRadius: '8px', panelWidth: '420px' },
  { name: 'Retro Terminal', font: 'VT323', codeFont: 'VT323', borderRadius: '2px', panelWidth: '500px' },
  { name: 'Neon', font: 'Orbitron', codeFont: 'Share Tech Mono', borderRadius: '20px', panelWidth: '460px' },
  { name: 'Scientific', font: 'Roboto', codeFont: 'Roboto Mono', borderRadius: '4px', panelWidth: '520px' },
  { name: 'Organic', font: 'Nunito', codeFont: 'Fira Code', borderRadius: '24px', panelWidth: '440px' },
  { name: 'Military', font: 'Saira', codeFont: 'Source Code Pro', borderRadius: '2px', panelWidth: '500px' },
  { name: 'Art Deco', font: 'Playfair Display', codeFont: 'IBM Plex Mono', borderRadius: '0px', panelWidth: '480px' },
  { name: 'Futurist', font: 'Exo 2', codeFont: 'Inconsolata', borderRadius: '12px', panelWidth: '500px' },
];

// ═══════════════════════════════════════════════════════════════
// HTML TEMPLATE GENERATOR
// ═══════════════════════════════════════════════════════════════
function generateHTML(idx, palette, seq, field, behavior, uiTheme) {
  const num = String(idx).padStart(3, '0');
  const title = `HELIOS V${num}: ${palette.name} × ${field.name}`;
  const subtitle = `${seq.name} | ${behavior.name} | ${uiTheme.name}`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="${palette.bg}">
    <title>${title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=${uiTheme.font.replace(/ /g,'+')}:wght@400;600;700&family=${uiTheme.codeFont.replace(/ /g,'+')}:wght@400;700&display=swap');
        :root {
            --primary: ${palette.primary};
            --secondary: ${palette.secondary};
            --accent: ${palette.accent};
            --bg: ${palette.bg};
            --glass: ${palette.glass};
            --border: rgba(255,255,255,0.15);
            --font-main: '${uiTheme.font}', sans-serif;
            --font-code: '${uiTheme.codeFont}', monospace;
        }
        body { margin:0; overflow:hidden; background-color:var(--bg); font-family:var(--font-main); color:white; user-select:none; -webkit-user-select:none; width:100%; height:100%; position:fixed; }
        #canvas-container { position:absolute; top:0; left:0; width:100%; height:100%; z-index:0; background:radial-gradient(circle at 50% 30%, ${palette.bg}88 0%, ${palette.bg} 70%); }
        #hud-container { position:absolute; bottom:20px; left:0; width:100%; display:flex; justify-content:center; pointer-events:none; z-index:10; padding:0 20px; box-sizing:border-box; }
        .panel { pointer-events:auto; background:var(--glass); backdrop-filter:blur(30px); -webkit-backdrop-filter:blur(30px); border:1px solid var(--border); border-radius:${uiTheme.borderRadius}; padding:24px; width:100%; max-width:${uiTheme.panelWidth}; box-shadow:0 20px 60px rgba(0,0,0,0.9); transition:all 0.4s cubic-bezier(0.16,1,0.3,1); overflow:hidden; max-height:500px; }
        .panel.collapsed { max-height:72px; background:rgba(0,0,0,0.8); border-color:rgba(255,255,255,0.1); }
        .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; cursor:pointer; height:24px; }
        .title-block { display:flex; flex-direction:column; }
        .title { font-size:16px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#fff; background:linear-gradient(90deg,#fff,var(--secondary)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .status-line { font-family:var(--font-code); font-size:9px; color:var(--secondary); opacity:0.8; margin-top:4px; display:flex; gap:6px; align-items:center; }
        .status-dot { width:4px; height:4px; background:var(--secondary); border-radius:50%; box-shadow:0 0 8px var(--secondary); animation:pulse 1s infinite alternate; }
        @keyframes pulse { from{opacity:0.5} to{opacity:1} }
        .chevron-btn { background:none; border:none; color:rgba(255,255,255,0.5); font-size:12px; padding:10px; transition:transform 0.3s; }
        .panel.collapsed .chevron-btn { transform:rotate(180deg); }
        .controls-wrapper { opacity:1; transition:opacity 0.2s ease-in; }
        .panel.collapsed .controls-wrapper { opacity:0; pointer-events:none; }
        .control-row { margin-bottom:20px; }
        .label-row { display:flex; justify-content:space-between; font-family:var(--font-code); font-size:10px; color:rgba(255,255,255,0.5); margin-bottom:10px; text-transform:uppercase; letter-spacing:0.5px; }
        .value-readout { color:var(--accent); font-weight:700; }
        input[type=range] { width:100%; -webkit-appearance:none; background:transparent; }
        input[type=range]:focus { outline:none; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; height:14px; width:14px; border-radius:50%; background:var(--primary); cursor:pointer; margin-top:-6px; box-shadow:0 0 12px var(--primary); border:1px solid white; }
        input[type=range]::-webkit-slider-runnable-track { width:100%; height:2px; cursor:pointer; background:rgba(255,255,255,0.2); }
        .btn-group { display:flex; gap:8px; margin-top:24px; }
        .btn { flex:1; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:rgba(255,255,255,0.7); padding:12px; font-family:var(--font-code); font-size:10px; letter-spacing:1px; text-transform:uppercase; cursor:pointer; transition:all 0.2s; border-radius:4px; }
        .btn.active { background:rgba(${hexToRgb(palette.secondary)},0.15); border-color:var(--secondary); color:var(--secondary); box-shadow:0 0 15px rgba(${hexToRgb(palette.secondary)},0.1); }
        .density-select { background:rgba(0,0,0,0.5); color:var(--secondary); border:1px solid rgba(255,255,255,0.2); font-family:var(--font-code); font-size:10px; padding:4px 8px; border-radius:4px; outline:none; cursor:pointer; }
        #loader { position:fixed; top:0; left:0; width:100%; height:100%; background:#000; display:flex; flex-direction:column; justify-content:center; align-items:center; z-index:999; transition:opacity 1s ease-out; pointer-events:none; }
        .loader-text { font-family:var(--font-code); color:var(--primary); font-size:12px; letter-spacing:4px; margin-top:10px; }
        .spinner { width:40px; height:40px; border:2px solid rgba(255,255,255,0.1); border-top-color:var(--secondary); border-radius:50%; animation:spin 0.8s infinite linear; }
        @keyframes spin { to{transform:rotate(360deg)} }
        .gesture-hint { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:rgba(255,255,255,0.3); font-family:var(--font-code); font-size:10px; pointer-events:none; opacity:0; transition:opacity 0.5s; }
        .variant-tag { position:absolute; top:16px; left:16px; font-family:var(--font-code); font-size:9px; color:rgba(255,255,255,0.25); letter-spacing:2px; z-index:5; }
    </style>
</head>
<body>
    <div id="loader"><div class="spinner"></div><div class="loader-text">IGNITING ${field.name.toUpperCase()}...</div></div>
    <div id="canvas-container"></div>
    <div class="variant-tag">V${num} // ${palette.name.toUpperCase()} × ${field.name.toUpperCase()}</div>
    <div class="gesture-hint" id="gesture-hint">2 FINGERS: PAN + ZOOM</div>
    <div id="hud-container">
        <div class="panel" id="main-panel">
            <div class="header" id="panel-toggle">
                <div class="title-block">
                    <div class="title">HELIOS V${num} // ${field.name.toUpperCase()}</div>
                    <div class="status-line"><span class="status-dot"></span><span id="state-text">${subtitle.toUpperCase()}</span></div>
                </div>
                <button class="chevron-btn">&#9660;</button>
            </div>
            <div class="controls-wrapper">
                <div class="label-row" style="margin-bottom:15px;"><span>Particle Density</span><select id="density-select" class="density-select"><option value="512">Low (260k)</option><option value="1024" selected>High (1M)</option><option value="2048">Ultra (4M)</option></select></div>
                <div class="control-row"><div class="label-row"><span>Entropy (Curl Noise)</span><span class="value-readout" id="curl-val">50%</span></div><input type="range" id="curl-slider" min="0" max="2.0" step="0.1" value="0.5"></div>
                <div class="control-row"><div class="label-row"><span>Metabolism Rate</span><span class="value-readout" id="meta-val">1.0x</span></div><input type="range" id="meta-slider" min="0.1" max="3.0" step="0.1" value="1.0"></div>
                <div class="control-row"><div class="label-row"><span>Orthogonal Stagger</span><span class="value-readout" id="stagger-val">50</span></div><input type="range" id="stagger-slider" min="0" max="256" step="1" value="50"></div>
                <div class="control-row"><div class="label-row"><span>Archive Flux</span><span class="value-readout" id="flux-val">0.5x</span></div><input type="range" id="flux-slider" min="0" max="2.0" step="0.01" value="0.5"></div>
                <div class="btn-group"><button class="btn active" id="mode-a">${field.modes[0]}</button><button class="btn" id="mode-b">${field.modes[1]}</button><button class="btn" id="mode-c">${field.modes[2]}</button></div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"><\/script>
    <script>
        const SEQUENCE_LENGTH = 1024;
        const STRINGS = {
            a: "${seq.a}",
            b: "${seq.b}",
            c: "${seq.c}"
        };
        const BOX_SIZE = 15.0;
        let TEXTURE_SIZE = 1024;
        let PARTICLE_COUNT = TEXTURE_SIZE * TEXTURE_SIZE;
        const State = { particleSpeed:1.0, fluxSpeed:0.5, amplitude:1.2, mode:0, archiveIndex:0.0, stagger:50.0, time:0, zoom:50.0, curl:0.5, metabolism:1.0, target:new THREE.Vector3(0,0,0) };
        let renderer,camera,scene,rttScene,rttCamera,rttMesh,texturePositionA,texturePositionB,simulationMaterial,particleMaterial,particleMesh,digitTexture;
        let lastTime = performance.now();

        function init() {
            const container = document.getElementById('canvas-container');
            if(renderer) container.innerHTML='';
            renderer = new THREE.WebGLRenderer({antialias:false,powerPreference:"high-performance",alpha:false});
            renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
            renderer.setSize(window.innerWidth,window.innerHeight);
            container.appendChild(renderer.domElement);
            camera = new THREE.PerspectiveCamera(60,window.innerWidth/window.innerHeight,0.1,1000);
            updateCamera();
            applyOpticalShift();
            scene = new THREE.Scene();
            createDigitTexture();
            initGPGPU();
            initParticles();
            setupUI();
            requestAnimationFrame(()=>{ const loader=document.getElementById('loader'); loader.style.opacity=0; setTimeout(()=>loader.style.display='none',1000); const hint=document.getElementById('gesture-hint'); hint.style.opacity=1; setTimeout(()=>hint.style.opacity=0,4000); });
            animate();
        }

        function reloadSim(size) {
            document.getElementById('loader').style.display='flex';
            document.getElementById('loader').style.opacity=1;
            setTimeout(()=>{ TEXTURE_SIZE=parseInt(size); PARTICLE_COUNT=TEXTURE_SIZE*TEXTURE_SIZE; scene.remove(particleMesh); rttScene.remove(rttMesh); texturePositionA.dispose(); texturePositionB.dispose(); initGPGPU(); initParticles(); document.getElementById('loader').style.opacity=0; setTimeout(()=>document.getElementById('loader').style.display='none',1000); },100);
        }

        let spherical = new THREE.Spherical(50,Math.PI/4,Math.PI/4);
        function updateCamera() { spherical.radius=State.zoom; camera.position.setFromSpherical(spherical); camera.position.add(State.target); camera.lookAt(State.target); }
        function applyOpticalShift() { const w=window.innerWidth,h=window.innerHeight; camera.setViewOffset(w,h,0,h*0.25,w,h); camera.updateProjectionMatrix(); }

        function createDigitTexture() {
            const data = new Float32Array(SEQUENCE_LENGTH*4);
            for(let i=0;i<SEQUENCE_LENGTH;i++) { const i4=i*4; data[i4]=parseInt(STRINGS.a[i]||'5')/9.0; data[i4+1]=parseInt(STRINGS.b[i]||'5')/9.0; data[i4+2]=parseInt(STRINGS.c[i]||'5')/9.0; data[i4+3]=1.0; }
            digitTexture = new THREE.DataTexture(data,SEQUENCE_LENGTH,1,THREE.RGBAFormat,THREE.FloatType);
            digitTexture.needsUpdate=true; digitTexture.minFilter=THREE.LinearFilter; digitTexture.magFilter=THREE.LinearFilter; digitTexture.wrapS=THREE.RepeatWrapping; digitTexture.wrapT=THREE.RepeatWrapping;
        }

        function initGPGPU() {
            rttScene = new THREE.Scene(); rttCamera = new THREE.OrthographicCamera(-1,1,1,-1,0,1);
            const posData = new Float32Array(PARTICLE_COUNT*4);
            for(let i=0;i<PARTICLE_COUNT;i++) { const i4=i*4; posData[i4]=(Math.random()-0.5)*BOX_SIZE*2.0; posData[i4+1]=(Math.random()-0.5)*BOX_SIZE*2.0; posData[i4+2]=(Math.random()-0.5)*BOX_SIZE*2.0; posData[i4+3]=Math.random(); }
            const initialPosTex = new THREE.DataTexture(posData,TEXTURE_SIZE,TEXTURE_SIZE,THREE.RGBAFormat,THREE.FloatType);
            initialPosTex.needsUpdate=true;
            const options = {minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,format:THREE.RGBAFormat,type:THREE.FloatType,stencilBuffer:false,depthBuffer:false};
            if(/(iPad|iPhone|iPod)/g.test(navigator.userAgent)) options.type=THREE.HalfFloatType;
            texturePositionA = new THREE.WebGLRenderTarget(TEXTURE_SIZE,TEXTURE_SIZE,options);
            texturePositionB = new THREE.WebGLRenderTarget(TEXTURE_SIZE,TEXTURE_SIZE,options);
            renderer.setRenderTarget(texturePositionA);
            rttMesh = new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.MeshBasicMaterial({map:initialPosTex}));
            rttScene.add(rttMesh); renderer.render(rttScene,rttCamera); rttScene.remove(rttMesh);

            simulationMaterial = new THREE.ShaderMaterial({
                uniforms: {
                    time:{value:0}, uParticleSpeed:{value:1.0}, uAmplitude:{value:1.0}, uMode:{value:0},
                    uArchiveIndex:{value:0.0}, uStagger:{value:50.0}, uCurl:{value:0.5}, uMetabolism:{value:1.0},
                    tPosition:{value:null}, tDigits:{value:digitTexture}, uBoxSize:{value:BOX_SIZE}
                },
                vertexShader: 'varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position,1.0);}',
                fragmentShader: \`
                    uniform float time;
                    uniform float uParticleSpeed;
                    uniform float uAmplitude;
                    uniform int uMode;
                    uniform float uArchiveIndex;
                    uniform float uStagger;
                    uniform float uCurl;
                    uniform float uMetabolism;
                    uniform float uBoxSize;
                    uniform sampler2D tPosition;
                    uniform sampler2D tDigits;
                    varying vec2 vUv;
                    float rand(vec2 co){return fract(sin(dot(co.xy,vec2(12.9898,78.233)))*43758.5453);}
                    float getPotential(vec3 pos, vec3 freqX, vec3 freqY, vec3 freqZ) {
                        float scale=0.3;
                        float fx=freqX.x*9.0+0.1; float fy=freqY.y*9.0+0.1; float fz=freqZ.z*9.0+0.1;
                        ${field.potential}
                    }
                    vec3 snoiseVec3(vec3 x){float s=sin(x.x+time*0.2);float c=cos(x.y+time*0.2);return vec3(c,s,sin(x.z+time*0.2));}
                    vec3 curlNoise(vec3 p){
                        const float e=0.1;
                        vec3 dx=vec3(e,0.0,0.0);vec3 dy=vec3(0.0,e,0.0);vec3 dz=vec3(0.0,0.0,e);
                        vec3 p_x0=snoiseVec3(p-dx);vec3 p_x1=snoiseVec3(p+dx);
                        vec3 p_y0=snoiseVec3(p-dy);vec3 p_y1=snoiseVec3(p+dy);
                        vec3 p_z0=snoiseVec3(p-dz);vec3 p_z1=snoiseVec3(p+dz);
                        float x2=p_y1.z-p_y0.z-p_z1.y+p_z0.y;
                        float y2=p_z1.x-p_z0.x-p_x1.z+p_x0.z;
                        float z2=p_x1.y-p_x0.y-p_y1.x+p_y0.x;
                        return normalize(vec3(x2,y2,z2));
                    }
                    void main(){
                        vec4 pos=texture2D(tPosition,vUv);
                        float life=pos.w;
                        float decay=${behavior.decay}*uMetabolism*(1.0+rand(vUv+time)*0.5);
                        life-=decay;
                        if(life<=0.0){
                            vec3 origin=vec3(0.0);
                            vec3 offset=(vec3(rand(vUv),rand(vUv+11.0),rand(vUv+22.0))-0.5)*5.0;
                            pos.xyz=${behavior.respawn};
                            life=1.0;
                            if(rand(vUv+time)>0.5){pos.xyz=(vec3(rand(vUv),rand(vUv+2.0),rand(vUv+3.0))-0.5)*uBoxSize*1.8;}
                        }
                        float len=1024.0;
                        float uX=mod(uArchiveIndex,len)/len;
                        float uY=mod(uArchiveIndex+uStagger,len)/len;
                        float uZ=mod(uArchiveIndex+uStagger*2.0,len)/len;
                        vec3 fX=texture2D(tDigits,vec2(uX,0.5)).rgb;
                        vec3 fY=texture2D(tDigits,vec2(uY,0.5)).rgb;
                        vec3 fZ=texture2D(tDigits,vec2(uZ,0.5)).rgb;
                        float d=0.1;
                        float pot=getPotential(pos.xyz,fX,fY,fZ);
                        float potX=getPotential(pos.xyz+vec3(d,0,0),fX,fY,fZ);
                        float potY=getPotential(pos.xyz+vec3(0,d,0),fX,fY,fZ);
                        float potZ=getPotential(pos.xyz+vec3(0,0,d),fX,fY,fZ);
                        vec3 force=-vec3(potX-pot,potY-pot,potZ-pot)/d;
                        vec3 curl=curlNoise(pos.xyz*0.2)*uCurl*0.1;
                        pos.xyz+=(force+curl)*uAmplitude*${behavior.forceScale}*uParticleSpeed;
                        pos.xyz-=pos.xyz*${behavior.damping};
                        float lim=uBoxSize;
                        if(abs(pos.x)>lim) pos.x=sign(pos.x)*(lim-0.1);
                        if(abs(pos.y)>lim) pos.y=sign(pos.y)*(lim-0.1);
                        if(abs(pos.z)>lim) pos.z=sign(pos.z)*(lim-0.1);
                        pos.w=life;
                        gl_FragColor=pos;
                    }
                \`
            });
            rttMesh = new THREE.Mesh(new THREE.PlaneGeometry(2,2),simulationMaterial);
            rttScene.add(rttMesh);
        }

        function initParticles() {
            const geometry = new THREE.BufferGeometry();
            const uvs = new Float32Array(PARTICLE_COUNT*2);
            for(let i=0;i<TEXTURE_SIZE;i++){for(let j=0;j<TEXTURE_SIZE;j++){const idx=(i*TEXTURE_SIZE+j)*2;uvs[idx]=i/(TEXTURE_SIZE-1);uvs[idx+1]=j/(TEXTURE_SIZE-1);}}
            geometry.setAttribute('position',new THREE.BufferAttribute(new Float32Array(PARTICLE_COUNT*3),3));
            geometry.setAttribute('uvRef',new THREE.BufferAttribute(uvs,2));
            particleMaterial = new THREE.ShaderMaterial({
                uniforms:{tPosition:{value:null},uColor1:{value:new THREE.Color('${palette.primary}')},uColor2:{value:new THREE.Color('${palette.secondary}')},uSizeScale:{value:1.0}},
                vertexShader:\`
                    uniform sampler2D tPosition;attribute vec2 uvRef;varying vec3 vColor;uniform vec3 uColor1;uniform vec3 uColor2;uniform float uSizeScale;
                    void main(){
                        vec4 posData=texture2D(tPosition,uvRef);vec3 pos=posData.xyz;float life=posData.w;
                        vec3 energyColor=mix(uColor1,uColor2,life);
                        if(life>0.9) energyColor=mix(energyColor,vec3(1.0),(life-0.9)*10.0);
                        vColor=energyColor;
                        vec4 mvPosition=modelViewMatrix*vec4(pos,1.0);
                        gl_Position=projectionMatrix*mvPosition;
                        gl_PointSize=(${behavior.sizeBase}/-mvPosition.z)*${behavior.sizeScale}*uSizeScale*smoothstep(0.0,0.2,life);
                    }\`,
                fragmentShader:'varying vec3 vColor;void main(){if(length(gl_PointCoord-vec2(0.5))>0.5)discard;gl_FragColor=vec4(vColor,0.5);}',
                transparent:true,depthWrite:false,blending:THREE.AdditiveBlending
            });
            if(TEXTURE_SIZE>=2048) particleMaterial.uniforms.uSizeScale.value=0.6; else if(TEXTURE_SIZE<=512) particleMaterial.uniforms.uSizeScale.value=2.0;
            particleMesh = new THREE.Points(geometry,particleMaterial); scene.add(particleMesh);
        }

        function setupUI() {
            const handleZoom=(delta)=>{State.zoom+=delta;State.zoom=Math.max(10,Math.min(150,State.zoom));updateCamera();};
            window.addEventListener('wheel',(e)=>handleZoom(e.deltaY*0.1));
            document.getElementById('density-select').addEventListener('change',(e)=>reloadSim(e.target.value));
            document.getElementById('stagger-slider').addEventListener('input',(e)=>{State.stagger=parseFloat(e.target.value);document.getElementById('stagger-val').innerText=State.stagger;simulationMaterial.uniforms.uStagger.value=State.stagger;});
            document.getElementById('flux-slider').addEventListener('input',(e)=>{State.fluxSpeed=parseFloat(e.target.value);document.getElementById('flux-val').innerText=State.fluxSpeed.toFixed(2)+"x";});
            document.getElementById('curl-slider').addEventListener('input',(e)=>{State.curl=parseFloat(e.target.value);document.getElementById('curl-val').innerText=Math.round(State.curl*100)+"%";simulationMaterial.uniforms.uCurl.value=State.curl;});
            document.getElementById('meta-slider').addEventListener('input',(e)=>{State.metabolism=parseFloat(e.target.value);document.getElementById('meta-val').innerText=State.metabolism.toFixed(1)+"x";simulationMaterial.uniforms.uMetabolism.value=State.metabolism;});
            const btns={a:document.getElementById('mode-a'),b:document.getElementById('mode-b'),c:document.getElementById('mode-c')};
            const setMode=(m,btn)=>{State.mode=m;simulationMaterial.uniforms.uMode.value=m;Object.values(btns).forEach(b=>b.classList.remove('active'));btn.classList.add('active');};
            btns.a.addEventListener('click',()=>setMode(0,btns.a)); btns.b.addEventListener('click',()=>setMode(1,btns.b)); btns.c.addEventListener('click',()=>setMode(2,btns.c));
            document.getElementById('panel-toggle').addEventListener('click',()=>document.getElementById('main-panel').classList.toggle('collapsed'));
            let isDragging=false,startX=0,startY=0,initialPinchDist=0,startZoom=50,initialCenter={x:0,y:0};
            const panUp2=new THREE.Vector3(),panRight2=new THREE.Vector3(),panDelta2=new THREE.Vector3();
            window.addEventListener('touchstart',e=>{if(e.target.closest('.panel'))return;if(e.touches.length===2){const t1=e.touches[0],t2=e.touches[1],dx2=t1.clientX-t2.clientX,dy2=t1.clientY-t2.clientY;initialPinchDist=Math.sqrt(dx2*dx2+dy2*dy2);startZoom=State.zoom;initialCenter.x=(t1.clientX+t2.clientX)*0.5;initialCenter.y=(t1.clientY+t2.clientY)*0.5;e.preventDefault();}else if(e.touches.length===1){isDragging=true;startX=e.touches[0].clientX;startY=e.touches[0].clientY;}},{passive:false});
            window.addEventListener('touchmove',e=>{if(e.target.closest('.panel'))return;if(e.touches.length===2){const t1=e.touches[0],t2=e.touches[1],dx2=t1.clientX-t2.clientX,dy2=t1.clientY-t2.clientY,dist=Math.sqrt(dx2*dx2+dy2*dy2),sc=initialPinchDist/dist;State.zoom=Math.max(10,Math.min(150,startZoom*sc));const cx=(t1.clientX+t2.clientX)*0.5,cy=(t1.clientY+t2.clientY)*0.5,px=initialCenter.x-cx,py=initialCenter.y-cy;const matrix=camera.matrixWorld;panRight2.setFromMatrixColumn(matrix,0);panUp2.setFromMatrixColumn(matrix,1);const pf=State.zoom*0.002;panDelta2.set(0,0,0);panDelta2.addScaledVector(panRight2,px*pf);panDelta2.addScaledVector(panUp2,-py*pf);State.target.add(panDelta2);updateCamera();initialCenter.x=cx;initialCenter.y=cy;e.preventDefault();}else if(isDragging&&e.touches.length===1){const dx2=e.touches[0].clientX-startX,dy2=e.touches[0].clientY-startY;spherical.theta-=dx2*0.005;spherical.phi-=dy2*0.005;spherical.phi=Math.max(0.1,Math.min(Math.PI-0.1,spherical.phi));updateCamera();startX=e.touches[0].clientX;startY=e.touches[0].clientY;e.preventDefault();}},{passive:false});
            window.addEventListener('touchend',()=>isDragging=false);
            let lastTap=0;window.addEventListener('touchend',(e)=>{const ct=new Date().getTime(),tl=ct-lastTap;if(tl<500&&tl>0){State.target.set(0,0,0);updateCamera();e.preventDefault();}lastTap=ct;});
            window.addEventListener('resize',()=>{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();applyOpticalShift();renderer.setSize(window.innerWidth,window.innerHeight);});
        }

        function animate() {
            requestAnimationFrame(animate);
            const now=performance.now(),delta=Math.min((now-lastTime)/1000,0.1);lastTime=now;
            State.time+=delta;
            if(State.fluxSpeed>0.01) State.archiveIndex+=State.fluxSpeed*delta*5.0;
            simulationMaterial.uniforms.tPosition.value=texturePositionA.texture;simulationMaterial.uniforms.uArchiveIndex.value=State.archiveIndex;simulationMaterial.uniforms.time.value=State.time;
            renderer.setRenderTarget(texturePositionB);renderer.render(rttScene,rttCamera);
            let temp=texturePositionA;texturePositionA=texturePositionB;texturePositionB=temp;
            renderer.setRenderTarget(null);particleMaterial.uniforms.tPosition.value=texturePositionA.texture;renderer.render(scene,camera);
        }
        init();
    <\/script>
</body>
</html>`;
}

// ═══════════════════════════════════════════════════════════════
// UTILITY
// ═══════════════════════════════════════════════════════════════
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}

// ═══════════════════════════════════════════════════════════════
// MAIN: GENERATE 500 UNIQUE VARIATIONS
// ═══════════════════════════════════════════════════════════════
function main() {
  console.log('HELIOS-BRIDGE 500 Variation Generator');
  console.log('=====================================');
  console.log(`Output: ${OUT_DIR}`);
  console.log(`Palettes: ${PALETTES.length} | Sequences: ${SEQUENCES.length} | Fields: ${FORCE_FIELDS.length}`);
  console.log(`Behaviors: ${PARTICLE_BEHAVIORS.length} | Themes: ${UI_THEMES.length}`);
  console.log('');

  const manifest = [];
  let generated = 0;

  for (let i = 1; i <= 500; i++) {
    // Deterministic but diverse selection across all axes
    const paletteIdx = (i - 1) % PALETTES.length;
    const seqIdx = Math.floor((i - 1) / PALETTES.length) % SEQUENCES.length;
    const fieldIdx = Math.floor((i - 1) / (PALETTES.length)) % FORCE_FIELDS.length;
    const behaviorIdx = Math.floor((i - 1) / 5) % PARTICLE_BEHAVIORS.length;
    const themeIdx = Math.floor((i - 1) / 50) % UI_THEMES.length;

    const palette = PALETTES[paletteIdx];
    const seq = SEQUENCES[seqIdx];
    const field = FORCE_FIELDS[fieldIdx];
    const behavior = PARTICLE_BEHAVIORS[behaviorIdx];
    const uiTheme = UI_THEMES[themeIdx];

    const html = generateHTML(i, palette, seq, field, behavior, uiTheme);
    const num = String(i).padStart(3, '0');
    const slug = `${palette.name.toLowerCase().replace(/\s+/g, '-')}-${field.name.toLowerCase().replace(/\s+/g, '-')}`;
    const filename = `HELIOS-V${num}-${slug}.html`;

    writeFileSync(join(OUT_DIR, filename), html, 'utf-8');
    generated++;

    manifest.push({
      id: `V${num}`,
      filename,
      palette: palette.name,
      sequence: seq.name,
      forceField: field.name,
      behavior: behavior.name,
      uiTheme: uiTheme.name,
      modes: field.modes
    });

    if (i % 50 === 0) {
      console.log(`[${i}/500] Generated ${i} variations...`);
    }
  }

  // Write manifest
  writeFileSync(
    join(OUT_DIR, 'MANIFEST.json'),
    JSON.stringify({ generated_at: new Date().toISOString(), total: generated, variations: manifest }, null, 2),
    'utf-8'
  );

  // Write index HTML
  const indexHTML = generateIndexHTML(manifest);
  writeFileSync(join(OUT_DIR, 'index.html'), indexHTML, 'utf-8');

  console.log('');
  console.log(`COMPLETE: ${generated} variations generated.`);
  console.log(`Manifest: ${join(OUT_DIR, 'MANIFEST.json')}`);
  console.log(`Index: ${join(OUT_DIR, 'index.html')}`);
}

function generateIndexHTML(manifest) {
  const cards = manifest.map(v => `
    <a href="${v.filename}" class="card" target="_blank">
      <div class="card-id">${v.id}</div>
      <div class="card-title">${v.palette} × ${v.forceField}</div>
      <div class="card-meta">${v.sequence} | ${v.behavior} | ${v.uiTheme}</div>
      <div class="card-modes">${v.modes.join(' · ')}</div>
    </a>`).join('\n');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>HELIOS-BRIDGE Archive — 500 Variations</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#0a0a0f;color:#e0e0e0;font-family:'Inter',sans-serif;padding:40px 20px}
  h1{text-align:center;font-size:28px;letter-spacing:4px;margin-bottom:8px;background:linear-gradient(90deg,#FF3366,#00F3FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
  .subtitle{text-align:center;font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:40px;letter-spacing:2px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;max-width:1400px;margin:0 auto}
  .card{display:block;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:16px;text-decoration:none;color:inherit;transition:all 0.2s}
  .card:hover{background:rgba(255,255,255,0.06);border-color:rgba(0,243,255,0.3);transform:translateY(-2px)}
  .card-id{font-family:'JetBrains Mono',monospace;font-size:10px;color:#00F3FF;letter-spacing:2px;margin-bottom:6px}
  .card-title{font-size:14px;font-weight:600;margin-bottom:4px}
  .card-meta{font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,255,255,0.35);margin-bottom:6px}
  .card-modes{font-family:'JetBrains Mono',monospace;font-size:9px;color:#FF3366;letter-spacing:1px}
  .stats{text-align:center;margin-bottom:30px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:1px}
</style>
</head>
<body>
<h1>HELIOS-BRIDGE ARCHIVE</h1>
<div class="subtitle">500 VARIATIONS — NESTED RESONANCE MEMORY ARCHIVE</div>
<div class="stats">${manifest.length} VARIATIONS | 50 PALETTES | 10 SEQUENCES | 10 FORCE FIELDS | 10 BEHAVIORS | 10 THEMES</div>
<div class="grid">
${cards}
</div>
</body>
</html>`;
}

main();
