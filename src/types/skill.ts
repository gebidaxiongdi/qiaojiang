export interface Skill {
  id: string;
  name: string;
  benefit: string;
  description: string;
  category: string;
  score: number;
  stars: number;
  downloads: number;
  updated: string;
  install: string;
  license: string;
  url: string;
  tags: string[];
  source: string;
  platforms: string[];
  created_at: string;
}

export const CATEGORIES = [
  { key: '办公必备', icon: '📄', desc: '写周报、做表格、理文档、记笔记' },
  { key: '自媒体人', icon: '📱', desc: '写文案、去AI味、起标题、做封面' },
  { key: '网站设计', icon: '🌐', desc: '搭网站、写代码、低代码生成' },
  { key: '图片生成', icon: '🎨', desc: '画图、做素材、修图' },
  { key: '视频制作', icon: '🎬', desc: '剪视频、加字幕、配音' },
  { key: '学习必备', icon: '🎓', desc: '学英语、读论文、查资料、备考' },
  { key: '电商带货', icon: '💰', desc: '写商品文案、做详情页、数据分析' },
  { key: '数据分析', icon: '📊', desc: '做图表、分析数据、出报告' },
  { key: 'AI调教', icon: '🧠', desc: '记忆增强、优化、学新手艺' },
  { key: '其他', icon: '🔧', desc: '暂时不好归类的' },
] as const;

export const PLATFORM_MAP: Record<string, { label: string }> = {
  hermes: { label: 'Hermes' },
  claude: { label: 'Claude' },
  codex: { label: 'Codex' },
  openclaw: { label: 'OpenClaw' },
  mcp: { label: 'MCP' },
  gemini: { label: 'Gemini' },
  all: { label: '全平台' },
};
