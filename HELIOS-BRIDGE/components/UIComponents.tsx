
import React, { useEffect } from 'react';
import { Settings, Waves, FlaskConical, Camera, Play, Pause, RotateCcw, Hash, Fingerprint, LayoutGrid, Activity, Eye, Timer, Images, Scissors, ExternalLink, Wrench, Pipette, Zap, Snowflake, Cctv, HardHat, Hammer, Umbrella, Clapperboard, Shovel, BrickWall, Tractor, Ruler, PaintRoller, DoorClosed, Sprout, TrafficCone } from 'lucide-react';
import { SimulationState, SimulationMode, TranscendentalNumber, CameraTarget } from '../types';
import { PRIME_NUMBERS } from '../constants';
import { PRESETS } from '../presets';

interface GaStatus {
  generation: number;
  best_fitness: number;
  best_genome: number[]; // Array of phases
}

interface UIProps {
  config: SimulationState;
  setConfig: React.Dispatch<React.SetStateAction<SimulationState>>;
  activePanel: string | null;
  setActivePanel: (p: string | null) => void;
  digitRefs: any; // Passed from App
  onCameraMove: (target: CameraTarget) => void;
  onResetCamera: () => void;
  isConnected: boolean;
  tasksCompleted: number;
  gaStatus: GaStatus | null;
  showArray: boolean;
  setShowArray: (v: boolean) => void;
  setKaleidoMode?: (m: number) => void;
}

const NavItem: React.FC<{ icon: React.ReactNode, label: string, active: boolean, onClick: () => void }> = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center w-[60px] h-[60px] rounded-2xl transition-all duration-300 relative overflow-hidden group ${active ? 'bg-primary text-white shadow-[0_0_20px_rgba(124,58,237,0.5)] scale-110' : 'bg-glass text-white/70 hover:bg-white/10'}`}
  >
    <div className="z-10 flex flex-col items-center">
      {React.cloneElement(icon as React.ReactElement, { size: 24, className: 'mb-1' })}
      <span className="text-[10px] font-bold uppercase tracking-wide">{label}</span>
    </div>
    {/* Hover glow effect */}
    <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
  </button>
);

const IconButtonWithTooltip: React.FC<{ onClick: () => void, icon: React.ReactNode, label: string, colorClass: string }> = ({ onClick, icon, label, colorClass }) => (
  <div className="relative group">
    <button onClick={onClick} className={`p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors ${colorClass}`}>
      {icon}
    </button>
    <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-black/90 backdrop-blur border border-white/10 rounded text-[10px] font-bold text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl z-50">
      {label}
    </div>
  </div>
);

const Panel: React.FC<{ title: string, subtitle: string, active: boolean, onClose: () => void, children: React.ReactNode, onResetParticles?: () => void, onResetDefaults?: () => void }> = ({ title, subtitle, active, onClose, children, onResetParticles, onResetDefaults }) => {
  if (!active) return null;
  return (
    <div className="fixed bottom-[90px] left-0 md:left-10 right-0 md:right-auto md:w-[400px] w-full md:max-h-[calc(100vh-120px)] max-h-[60vh] glass-panel rounded-t-2xl md:rounded-2xl z-40 animate-in slide-in-from-bottom-10 fade-in duration-300 flex flex-col shadow-2xl">
      {/* Header - No Overflow */}
      <div className="bg-black/80 backdrop-blur-xl p-5 border-b border-white/10 z-50 flex justify-between items-start rounded-t-2xl md:rounded-t-2xl shrink-0">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">{title}</h2>
          <p className="text-xs text-white/60 font-medium">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          {onResetParticles && (
            <IconButtonWithTooltip
              onClick={onResetParticles}
              icon={<RotateCcw size={14} />}
              label="Reset Particles"
              colorClass="text-emerald-400 hover:text-emerald-300 hover:shadow-[0_0_10px_rgba(52,211,153,0.3)]"
            />
          )}
          {onResetDefaults && (
            <IconButtonWithTooltip
              onClick={onResetDefaults}
              icon={<RotateCcw size={14} />}
              label="Reset Defaults"
              colorClass="text-rose-400 hover:text-rose-300 hover:shadow-[0_0_10px_rgba(251,113,133,0.3)]"
            />
          )}
          <button onClick={onClose} className="p-2 text-white/50 hover:text-white transition-colors text-2xl leading-none ml-2">&times;</button>
        </div>
      </div>

      {/* Content - Scrollable */}
      <div className="p-5 space-y-6 overflow-y-auto flex-1 rounded-b-2xl">
        {children}

        {/* Panel Branding Footer */}
        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col items-center gap-1 opacity-80">
          <a href="https://github.com/mrdirno/nested-resonance-memory-archive" target="_blank" rel="noopener noreferrer" className="text-[10px] font-mono text-white tracking-widest hover:underline drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
            github.com/mrdirno/nested-resonance-memory-archive
          </a>
        </div>
      </div>
    </div>
  );
};

const Button: React.FC<{ children: React.ReactNode, variant?: 'primary' | 'secondary' | 'tertiary' | 'success', onClick?: () => void, className?: string }> = ({ children, variant = 'primary', onClick, className = '' }) => {
  const gradients = {
    primary: 'bg-gradient-to-br from-primary to-violet-700',
    secondary: 'bg-gradient-to-br from-secondary to-pink-600',
    tertiary: 'bg-gradient-to-br from-tertiary to-cyan-600',
    success: 'bg-gradient-to-br from-success to-emerald-600',
  };
  return (
    <button
      onClick={onClick}
      className={`w-full py-4 rounded-xl font-bold text-sm text-white shadow-lg active:scale-98 transition-transform relative overflow-hidden ${gradients[variant]} ${className}`}
    >
      <div className="relative z-10 flex items-center justify-center gap-2">{children}</div>
      <div className="absolute inset-0 bg-white/20 opacity-0 hover:opacity-100 transition-opacity" />
    </button>
  );
};


const EffectSlider: React.FC<{ label: string, value: number, onChange: (val: number) => void, max?: number }> = ({ label, value, onChange, max = 1 }) => {
  const isActive = value > 0;
  const displayValue = Math.abs(value);

  return (
    <div className={`p-3 rounded-xl border transition-all ${isActive ? 'bg-black/40 border-white/10' : 'bg-black/10 border-white/5 opacity-60'}`}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              // Toggle polarity
              if (value === 0) onChange(0.1); // Default to 10% if 0
              else onChange(value * -1);
            }}
            className={`p-1 rounded-full transition-colors ${isActive ? 'bg-primary text-white shadow-[0_0_10px_rgba(124,58,237,0.5)]' : 'bg-white/10 text-white/30 hover:bg-white/20'}`}
          >
            <Settings size={12} className={isActive ? "animate-spin-slow" : ""} />
          </button>
          <span className={`text-xs font-bold ${isActive ? 'text-white' : 'text-white/40'}`}>{label}</span>
        </div>
        <span className={`font-mono text-xs ${isActive ? 'text-primary' : 'text-white/30'}`}>{Math.round(displayValue * 100)}%</span>
      </div>
      <input
        type="range" min="0" max={max} step="0.01"
        value={displayValue}
        onChange={(e) => {
          const newVal = parseFloat(e.target.value);
          // Preserve sign if active, else just set value (which makes it active if > 0)
          // Actually, if it's disabled (negative), dragging should re-enable it (positive)
          onChange(newVal);
        }}
        className={`w-full h-1 rounded-lg appearance-none cursor-pointer ${isActive ? 'bg-white/10 accent-primary' : 'bg-white/5 accent-white/20'}`}
      />
    </div>
  );
};
// This app no longer sits at the site root, so a link written as './x/' has to be
// resolved against the root rather than against this page. SITE_ROOT is inlined
// by vite.config.ts; a plain local build is served from the root and is unchanged.
const SITE_ROOT: string = (import.meta as any).env.SITE_ROOT ?? './';
const siteHref = (href: string): string => href.replace(/^\.\//, SITE_ROOT);

/**
 * Other pages published alongside the bridge in the SAME Pages artifact.
 *
 * To add one: append an entry here AND stage its directory in
 * .github/workflows/deploy_bridge.yml. Both halves are required — an entry
 * without a staged directory is a link to a 404, which is exactly how the
 * collage tool went missing in the first place.
 *
 * hrefs are written against the SITE ROOT ('./collage/' means <root>/collage/)
 * and go through siteHref() above, so they stay right wherever this app is
 * served from, without hardcoding the domain.
 */
// The site root is now the HALO page (HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html).
// The registry the deploy checks is the Tools panel (section id="panel-tools") in that HALO page;
// this list serves the classic bridge only, which is served from archive/classic/.
const TOOLS: { name: string; href: string; blurb: string; tag?: string; icon: React.ReactNode }[] = [
  {
    name: 'Collage Studio',
    href: './collage/',
    tag: 'video',
    blurb: 'Smart-crop generative compositor. Drop in images — or a video, and pull frames straight out of it — and it finds the salient region of each, then composes them onto a live canvas.',
    icon: <Scissors size={18} />,
  },
  {
    name: 'Collage Beta',
    href: './collage-beta/',
    blurb: 'The earlier build of the compositor, kept live alongside it for comparison.',
    icon: <Images size={18} />,
  },
  {
    name: 'Bridge Archive',
    href: './archive/',
    tag: '500',
    blurb: 'Five hundred standalone particle-interference variations of this bridge, each one its own page.',
    icon: <LayoutGrid size={18} />,
  },
  {
    // V501 · HALO — the laboratory iteration of this bridge. Registered OUTSIDE the
    // 500-variation manifest (it is not a point in that 5-axis space) and gated in
    // deploy_bridge.yml's entry-point list so a rename fails the build, never a 404.
    name: 'HALO — Resonance Chamber',
    href: './archive/HELIOS-V501-halo-resonance-chamber.html',
    tag: 'V501',
    blurb: 'The newest bridge, built as a laboratory: up to 4 million particles in a spherical cavity, with instruments that test the page\u2019s own claims — a chaos meter, a memory test shown beside its control, a spectrum. Press 7 for the Lab.',
    icon: <FlaskConical size={18} />,
  },
  {
    name: 'AV Field Toolkit',
    href: './av/',
    tag: 'field',
    blurb: 'Dead-practical browser tools for AV field work — consumables list, cable & adapter list, field-report setup. Every one of them started as a wish from someone in the trade.',
    icon: <Wrench size={18} />,
  },
  {
    // TRADE #2. This entry was MISSING for the whole life of the plumbing
    // toolkit: plumbing/ shipped 2026-08-03 and was staged by deploy_bridge.yml,
    // but never registered here — so the only route to it anywhere on the site
    // was a hand-wired link inside av/index.html. Verified against the DEPLOYED
    // bundle 2026-08-04: './av/' 1 hit, './plumbing/' 0 hits. That is precisely
    // the both-halves-required invariant this file's header states, failing in
    // the direction nothing checks (staged dir with no registry entry).
    name: 'Plumbing Field Toolkit',
    href: './plumbing/',
    tag: 'field',
    blurb: 'The same toolkit, isomorphed to plumbing — supply house order to start, in the counter’s own language: size, material, configuration, unit of issue.',
    icon: <Pipette size={18} />,
  },
  {
    // TRADE #3. Registered in the SAME commit that stands the trade up — the
    // deploy now fails if a staged trade has no entry here, in both directions,
    // so this can no longer be the afterthought it was for plumbing.
    name: 'Electrical Field Toolkit',
    href: './electrical/',
    tag: 'field',
    blurb: 'Isomorphed again, to electrical — the pull list first: type what you already know you need, then tick down the forget-list of small stuff that stops a crew when it is not on the truck.',
    icon: <Zap size={18} />,
  },
  {
    // TRADE #4. Registered in the same commit that stands the trade up.
    name: 'HVAC/R Field Toolkit',
    href: './hvac/',
    tag: 'field',
    blurb: 'Isomorphed to HVAC and refrigeration — the repair recommendation first: the turnover a tech sends from the roof so the office can quote the fix without a second trip.',
    icon: <Snowflake size={18} />,
  },
  {
    // TRADE #5. Registered in the same commit that stands the trade up.
    name: 'Low-Voltage Field Toolkit',
    href: './low-voltage/',
    tag: 'field',
    blurb: 'Isomorphed to low-voltage, security and fire — the device schedule first: log every camera, reader and device as you hang it and hand the PM a clean list instead of a night in a spreadsheet.',
    icon: <Cctv size={18} />,
  },
  {
    // TRADE #6 — and the last family owed a toolkit on the ladder. Registered in
    // the same commit that stands the trade up. GC went LAST on purpose: every
    // other trade here sends its paperwork UP to the super, so building his side
    // first would have meant writing the receiving end of documents that did not
    // exist yet.
    name: 'GC & Site Super Toolkit',
    href: './gc/',
    tag: 'field',
    blurb: 'Isomorphed to whoever runs the job — the weather day first: you lost the day, so tick what it did, what it stopped and what it cost besides the hours, and send your PM one thing he can answer in a thumb before he writes the letter.',
    icon: <HardHat size={18} />,
  },
  {
    // TRADE #7 — and the FIRST one not on the original five-trade build order.
    // It was promoted by an INTERFACE EDGE found in the trades already served:
    // five of the six toolkits above name the framer / drywall crew as the party
    // they chase for backing, blocking, a wall left clear and an access panel.
    // The most-requested-of party in the whole program had no toolkit, and every
    // rough-in-request page we ship was pointing at a man with nothing.
    name: 'Framing & Drywall Field Toolkit',
    href: './framing/',
    tag: 'field',
    blurb: 'Isomorphed to the crew that closes the wall — the backing ledger first: log what went in, how high and who asked for it as it goes in, then send the come-look message this week and the proof in October, when somebody swears there is nothing behind that rock.',
    icon: <Hammer size={18} />,
  },
  {
    // TRADE #8 — the SECOND one promoted rather than inherited, by the same
    // INTERFACE MATRIX rule that promoted framing: the next family is whichever
    // unserved party the most served trades already chase. With the framer
    // served, the roofer was the highest count left — named independently by
    // electrical, HVAC and plumbing. It is also the one trade here that OWNS a
    // gate instead of racing one: everybody else is counting down to dry-in.
    name: 'Roofing Field Toolkit',
    href: './roofing/',
    tag: 'field',
    blurb: 'Isomorphed to the crew that owns dry-in — the tear-off release first: nobody opens a roof until somebody says what happens if it rains tonight, so tick who moved what, what is protected, how much you are opening and who owns the call, and send it before the first sheet comes off.',
    icon: <Umbrella size={18} />,
  },
  {
    // TRADE #9 — the first that is not a construction trade, and the first that
    // arrived as a WISH rather than off the researched ladder. A judge panel
    // narrowed it hard: not "creatives" (a photographer, a motion designer and a
    // print designer share almost no vocabulary) but the one-person shop that
    // takes a client brief, shoots, cuts and delivers against a scope with
    // revision rounds. Nothing new had to be built — the same five document
    // engines the eight construction kits run cover this trade's week wearing
    // different words.
    //
    // Clapperboard, not Camera: Cctv already carries the low-voltage kit, where a
    // camera means surveillance. A slate is the tool this trade carries, and the
    // sibling rule is that an icon is the GEAR, never the thing the trade makes.
    name: 'Creative Field Toolkit',
    href: './creative/',
    tag: 'field',
    blurb: 'Isomorphed to the people who shoot and cut — not the timeline, everything around it: paste the wall of notes the client emailed and answer every line including the ones outside the deal, or tag the "one small thing" that landed after sign-off with the delivery date attached. No price on anything, and nothing you paste leaves the browser.',
    icon: <Clapperboard size={18} />,
  },
  {
    // TRADE #10 — the THIRD promoted by the INTERFACE MATRIX rule, and the one
    // the matrix was pointing at the whole time. Concrete is the only unserved
    // receiver named by two served trades independently (the electrician's
    // sleeves/blockouts/pads/Ufer row and the plumber's sleeve-in-the-pour row),
    // and the GC's mirror row is literally "the pre-pour call". It is also the
    // EARLIEST gate in the program: five of the six gate ladders open with the
    // pour, and it is the only gate on the job that does not reopen — a wall gets
    // cut, a ceiling gets pulled, a slab gets cored. Five toolkits already ship a
    // page that asks this crew for something; until now the crew being asked had
    // nothing to walk the deck with.
    //
    // Shovel, not HardHat or Truck: the sibling rule is that an icon is the GEAR
    // the trade carries, never the thing it builds and never the site it stands
    // on. HardHat is already the GC kit and a slab has no glyph.
    name: 'Concrete Field Toolkit',
    href: './concrete/',
    tag: 'field',
    blurb: 'Isomorphed to the crew everybody else is counting down to — before-the-pour first: every sleeve, blockout, embed, anchor bolt, pad and ground another outfit owes you, with the gate each one has to beat, sent as one message per trade. Nothing on it is rated, sized or dosed; the figures are the ones you read off your own approved mix design.',
    icon: <Shovel size={18} />,
  },
  {
    // TRADE #11 — the FOURTH promoted by the INTERFACE MATRIX rule. Three served
    // kits name the mason as a receiver in their own who[] arrays (electrical
    // "Mason / CMU", plumbing "Mason", roofing "Mason / chimney"), and TWO of
    // them wrote his day into their own gate ladders in their own words:
    // electrical's "Before CMU caps out" and plumbing's "Before block goes up",
    // each carrying an ask bound to it. Twelve spec lines aimed at a crew with no
    // page to answer them on — the same condition that promoted concrete one
    // trade earlier. He OWNS that gate rather than racing it, and once a wall
    // caps and grouts, a box or a sleeve is a core bit through grout and rebar.
    //
    // BrickWall, and it breaks the sibling rule the same way the 🧱 chip does and
    // for the same measured reason: a mason's gear is a trowel, a line and a
    // story pole, none of which exists in this icon set, and Hammer is already
    // the framing kit. See masonry/trade.js.
    name: 'Masonry Field Toolkit',
    href: './masonry/',
    tag: 'field',
    blurb: 'Isomorphed to the crew two other toolkits already count their own day down to — where the wall\'s at first: wall by wall at quitting time, the course each one got to, which cells are still open and what nobody touches, sent as one message. Nothing on it is braced, rated, sized or spaced; the course is his own words and every engineered question is handed back.',
    icon: <BrickWall size={18} />,
  },
  {
    // TRADE #12, and the first promoted with the original build order exhausted.
    // BACKFILL is position #1 on THREE shipped gate ladders — electrical,
    // plumbing and GC each open their own milestone list with the dirt going
    // back — and nothing on the job publishes the date. The man on the machine
    // is the only one who has it. A trench that has been backfilled is not cut,
    // pulled or cored like a wall or a lid; it is dug again, and everything in
    // it that was right the first time comes out with it.
    //
    // Tractor, and the sibling rule HOLDS here rather than bending as it did at
    // #11: an icon is the gear the trade carries, and this trade's gear is the
    // machine. Construction was rejected — on a rack where every kit is a
    // construction trade, the generic construction glyph identifies nobody.
    name: 'Sitework Field Toolkit',
    href: './sitework/',
    tag: 'field',
    blurb: 'Isomorphed to the crew who owns the earliest gate on the job — before we close it first: run by run, what is in the ditch, what is still open, who has been told and the time the dirt goes back, sent as one message to everybody with something in it. Nothing on it is a slope, a soil class, a lift, a proctor or a locate; the trench protection and the compaction spec belong to the people who engineer them.',
    icon: <Tractor size={18} />,
  },
  {
    // TRADE #13. THE FOURTH LIST, and §TRADE EXPANSION did not name it either —
    // the same omission that let framing ship with no commons chip is why the
    // deploy asserts this one: a trade staged into the artifact with no entry
    // HERE is a whole toolkit nothing at the site root links to. The assert
    // caught it on the first push of this trade, which is the assert working.
    //
    // Ruler, and the sibling rule holds: an icon is the gear the trade carries,
    // never the thing it builds. Plank and tile ARE what it builds; the
    // STRAIGHTEDGE is the one tool on the van that decides whether the day
    // happens, because what you can see under it is the whole argument this kit
    // exists to send — and once the floor is over it, nobody can see it again.
    name: 'Flooring Field Toolkit',
    href: './flooring/',
    tag: 'field',
    blurb: 'Isomorphed to the last trade in the building, and the only one whose work permanently seals somebody else\u2019s mistake \u2014 give me the go first: the slab reads wet or the heat never ran and the super says put it in, so what you are standing on, what you measured, what your own instructions require and what it costs to sit go out in one letter that ends give me the go in writing or tell me who is fixing it. It supplies no moisture number, no flatness tolerance, no acclimation window and no product data, and it never says ready, acceptable or safe to install: your reading prints beside the limit you typed off your own pail.',
    icon: <Ruler size={18} />,
  },
  {
    // TRADE #14, and the first one found by the QUERY instead of the count.
    // The ladder's own instruction at #14 was to ask FIRST whose gate is
    // already written into other kits' vocabulary with no receiver behind it \u2014
    // and "Before paint" is a literal gate value in av's ladder, "Before it
    // goes to paint" in framing's, with paint words in TEN of thirteen kits.
    // The four-lens panel then disposed unanimously over the count's nominee
    // (doors, held for #15): nothing upstream numbers what a paint crew sends.
    //
    // PaintRoller, and the sibling rule holds: an icon is the gear the trade
    // carries, never the thing it builds. The roller is the field painter's
    // iron; the artist's palette is a different trade's glyph, and the walls
    // this kit serves are nobody's canvas.
    name: 'Painting Field Toolkit',
    href: './painting/',
    tag: 'field',
    blurb: 'Isomorphed to the last trade through every room, whose first coat seals the substrate as accepted and whose finish every later ladder lands on \u2014 not ready first: walk the rooms before the crew sets up, name what stops paint in your own words with your readings beside your own limits, and send the two-button ask \u2014 fix it, or direct me in writing to coat it as it sits. It supplies no spread rate, no film build, no recoat time, no moisture threshold and no color, never says a surface was ready or a color matched, and the punch list and the finish schedule stay whoever\u2019s they already are.',
    icon: <PaintRoller size={18} />,
  },
  {
    // TRADE #15, and the first one that had already LOST TWICE. Doors took one
    // first-place vote at #13 and four keeps at #14, both times beaten by the
    // same objection: the schedule and the hardware sets are owned and NUMBERED
    // upstream. The #14 entry recorded that what it needed next was not another
    // hearing but a kit concept that survives its own kill \u2014 every page scoped
    // to what the INSTALLER SENDS. Four lenses re-ran it: two ranked it first,
    // none killed it, and the two candidates it was tied with on receiver count
    // (fire sprinkler, structural steel) were both ruled poisoned on the safety
    // rail. It is the top BUILDABLE nominee on the rack, which is a different
    // and better claim than the most-mentioned one.
    //
    // DoorClosed, and the sibling rule bends here by necessity: the hub is named
    // for the SCOPE the bid package uses, because this trade may not have a job
    // title its own people agree on \u2014 a recorded risk, not a solved one. The
    // page-level chip is a screwdriver, which IS gear he carries.
    name: 'Doors & Hardware Field Toolkit',
    href: './doors/',
    tag: 'field',
    blurb: 'Isomorphed to the crew five other kits already name and none of them could reach \u2014 the man who sets the frames, hangs the leaves and puts the hardware on. Before they ship first: walk the openings with a tape before frames get welded and send the distributor what the field actually is, the hand it really swings and the wall you really have. It supplies no fire label value, no clearance or undercut, no closer setting, no hardware set and no keying, it never says an opening is complete or compliant, and the architect\u2019s door schedule stays his \u2014 an opening number here is an address, never a second copy of his document.',
    icon: <DoorClosed size={18} />,
  },
  {
    // TRADE #16, and the first one the panel had to find OFF the rack. The
    // who[] count and the gate-vocabulary query came back with nothing left
    // standing below the safety rail, so the shortlist was written to include
    // the COUNT-INVISIBLE \u2014 and four independent lenses (field hand, population,
    // doctrine, boundary) put landscape first on all four, vetoed by none.
    // Three shipped kits had already built this man a receiver chip (concrete,
    // sitework, gc) and not one could write him a line; concrete's own pre-pour
    // ask says his sentence for him and had to aim it at the plumber.
    //
    // Sprout, and the sibling rule bends the way masonry's brick bends it: an
    // icon is the gear the trade carries, never the thing it builds \u2014 and the
    // seedling is the MATERIAL that comes off the nursery truck by the hundred,
    // tagged and counted against a slip, not the finished landscape.
    name: 'Landscape & Irrigation Field Toolkit',
    href: './landscape/',
    tag: 'field',
    blurb: 'Isomorphed to the crew three other kits already name and none of them could reach \u2014 the one that puts the pipe in, grades it, plants it and turns the clock on. Where I cross first: walk every place your pipe has to get under somebody else\u2019s concrete before it closes and send it to whoever\u2019s pouring, in your words, with the sleeve you\u2019re putting in off your own submittal. It supplies no run time, no rate, no pipe size, no backflow test and no plant call, it never says a landscape is established, and the plant list and the irrigation design stay whoever\u2019s they already are \u2014 a line off their schedule here is an address, never a second copy of their document.',
    icon: <Sprout size={18} />,
  },
  {
    // TRADE #17 (C3706). A four-lens panel over nine count-invisible candidates
    // put paving & striping first on two lenses and second on the other two,
    // vetoed by none (70 · 70 · 62 · 78). The rack had already built him two
    // receiver chips and one letter — landscape's "walk my sleeves before the
    // base rolls" aimed at `paving`, sitework's orphan "Paving / base" — and
    // "before you pave" is the one irreversible gate word on the site rack no
    // hub owned. The doctrine dissent is the design: the layout page quotes the
    // sheet and his tape and never carries a stall count or a dimension.
    //
    // A traffic cone is GEAR: the thing he sets by the dozen to close a
    // section, not the mat he lays. The sibling rule holds without bending.
    name: 'Paving & Striping Field Toolkit',
    href: './paving/',
    tag: 'field',
    blurb: 'Isomorphed to the crew two other kits already name and neither could reach — the one that reads the base, lays the mat and paints the lot. Doesn’t Fit first: the striping sheet quoted against what the tape found, row by row, before paint. Then what’s under the mat before it rolls, the lot not ready to pave, and the section closed tonight.',
    icon: <TrafficCone size={18} />,
  },
];

export const UIOverlay: React.FC<UIProps> = (props) => {
  const { config, setConfig, activePanel, setActivePanel, digitRefs, onCameraMove, onResetCamera, isConnected, tasksCompleted, gaStatus } = props;
  const [lockEnergy, setLockEnergy] = React.useState(false);

  // Helper to update sliders without lag
  const handleRange = (key: keyof SimulationState, val: number) => {
    setConfig(prev => ({ ...prev, [key]: val }));
  };

  return (
    <>
      {/* App Header & Branding */}
      <div className="fixed top-0 left-0 w-full h-[100px] flex flex-col items-center justify-center z-20 pointer-events-none bg-gradient-to-b from-black/90 to-transparent pt-2">
        <h1 className="text-3xl md:text-4xl font-black uppercase tracking-tighter text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">
          HELIOS <span className="text-white/30 font-light">|</span> BRIDGE
        </h1>
        <div className="mt-2 pointer-events-auto flex flex-col items-center">
          <a href="https://github.com/mrdirno/nested-resonance-memory-archive" target="_blank" rel="noopener noreferrer" className="text-xs md:text-sm font-mono font-bold tracking-widest text-white hover:text-white/80 transition-colors drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]">
            github.com/mrdirno/nested-resonance-memory-archive
          </a>
          <a href={siteHref('./archive/HELIOS-V501-halo-resonance-chamber.html')} target="_blank" rel="noopener noreferrer" title="Open the Resonance Chamber (V501 · HALO) in a new tab" className="mt-1 text-[10px] md:text-xs font-mono font-bold tracking-widest text-tertiary hover:text-white transition-colors drop-shadow-[0_0_10px_rgba(0,0,0,0.9)]">
            V501 · HALO — RESONANCE CHAMBER ↗
          </a>
        </div>
      </div>

      {/* Controls Panel */}
      <Panel
        title="System Controls"
        subtitle="Configure potential field dynamics"
        active={activePanel === 'controls'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          speed: 1,
          quality: 1,
          amplitude: 1,
          exposure: 0.5,
          particleCount: 100000
        }))}
      >
        <div className="flex gap-3">
          <Button onClick={() => setConfig(c => ({ ...c, isPlaying: !c.isPlaying }))}>
            {config.isPlaying ? <Pause size={18} /> : <Play size={18} />}
            {config.isPlaying ? 'PAUSE' : 'RESUME'}
          </Button>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            <RotateCcw size={18} /> RELOAD APP
          </Button>
        </div>

        {/* Phase Duration Slider */}
        <div className="bg-white/5 p-3 rounded-xl border border-white/10">
          <div className="flex justify-between text-sm font-bold mb-2 text-white/80">
            <span className="flex items-center gap-2"><Timer size={14} /> Phase Duration</span>
            <span className="font-mono text-primary">{(1000 / config.speed).toFixed(0)} ms</span>
          </div>
          <input
            type="range" min="16" max="3000" step="10"
            value={1000 / config.speed}
            onChange={(e) => handleRange('speed', 1000 / parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-[10px] text-white/40 mt-1 uppercase font-bold">
            <span>Fast (16ms)</span>
            <span>Slow (3s)</span>
          </div>
        </div>

        <div className="flex gap-2 p-1 bg-black/30 rounded-xl border border-white/5">
          {[1, 5, 15].map(s => (
            <button
              key={s}
              onClick={() => setConfig(c => ({ ...c, speed: s }))}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition ${config.speed === s ? 'bg-tertiary text-black shadow-lg' : 'text-white/50 hover:text-white'}`}
            >
              {s === 1 ? 'SLOW' : s === 5 ? 'FAST' : 'ULTRA'}
            </button>
          ))}
        </div>

        <div className="space-y-5 mt-2">
          {/* The Reality Slider */}
          <div className="bg-white/5 p-3 rounded-xl border border-white/10">
            <div className="flex justify-between text-sm font-bold mb-2 text-secondary">
              <span className="flex items-center gap-2"><Eye size={14} /> Existence Threshold</span>
              <span className="font-mono">{config.exposure.toFixed(2)}</span>
            </div>
            <input
              type="range" min="0.0" max="3.0" step="0.05"
              value={config.exposure}
              onChange={(e) => handleRange('exposure', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-[10px] text-white/40 mt-1 uppercase font-bold">
              <span>Void</span>
              <span>Reality</span>
              <span>Overload</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Particle Density</span>
              <span className="text-primary font-mono">{config.particleCount.toLocaleString()}</span>
            </div>
            <input
              type="range" min="10000" max="1000000" step="10000"
              value={config.particleCount}
              onChange={(e) => handleRange('particleCount', parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Visual Quality</span>
              <span className="text-primary font-mono">{config.quality.toFixed(1)}x</span>
            </div>
            <input
              type="range" min="0.1" max="2.0" step="0.1"
              value={config.quality}
              onChange={(e) => handleRange('quality', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Field Amplitude</span>
              <span className="text-primary font-mono">{config.amplitude.toFixed(1)}x</span>
            </div>
            <input
              type="range" min="0.1" max="100" step="0.1"
              value={config.amplitude}
              onChange={(e) => handleRange('amplitude', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          {Object.values(SimulationMode).map(mode => (
            <button
              key={mode}
              onClick={() => setConfig(c => ({ ...c, mode }))}
              className={`py-3 rounded-xl text-xs font-bold uppercase border transition-all ${config.mode === mode ? 'bg-success/20 border-success text-success' : 'bg-black/30 border-transparent text-white/60'}`}
            >
              {mode}
            </button>
          ))}
        </div>
      </Panel>

      {/* Waves Panel */}
      <Panel
        title="Potential Field"
        subtitle="2500-digit sequences driving Ψ(r,t)"
        active={activePanel === 'waves'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          mapping: { a: TranscendentalNumber.PHI, b: TranscendentalNumber.PHI, c: TranscendentalNumber.PI },
          stagger: { a: 0, b: 239, c: 478 }
        }))}
      >
        <div className="relative overflow-hidden rounded-xl bg-black/50 border border-white/10 p-4 font-mono text-sm leading-relaxed">
          {/* The gradient background for wave display */}
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 via-secondary/20 to-tertiary/20 opacity-50 animate-pulse" />
          <div className="relative z-10 space-y-2">
            <div className="flex items-center gap-3">
              <span className="text-primary font-bold w-6">A:</span>
              <span ref={digitRefs.m} className="bg-primary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(124,58,237,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence A...</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-secondary font-bold w-6">B:</span>
              <span ref={digitRefs.n} className="bg-secondary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(236,72,153,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence B...</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-tertiary font-bold w-6">C:</span>
              <span ref={digitRefs.p} className="bg-tertiary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(6,182,212,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence C...</span>
            </div>
          </div>
        </div>

        <div className="bg-black/30 rounded-xl p-4 border border-white/5 space-y-4">
          <div className="text-sm font-bold text-tertiary mb-2">Transcendental Mapping</div>
          {['a', 'b', 'c'].map(dim => (
            <div key={dim} className="flex justify-between items-center">
              <span className="uppercase text-xs font-bold text-white/70">Dimension {dim}</span>
              <select
                value={config.mapping[dim as keyof typeof config.mapping]}
                onChange={(e) => setConfig(c => ({ ...c, mapping: { ...c.mapping, [dim]: e.target.value } }))}
                className="bg-black border border-white/20 rounded px-3 py-1 text-xs text-white outline-none focus:border-primary"
              >
                {Object.values(TranscendentalNumber).map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
              </select>
            </div>
          ))}
        </div>

        <div className="bg-black/30 rounded-xl p-4 border border-white/5">
          <div className="flex justify-between text-sm font-bold mb-2">
            <span>Prime Spacing</span>
            <span className="text-primary">{config.stagger.b}</span>
          </div>
          <input
            type="range" min="0" max={PRIME_NUMBERS.length - 1}
            onChange={(e) => {
              const val = PRIME_NUMBERS[parseInt(e.target.value)];
              setConfig(c => ({ ...c, stagger: { a: 0, b: val, c: val * 2 } }));
            }}
            className="w-full"
          />
          <div className="mt-4 grid grid-cols-2 gap-3 text-center">
            <div className="bg-white/5 rounded p-2">
              <div className="text-[10px] uppercase text-white/50">Total Energy</div>
              <div ref={digitRefs.energy} className="text-xl font-mono font-bold text-secondary">0</div>
            </div>
            <div className="bg-white/5 rounded p-2">
              <div className="text-[10px] uppercase text-white/50">Cycle Pos</div>
              <div ref={digitRefs.pos} className="text-xl font-mono font-bold text-primary">0</div>
            </div>
          </div>
        </div>
      </Panel>

      {/* Labs Panel */}
      <Panel
        title="Research Labs"
        subtitle="Advanced N-particle dynamics experiments"
        active={activePanel === 'labs'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          extensions: {
            crystal: { threeFold: 0, sixFold: 0, lattice: 0 },
            harmonic: { commaSpiral: 0, perfectFifths: 0, equalTemp: 0 },
            topology: { trefoil: 0, torus: 0, hopf: 0 }
          }
        }))}
      >
        {/* V501 · HALO — the laboratory iteration of this bridge, its own page */}
        <a
          href={siteHref('./archive/HELIOS-V501-halo-resonance-chamber.html')}
          target="_blank"
          rel="noopener noreferrer"
          className="group flex items-start gap-3 w-full p-4 mb-4 rounded-xl bg-tertiary/10 border border-tertiary/30 hover:border-tertiary/60 hover:bg-tertiary/20 transition-colors active:scale-[0.99]"
        >
          <div className="shrink-0 mt-0.5 text-tertiary"><FlaskConical size={18} /></div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white">Open the Resonance Chamber</span>
              <span className="shrink-0 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-tertiary/20 text-tertiary">V501 · HALO</span>
            </div>
            <p className="text-xs text-white/60 leading-relaxed mt-1">The newest bridge, built as a laboratory: up to 4 million particles with instruments that test the page’s own claims. Opens in a new tab — press 7 for the Lab.</p>
          </div>
          <ExternalLink size={14} className="shrink-0 mt-1 text-white/30 group-hover:text-tertiary transition-colors" />
        </a>
        {/* Presets Dropdown */}
        <div className="bg-white/5 p-3 rounded-xl border border-white/10 mb-4">
          <div className="flex justify-between items-center mb-2">
            <div className="text-xs font-bold text-white/60 uppercase tracking-wider">Quick Load Presets</div>
            <div className="relative group">
              <button
                onClick={() => setLockEnergy(!lockEnergy)}
                className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] font-bold uppercase transition-colors ${lockEnergy ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-white/5 text-white/40 border border-white/10 hover:bg-white/10'}`}
              >
                {lockEnergy ? <React.Fragment>🔒 Locked</React.Fragment> : <React.Fragment>🔓 Unlocked</React.Fragment>}
              </button>
              <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-black/90 backdrop-blur border border-white/10 rounded text-[10px] font-bold text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl z-50">
                {lockEnergy ? "Energy Locked: Presets only change geometry" : "Energy Unlocked: Presets apply global physics settings"}
              </div>
            </div>
          </div>
          <select
            className="w-full bg-black border border-white/20 rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-primary transition-colors"
            onChange={(e) => {
              if (e.target.value === 'preset67') {
                setConfig(c => ({
                  ...c,
                  // Apply globals only if NOT locked
                  ...(lockEnergy ? {} : {
                    particleCount: 67000,
                    mode: SimulationMode.HARMONIC,
                    speed: 15, // Ultra
                  }),
                  extensions: {
                    crystal: { threeFold: 0.38, sixFold: 0.38, lattice: 0 },
                    harmonic: { commaSpiral: 0.23, perfectFifths: 0.26, equalTemp: 0 },
                    topology: { trefoil: 0.24, torus: 0.67, hopf: 0 }
                  }
                }));
              } else if (e.target.value === 'holytrinity') {
                // Holy Trinity — cloned from Entangled 67, 260k density, Fast,
                // with the Gasket (3-fold) kaleidoscope. The trinity = 3-fold.
                setConfig(c => ({
                  ...c,
                  ...(lockEnergy ? {} : {
                    particleCount: 330000,
                    mode: SimulationMode.HARMONIC,
                    speed: 1,        // phase duration 1000ms
                    amplitude: 33.3, // field amplitude
                  }),
                  extensions: {
                    crystal: { threeFold: 0.38, sixFold: 0.38, lattice: 0 },
                    harmonic: { commaSpiral: 0.23, perfectFifths: 0.26, equalTemp: 0 },
                    topology: { trefoil: 0.24, torus: 0.67, hopf: 0 }
                  }
                }));
                props.setKaleidoMode?.(3); // Gasket (3-fold) kaleidoscope
              } else if (e.target.value === 'atomic') {
                setConfig(c => ({
                  ...c,
                  // Apply globals only if NOT locked
                  ...(lockEnergy ? {} : {
                    speed: 5, // 200ms
                    exposure: 3.0,
                    particleCount: 350000,
                    quality: 2.0,
                    amplitude: 12.0,
                    mode: SimulationMode.HARMONIC,
                  }),
                  extensions: {
                    crystal: { threeFold: 0, sixFold: 0, lattice: 0 },
                    harmonic: { commaSpiral: 0, perfectFifths: 0, equalTemp: 0 },
                    topology: { trefoil: 0, torus: 0, hopf: 0 }
                  }
                }));
              }
            }}
            value=""
          >
            <option value="" disabled>Select a Preset...</option>
            <option value="holytrinity">Holy Trinity (Gasket · 330k · 33.3 amp)</option>
            <option value="preset67">Entangled 67 (Mobile Optimized)</option>
            <option value="atomic">Atomic (High Energy)</option>
          </select>
        </div>

        <div className="space-y-6">
          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-tertiary font-bold text-sm mb-3 flex items-center gap-2"><Fingerprint size={16} /> Crystallographic Symmetry</div>
            <div className="space-y-2">
              <EffectSlider label="3-Fold (120°) Symmetry" value={config.extensions.crystal.threeFold} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, threeFold: v } } }))} />
              <EffectSlider label="6-Fold (60°) Symmetry" value={config.extensions.crystal.sixFold} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, sixFold: v } } }))} />
              <EffectSlider label="Hexagonal Lattice" value={config.extensions.crystal.lattice} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, lattice: v } } }))} />
            </div>
          </div>

          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-secondary font-bold text-sm mb-3 flex items-center gap-2"><Activity size={16} /> Pythagorean Harmonics</div>
            <div className="space-y-2">
              <EffectSlider label="Comma Spiral (23.46¢)" value={config.extensions.harmonic.commaSpiral} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.HARMONIC : c.mode, extensions: { ...c.extensions, harmonic: { ...c.extensions.harmonic, commaSpiral: v } } }))} />
              <EffectSlider label="Perfect Fifth Stack" value={config.extensions.harmonic.perfectFifths} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.HARMONIC : c.mode, extensions: { ...c.extensions, harmonic: { ...c.extensions.harmonic, perfectFifths: v } } }))} />
            </div>
          </div>

          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-primary font-bold text-sm mb-3 flex items-center gap-2"><Hash size={16} /> Topological Forms</div>
            <div className="space-y-3">
              <EffectSlider
                label="Trefoil Knot"
                value={config.extensions.topology.trefoil}
                max={0.42}
                onChange={(v) => setConfig(c => ({ ...c, extensions: { ...c.extensions, topology: { ...c.extensions.topology, trefoil: v } } }))}
              />
              <EffectSlider label="Toroidal Attractor" value={config.extensions.topology.torus} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.TOPOLOGY : c.mode, extensions: { ...c.extensions, topology: { ...c.extensions.topology, torus: v } } }))} />
            </div>
          </div>
        </div>
      </Panel>

      {/* Camera Panel */}
      <Panel title="Camera Control" subtitle="Navigate N-particle phase space" active={activePanel === 'camera'} onClose={() => setActivePanel(null)}>
        <div className="grid grid-cols-2 gap-3 mb-6">
          <button onClick={() => onCameraMove({ position: [0, 30, 0.1], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Top View</button>
          <button onClick={() => onCameraMove({ position: [30, 0, 0], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Side View</button>
          <button onClick={() => onCameraMove({ position: [20, 20, 20], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Isometric</button>
          <button onClick={() => onCameraMove({ position: [0.1, 0.1, 0.1], target: [10, 10, 10] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Core View</button>
        </div>

        <Button variant="secondary" onClick={onResetCamera}>Reset Camera</Button>

        <div className="mt-6 p-4 bg-black/30 rounded-xl border border-white/5">
          <div className="text-xs text-white/40 uppercase mb-2">Camera Telemetry</div>
          <div className="grid grid-cols-2 gap-4 font-mono text-sm">
            <div>X: <span className="text-tertiary">0.00</span></div>
            <div>Y: <span className="text-tertiary">0.00</span></div>
            <div>Z: <span className="text-tertiary">0.00</span></div>
            <div>D: <span className="text-primary">25.0</span></div>
          </div>
        </div>
      </Panel>

      {/* Swarm Panel */}
      <Panel
        title="Swarm Status"
        subtitle="Distributed compute network telemetry"
        active={activePanel === 'swarm'}
        onClose={() => setActivePanel(null)}
      >
        <div className="bg-white/5 p-4 rounded-xl border border-white/10 text-white">
          <div className="flex items-center justify-between text-sm font-bold mb-2">
            <span>Connection Status:</span>
            <span className={isConnected ? 'text-emerald-400' : 'text-rose-400'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm font-bold">
            <span>Tasks Completed:</span>
            <span className="text-primary font-mono">{tasksCompleted}</span>
          </div>
        </div>

        {gaStatus && (
          <div className="bg-white/5 p-4 rounded-xl border border-white/10 text-white mt-4">
            <div className="flex items-center justify-between text-sm font-bold mb-2">
              <span>GA Generation:</span>
              <span className="text-tertiary font-mono">{gaStatus.generation}</span>
            </div>
            <div className="flex items-center justify-between text-sm font-bold mb-2">
              <span>Best Fitness:</span>
              <span className="text-secondary font-mono">{gaStatus.best_fitness.toFixed(4)}</span>
            </div>
            <div className="text-xs font-bold mb-1">Best Genome (Phases):</div>
            <div className="text-xs text-white/70 font-mono break-all line-clamp-3">
              [{gaStatus.best_genome.map(p => p.toFixed(2)).join(', ')}]
            </div>

            <button
              onClick={() => props.setShowArray(!props.showArray)}
              className={`mt-4 w-full py-2 rounded-lg text-xs font-bold uppercase transition-colors ${props.showArray ? 'bg-primary text-white' : 'bg-white/10 text-white/50 hover:bg-white/20'}`}
            >
              {props.showArray ? 'Hide Emitters' : 'Show Emitters'}
            </button>
          </div>
        )}
      </Panel>

      {/* Tools Panel — registry of the archive's other pages (see TOOLS above) */}
      <Panel
        title="Tools"
        subtitle="Other pages in the archive"
        active={activePanel === 'tools'}
        onClose={() => setActivePanel(null)}
      >
        <div className="space-y-3">
          {TOOLS.map((t) => (
            <a
              key={t.href}
              href={siteHref(t.href)}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-start gap-3 w-full p-4 rounded-xl bg-black/30 border border-white/5 hover:border-tertiary/40 hover:bg-black/50 transition-colors active:scale-[0.99]"
            >
              <div className="shrink-0 mt-0.5 text-tertiary">{t.icon}</div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-white">{t.name}</span>
                  {t.tag && (
                    <span className="shrink-0 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-tertiary/20 text-tertiary">
                      {t.tag}
                    </span>
                  )}
                </div>
                <p className="text-xs text-white/60 leading-relaxed mt-1">{t.blurb}</p>
                <span className="text-[10px] font-mono text-white/30 tracking-widest">{t.href}</span>
              </div>
              <ExternalLink size={14} className="shrink-0 mt-1 text-white/30 group-hover:text-tertiary transition-colors" />
            </a>
          ))}
        </div>
        <div className="text-center text-[10px] font-bold uppercase tracking-wide text-white/25 pt-1">
          Opens in a new tab — the field keeps running
        </div>
      </Panel>

      {/* Navigation Bar */}
      <div className="fixed bottom-0 left-0 w-full h-[80px] bg-glass backdrop-blur-xl border-t border-white/10 flex justify-around items-center px-2 sm:px-4 z-50">
        <NavItem icon={<Settings />} label="Control" active={activePanel === 'controls'} onClick={() => setActivePanel(activePanel === 'controls' ? null : 'controls')} />
        <NavItem icon={<Waves />} label="Fields" active={activePanel === 'waves'} onClick={() => setActivePanel(activePanel === 'waves' ? null : 'waves')} />
        <NavItem icon={<FlaskConical />} label="Labs" active={activePanel === 'labs'} onClick={() => setActivePanel(activePanel === 'labs' ? null : 'labs')} />
        <NavItem icon={<Camera />} label="Camera" active={activePanel === 'camera'} onClick={() => setActivePanel(activePanel === 'camera' ? null : 'camera')} />
        <NavItem
          icon={<LayoutGrid />}
          label={isConnected ? 'Online' : 'Offline'}
          active={activePanel === 'swarm'}
          onClick={() => setActivePanel(activePanel === 'swarm' ? null : 'swarm')}
        />
        <NavItem icon={<Wrench />} label="Tools" active={activePanel === 'tools'} onClick={() => setActivePanel(activePanel === 'tools' ? null : 'tools')} />
      </div>
    </>
  );
};