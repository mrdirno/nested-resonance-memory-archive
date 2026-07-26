import { LayoutItem } from './layout';
import { LayoutMode } from '../types';

export interface Template {
  id: string;
  name: string;
  timestamp: number;
  layout: {
    mode: LayoutMode;
    count: number;
    seed: number; // The geometry seed
    aspect: number;
    gutter: number;
  };
  // We don't save specific images, just the geometry structure
}

const STORAGE_KEY = 'genart_templates_v1';

export const getTemplates = (): Template[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
};

export const saveTemplate = (name: string, layout: Template['layout']): Template => {
  const templates = getTemplates();
  const newTemplate: Template = {
    id: `tpl-${Date.now()}`,
    name,
    timestamp: Date.now(),
    layout
  };
  
  templates.push(newTemplate);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
  return newTemplate;
};

export const deleteTemplate = (id: string) => {
  const templates = getTemplates().filter(t => t.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
};
