"""
巧匠 · 分类优化脚本
基于benefit和name进行更精确的分类
"""
import json, os, re

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'skills.json')

# 精确分类规则（name + benefit）
RULES = [
    # --- 办公必备 ---
    ('办公必备', ['mail', 'email', 'lark', 'approval', 'note', 'doc', 'document',
                  'presentation', 'slides', 'ppt', 'spreadsheet', 'excel']),
    # --- 自媒体人 ---
    ('自媒体人', ['writing', 'blog', 'content creation', 'newsletter', 'rewrite',
                  'avoid ai', 'anti-ai', 'vibe-testing', 'vibe']),
    # --- 网站设计 ---
    ('网站设计', ['frontend', 'backend', 'fullstack', 'web design', 'ui design',
                  'react', 'vue', 'tailwind', 'css', 'html', 'component',
                  'low-code', 'lowcode', 'jeecgboot', 'azure', 'aws', 'cloud',
                  'deploy', 'firebase', 'stripe', 'turborepo', 'next.js',
                  'prisma', 'database', 'api', 'auth', 'better-auth',
                  'building-components', 'architecture', 'sleek-design',
                  'userscript', 'app-it', 'xcode', 'mobile', 'ios',
                  'sandbox', 'shell', 'terminal', 'desktop commander',
                  'figma', 'color', 'mcp-use', 'desktop', 'electron',
                  'planning-with-files', 'codepilot']),
    # --- 学习必备 ---
    ('学习必备', ['search', 'find', 'tavily', 'research', 'paper', 'study',
                  'tutorial', 'course', 'learn', 'tutor', 'math',
                  'deeplake', 'dataset', 'cyber', 'security',
                  'claude-code-guide', 'yupi', 'guide', 'hexstrike',
                  'ansari', 'apple-health', 'rocketride']),
    # --- AI调教 ---
    ('AI调教', ['memory', 'memor', 'awesome-', 'collection', 'registry',
                'ecosystem', 'self-evolution', 'optimize', '进化',
                'cowagent', 'ecc', 'mastra', 'skill-flow', 'clawhub',
                'ai-elements', 'ai-sdk', '技能', '调教', 'session',
                'selftune', 'claude-code-marketplace', 'agentgateway',
                'activepieces']),
    # --- 图片生成 ---
    ('图片生成', ['image', 'generative', 'illustration', 'comfyui',
                  'stable diffusion', 'midjourney']),
    # --- 视频制作 ---
    ('视频制作', ['video', 'animation', 'remotion', 'graphify', 'ai-video']),
    # --- 数据分析 ---
    ('数据分析', ['data analysis', 'data analytics', 'dashboard', 'chart',
                  'visualization', 'mcp-toolbox', 'apple-health']),
    # --- 电商带货 ---
    ('电商带货', ['ecommerce', 'shopify', 'marketing', 'seo', 'promotion']),
]


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        skills = json.load(f)

    changed = 0
    for s in skills:
        text = f"{s['name']} {s['benefit']} {s.get('description','')} {s.get('tags','')}".lower()
        old_cat = s['category']

        for cat, keywords in RULES:
            for kw in keywords:
                if kw.lower() in text:
                    s['category'] = cat
                    break
            if s['category'] != old_cat:
                break

        if s['category'] != old_cat:
            changed += 1
            print(f'  🔄 {s["name"]}: {old_cat} → {s["category"]}')

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

    print(f'\n📊 调整: {changed} 个')
    
    from collections import Counter
    cats = Counter(s['category'] for s in skills)
    print('\n=== 优化后分类分布 ===')
    for cat, count in cats.most_common():
        print(f'  {cat}: {count}个')


if __name__ == '__main__':
    main()
