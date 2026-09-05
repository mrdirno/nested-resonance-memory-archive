// Author: Aldrin Payopay · GPL-3.0-only
// Editor intent and UI-only history. Recipe v1 remains unchanged.
import { normalizeArtRecipe, type ArtKind, type ArtLayer, type ArtRecipe } from './artRack';

export type ArtDiceScope = 'composition' | 'layer';
export interface ArtSelection { selectedId: string; scope: ArtDiceScope }
export interface ArtHistoryEntry { recipe: ArtRecipe; selection: ArtSelection }

export function artSelection(recipe: ArtRecipe, selection: ArtSelection): ArtSelection {
  const exists = recipe.layers.some(layer => layer.id === selection.selectedId);
  const selectedId = exists ? selection.selectedId : recipe.layers.at(-1)?.id || '';
  // A missing selection must never silently aim dice at the fallback layer.
  return { selectedId, scope: exists ? selection.scope : 'composition' };
}

export function artHistoryEntry(recipe: ArtRecipe, selection: ArtSelection): ArtHistoryEntry {
  const snapshot = normalizeArtRecipe(recipe);
  return { recipe: snapshot, selection: artSelection(snapshot, selection) };
}

/** Use replaces the native stack; Add alone appends. Parent media is not involved. */
export function artTemplateIntent(recipe: ArtRecipe, layer: ArtLayer, intent: 'use' | 'add'): ArtRecipe {
  if (intent === 'add' && recipe.layers.length >= 8) throw new Error('Eight layers are in this composition. Remove one to add another.');
  return intent === 'use'
    ? { ...recipe, layers: [layer], soloId: null }
    : { ...recipe, layers: [...recipe.layers, layer] };
}

// Each descriptor is data for controls that drawArt/sampleArtLayer actually use.
// No native renderer exposes independently addressable regions.
export const ART_NATIVE_CONTROLS = {
  look: ['opacity', 'scale', 'density'],
  position: ['rotation', 'x', 'y'],
  motion: ['none', 'form', 'scale', 'rotation', 'opacity', 'drift'],
  regions: [],
} as const;
export const ART_PARAMETER_UI = {
  opacity: { label: 'Opacity', min: 0, max: 1, step: .01 },
  scale: { label: 'Scale', min: .3, max: 2, step: .01 },
  density: { label: 'Density', min: 0, max: 1, step: .01 },
  rotation: { label: 'Rotation', min: -180, max: 180, step: 1 },
  x: { label: 'Horizontal position', min: -.75, max: .75, step: .01 },
  y: { label: 'Vertical position', min: -.75, max: .75, step: .01 },
} as const;
export const ART_INSTRUMENT_UI: Record<ArtKind, { densityHelp: string; controls: typeof ART_NATIVE_CONTROLS }> = {
  contour: { densityHelp: 'How many contour lines fill the field.', controls: ART_NATIVE_CONTROLS },
  rosette: { densityHelp: 'Petal detail and the number of nested rings.', controls: ART_NATIVE_CONTROLS },
  rings: { densityHelp: 'How many ellipses overlap in each family.', controls: ART_NATIVE_CONTROLS },
  ribbons: { densityHelp: 'The number and bending depth of the bands.', controls: ART_NATIVE_CONTROLS },
  branches: { densityHelp: 'How many levels each branch grows.', controls: ART_NATIVE_CONTROLS },
  facets: { densityHelp: 'How many crystals fill the canvas.', controls: ART_NATIVE_CONTROLS },
  weave: { densityHelp: 'How tightly the woven grid is spaced.', controls: ART_NATIVE_CONTROLS },
  particles: { densityHelp: 'How many particles fill the field.', controls: ART_NATIVE_CONTROLS },
};
