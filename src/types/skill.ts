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
  { key: '前端开发', icon: '🎨', desc: 'React、Vue、CSS、动效、UI设计' },
  { key: '后端开发', icon: '⚙️', desc: 'API、数据库、Docker、微服务' },
  { key: '编程语言', icon: '🦀', desc: 'Python、Rust、Go、Java、TypeScript' },
  { key: '框架教程', icon: '📚', desc: 'Django、Spring Boot、Next.js、PyTorch' },
  { key: '网络安全', icon: '🛡️', desc: '代码审计、漏洞扫描、合规检查' },
  { key: '测试工具', icon: '🧪', desc: 'TDD、E2E测试、浏览器QA、回归测试' },
  { key: '网站设计', icon: '🌐', desc: '搭网站、写代码、低代码生成' },
  { key: '图片生成', icon: '🎨', desc: '画图、做素材、修图' },
  { key: '视频制作', icon: '🎬', desc: '剪视频、加字幕、配音、动画' },
  { key: '学习必备', icon: '🎓', desc: '学英语、读论文、查资料、备考' },
  { key: '电商带货', icon: '💰', desc: '写商品文案、做详情页、数据分析' },
  { key: '数据分析', icon: '📊', desc: '做图表、分析数据、出报告' },
  { key: 'AI调教', icon: '🧠', desc: 'Agent调优、Prompt工程、记忆增强' },
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
