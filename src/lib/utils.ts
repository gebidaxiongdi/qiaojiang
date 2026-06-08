import { Skill, CATEGORIES } from '@/types/skill';
import skillsData from '@/data/skills.json';

export function getSkills(): Skill[] {
  return skillsData as Skill[];
}

export function getCategoryIcon(category: string): string {
  const cat = CATEGORIES.find(c => c.key === category);
  return cat?.icon || '🔧';
}

export function getScoreClass(score: number): string {
  if (score >= 8.5) return 'text-emerald-400 border-emerald-400';
  if (score >= 7) return 'text-amber-400 border-amber-400';
  return 'text-red-400 border-red-400';
}
