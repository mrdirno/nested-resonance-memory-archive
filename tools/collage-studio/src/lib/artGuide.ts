// Author: Aldrin Payopay · GPL-3.0-only
// C3724 — what the Art Room says about itself, decided without the DOM.
//
// THE WISH (collage well, bug, about_tool=layout): *"Missing undo — Missing info
// button in art room also prolly get rid of the which part drop down less
// clicks better."* Three lenses read "the which part drop down" as the footer's
// Dice scope select (Art composition / <layer name>): the only control in the
// room that literally asks which part, and the one tapped before every roll.
// This module is the pure half of the answer: which dice buttons are live, the
// sentence the stage shows for the instrument in hand, the four-line guide, and
// what Undo announces. Recipe v1 is untouched; nothing here is saved.
import { ART_TEMPLATES, type ArtKind, type ArtRecipe } from './artRack';
import type { ArtSelection } from './artIntent';

export type ArtDiceTarget = 'art' | 'layer';

export interface ArtDiceTargets {
  /** Dice art: at least one layer is enabled and unlocked. */
  art: boolean;
  /** Dice layer: the selected layer exists, is enabled and unlocked. */
  layer: boolean;
  /** The selected layer's instrument name, for the accessible name; '' when none. */
  layerName: string;
}

export function artTemplateName(kind: ArtKind): string {
  return ART_TEMPLATES.find(t => t.id === kind)?.name || kind;
}

function describe(kind: ArtKind): string {
  return ART_TEMPLATES.find(t => t.id === kind)?.description || '';
}

/**
 * One tap per target. A preview owns the dice while it is up (the room shows a
 * single "Dice preview" then), so both are false while auditioning.
 */
export function artDiceTargets(recipe: ArtRecipe, selection: ArtSelection, auditioning = false): ArtDiceTargets {
  const selected = recipe.layers.find(l => l.id === selection.selectedId);
  const layerName = selected ? artTemplateName(selected.kind) : '';
  if (auditioning) return { art: false, layer: false, layerName };
  return {
    art: recipe.layers.some(l => l.enabled && !l.locked),
    layer: !!selected && selected.enabled && !selected.locked,
    layerName,
  };
}

export interface ArtInstrumentNote {
  kind: ArtKind;
  name: string;
  text: string;
  /** preview: the audition's description · layer: the selected layer's · held / off: why Dice layer is dark. */
  state: 'preview' | 'layer' | 'held' | 'off';
}

/**
 * The instrument's own sentence. The written description of the twelve
 * instruments existed in the data and was rendered nowhere; the panel put it at
 * the moment of decision — previewing, or editing a selected layer — at zero
 * taps, instead of behind the help card. The room renders it inside the
 * preview sheet and under the selected layer's heading, NOT on the stage: the
 * stage is a fixed-height box on phones and the C3722 gate measured the line
 * costing the artwork 24px there. For the whole composition there is nothing
 * to say. When the selected layer cannot be diced, the line says why, so a
 * dark Dice layer is never a dead end.
 */
export function artInstrumentNote(recipe: ArtRecipe, selection: ArtSelection, auditionKind: ArtKind | null): ArtInstrumentNote | null {
  if (auditionKind) return { kind: auditionKind, name: artTemplateName(auditionKind), text: describe(auditionKind), state: 'preview' };
  if (selection.scope !== 'layer') return null;
  const layer = recipe.layers.find(l => l.id === selection.selectedId);
  if (!layer) return null;
  const name = artTemplateName(layer.kind);
  if (!layer.enabled) return { kind: layer.kind, name, text: `${name} is off. Turn it on in Layers to see it or dice it.`, state: 'off' };
  if (layer.locked) return { kind: layer.kind, name, text: `${name} is held. Dice leaves it alone until you unlock it in Layer options.`, state: 'held' };
  return { kind: layer.kind, name, text: describe(layer.kind), state: 'layer' };
}

/** Four lines, and only four: the help card is a card, not a manual. */
export const ART_ROOM_GUIDE: ReadonlyArray<string> = [
  'Browse a look, preview it over your layers, keep it. Up to eight layers, front to back.',
  'Dice art rolls every unlocked layer. Dice layer rolls only the one you picked.',
  'Undo takes any step back, sliders included. It sits in the top bar.',
  'Use in Studio places the artwork on your collage. Nothing leaves your device.',
];

/** Shown only where there is a keyboard; phones hide the whole list. */
export const ART_ROOM_SHORTCUTS: ReadonlyArray<readonly [keys: string, action: string]> = [
  ['⌘ Z / Ctrl Z', 'Undo'],
  ['⇧ ⌘ Z / Ctrl Y', 'Redo'],
  ['⌘ S / Ctrl S', 'Save recipe'],
  ['Esc', 'Close'],
];

/** A silent undo on a phone reads as a dead button: name the step taken back. */
export function artUndoNotice(label: string | undefined, redo: boolean): string {
  if (label) return `${redo ? 'Redid' : 'Undid'}: ${label}.`;
  return redo ? 'Change restored.' : 'Change undone.';
}
