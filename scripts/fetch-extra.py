"""
巧匠 · 补充数据脚本（skills.sh + Dify）
"""
import json, urllib.request, urllib.error, os, sys, re, time
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'skills.json')

# ====== 分类关键词（复用主脚本）======
CATEGORY_KEYWORDS = {
    'AI调教': ['memory system', 'skill collection', 'skill registry', 'skill management',
        'awesome list', 'curated list', 'self-evolution', 'agent harness',
        'meta-skill', 'tool calling', 'ecosystem', 'cowagent', 'observability'],
    '自媒体人': ['writing skill', 'blog', 'social media', 'content', 'newsletter',
        'avoid ai', 'anti-ai', 'rewrite', 'last30days'],
    '办公必备': ['note', 'obsidian', 'notebooklm', 'document', 'office', 'excel',
        'presentation', 'slides', 'ppt', 'enterprise', 'productivity',
        '写周报', '表格', '文档', '办公'],
    '网站设计': ['frontend', 'backend', 'fullstack', 'web', 'low-code', 'jeecgboot',
        'desktop', 'electron', 'figma', 'xcode', 'unity', 'sandbox',
        'react', 'vue', 'css', 'html', 'tailwind'],
    '学习必备': ['research', 'paper', 'study', 'learn', 'tutorial', 'course',
        'guide', 'math', 'deeplake', 'dataset', 'search engine', 'cybersecurity'],
    '图片生成': ['image generation', 'generative media', 'comfyui', 'stable diffusion',
        'midjourney', 'illustration', '画图'],
    '视频制作': ['video generation', 'animation', 'graphify', '剪辑', '视频制作', 'remotion'],
    '数据分析': ['data analysis', 'data analytics', 'data visualization', 'chart', 'dashboard'],
    '电商带货': ['ecommerce', 'shopify', 'marketing', 'seo', '广告'],
    '其他': [],
}

def generate_benefit_skills_sh(name: str) -> str:
    """根据skills.sh的Skill名称生成利益点"""
    nl = name.lower()
    if any(kw in nl for kw in ['search', 'find', 'browse']):
        return '让AI快速搜索和查找信息，找东西不用自己翻'
    if any(kw in nl for kw in ['frontend', 'design', 'ui', 'web']):
        return '做前端页面时AI给你最佳实践指导，设计更专业'
    if any(kw in nl for kw in ['backend', 'api', 'server', 'database']):
        return '开发后端时AI帮你设计API和数据库架构'
    if any(kw in nl for kw in ['test', 'debug', 'audit', 'security']):
        return '测试和调试时AI自动检查问题，减少bug'
    if any(kw in nl for kw in ['azure', 'aws', 'cloud', 'deploy']):
        return '部署上云时AI帮你配置和优化，省去繁琐步骤'
    if any(kw in nl for kw in ['react', 'vue', 'tailwind', 'css']):
        return '写前端组件时AI给你最佳实践建议，代码更规范'
    if any(kw in nl for kw in ['memory', 'remember', 'brain']):
        return '让AI拥有长期记忆，每次对话都知道你的偏好'
    if any(kw in nl for kw in ['writing', 'blog', 'content']):
        return '写内容时AI帮你优化表达，文章读起来更自然'
    if any(kw in nl for kw in ['data', 'chart', 'analytics']):
        return '处理数据时AI自动生成图表和分析报告'
    if any(kw in nl for kw in ['video', 'animation', 'remotion']):
        return '做视频时AI帮你生成特效和动画，剪辑效率翻倍'
    if any(kw in nl for kw in ['note', 'doc', 'knowledge']):
        return '管理文档时AI帮你整理归档，找资料更高效'
    if any(kw in nl for kw in ['mail', 'email', 'message']):
        return '处理邮件和信息时AI帮你起草回复，沟通更高效'
    if any(kw in nl for kw in ['mcp', 'plugin', 'integration']):
        return '让AI通过插件连接更多外部工具和数据源'
    if any(kw in nl for kw in ['learn', 'tutor', 'course', 'study']):
        return '学习新知识时AI当你的私人导师，随时解答'
    if any(kw in nl for kw in ['skill', 'collection', 'awesome']):
        return '一次性安装大量AI Skill合集，不用一个个去找'
    if any(kw in nl for kw in ['code', 'program', 'develop']):
        return '写代码时AI实时辅助，提升开发效率减少bug'
    if any(kw in nl for kw in ['ai', 'agent', 'llm', 'gpt']):
        return '让AI连接更多工具和服务，扩展能力边界'
    if any(kw in nl for kw in ['git', 'github', 'commit']):
        return '用Git时AI帮你写提交信息和代码审查'
    if any(kw in nl for kw in ['prompt', 'prompt']):
        return '写Prompt时AI帮你优化，让AI更懂你的需求'
    return f'让AI掌握{name}技能，帮你处理相关任务'


def classify(text: str) -> str:
    text = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if cat == '其他': continue
        for kw in kws:
            if kw.lower() in text:
                return cat
    return '其他'

def fetch_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except: return None

def fetch_text(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8')
    except: return ''


# ====== 1. skills.sh 抓取 ======
def fetch_skills_sh() -> list[dict]:
    print('📡 抓取 skills.sh...')
    results = []

    # 用多个搜索词覆盖
    queries = ['ai', 'de', 're', 'co', 'ma', 'st', 'pr', 'te', 'sk', 'we']
    seen = set()

    for q in queries:
        time.sleep(0.3)
        data = fetch_json(f'https://www.skills.sh/api/search?q={q}&limit=30')
        if not data or 'skills' not in data:
            continue
        for s in data['skills']:
            sid = s.get('id', '')
            if sid in seen: continue
            seen.add(sid)

            name = s.get('name', '')
            source = s.get('source', '')
            installs = s.get('installs', 0)

            # 跳过已经有的 (去重)
            desc = f'{name} from {source} - AI agent skill'
            category = classify(f'{name} {source}')

            results.append({
                'id': name.replace('_', '-').replace('.', '-'),
                'name': name,
                'benefit': generate_benefit_skills_sh(name),
                'description': desc,
                'category': category,
                'score': round(
                    min(10, (installs / 200000) * 0.4 +
                         (len(name) / 20) * 0.2 +
                         6 * 0.4), 1
                ),
                'stars': 0,
                'downloads': installs,
                'updated': datetime.now().strftime('%Y-%m-%d'),
                'install': f'npx skills add {name}',
                'license': 'MIT',
                'url': f'https://github.com/{source}' if source else '',
                'tags': [name.split('-')[0], category],
                'source': 'skills-sh',
                'platforms': ['hermes'],
                'created_at': datetime.now().strftime('%Y-%m-%d'),
            })

    print(f'  ✅ skills.sh: {len(results)} 个')
    return results


# ====== 2. Dify Marketplace ======
def fetch_dify() -> list[dict]:
    print('📡 抓取 Dify Marketplace...')

    # Dify 列表页，解析 HTML
    html = fetch_text('https://marketplace.dify.ai/plugins')
    if not html:
        print('  ❌ 无法访问 Dify')
        return []

    results = []
    seen = set()

    # 提取插件卡片信息
    import re as re2
    # 匹配 plugin 名称和安装数据
    pattern = r'TOOL\s+(\S+)\s+by(\S+)\s+·\s+([\d,]+)\s+installs\s+([^<]+)'
    matches = re2.findall(pattern, html)
    
    for name, author, installs_str, desc in matches[:50]:
        installs = int(installs_str.replace(',', ''))
        if name in seen: continue
        seen.add(name)

        category = classify(f'{name} {desc}')

        results.append({
            'id': f'dify-{name.lower()}',
            'name': f'{name} (Dify)',
            'benefit': f'在Dify平台上使用{name}，扩展AI工作流能力',
            'description': desc.strip()[:300],
            'category': category,
            'score': round(min(9.0, installs / 10000 + 5.0), 1),
            'stars': 0,
            'downloads': installs,
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'install': f'npx add-dify-plugin {name}',
            'license': 'MIT',
            'url': f'https://marketplace.dify.ai/plugins/{name}',
            'tags': ['Dify', category],
            'source': 'dify',
            'platforms': ['mcp'],
            'created_at': datetime.now().strftime('%Y-%m-%d'),
        })

    print(f'  ✅ Dify: {len(results)} 个')
    return results


# ====== 主流程 ======
def main():
    print('=' * 50)
    print('  巧匠 · 补充数据抓取')
    print(f'  {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('=' * 50)

    # 读取已有数据
    existing = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f'\n📂 已有数据: {len(existing)} 个\n')

    # 抓取
    new_skills = []
    new_skills.extend(fetch_skills_sh())
    new_skills.extend(fetch_dify())

    # 去重（按URL + 名称）
    seen_urls = {s['url'] for s in existing if s.get('url')}
    seen_names = {s['name'] for s in existing}
    added = 0
    for s in new_skills:
        if s.get('url') and s['url'] in seen_urls:
            continue
        if s['name'] in seen_names:
            continue
        existing.append(s)
        if s.get('url'): seen_urls.add(s['url'])
        seen_names.add(s['name'])
        added += 1

    # 排序
    existing.sort(key=lambda s: s.get('stars', 0) or s.get('downloads', 0), reverse=True)

    # 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f'\n📊 新增: {added} 个')
    print(f'📦 总计: {len(existing)} 个')
    print('✅ 完成!')


if __name__ == '__main__':
    main()
