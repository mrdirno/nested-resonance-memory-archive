// Author: Aldrin Payopay · GPL-3.0-only
import { normalizeArtRecipe, type ArtLayer, type ArtRecipe } from './artRack';

/** A candidate is UI state. It must never enter a saved recipe before Keep. */
export interface ArtAudition {
  layer: ArtLayer;
  placement: 'add' | 'replace';
  targetId: string | null;
}

export function previewArtRecipe(recipe: ArtRecipe, audition: ArtAudition | null, alone = false): ArtRecipe {
  if (!audition) return recipe;
  const { layer, placement, targetId } = audition;
  // A transient ninth layer may be auditioned at capacity; saved v1 stays at eight.
  const layers = alone ? [layer] : placement === 'replace'
    ? recipe.layers.map(kept => kept.id === targetId ? layer : kept)
    : [...recipe.layers, layer];
  return { ...recipe, layers, soloId: null };
}

export function keepArtAudition(recipe: ArtRecipe, audition: ArtAudition, start = false): ArtRecipe {
  if (start) return normalizeArtRecipe({ ...recipe, layers: [audition.layer], soloId: null });
  if (audition.placement === 'add' && recipe.layers.length >= 8) throw new Error('All eight layers are filled. Replace a selected layer or remove one.');
  if (audition.placement === 'replace' && !recipe.layers.some(layer => layer.id === audition.targetId)) throw new Error('Select a kept layer to replace.');
  return normalizeArtRecipe(previewArtRecipe(recipe, audition));
}
