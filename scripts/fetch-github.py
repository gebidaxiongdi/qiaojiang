"""
巧匠 · GitHub Skill 抓取脚本
每6小时运行一次，抓取最新 Skill 数据
"""

import json
import urllib.request
import urllib.error
import time
import os
import re
from datetime import datetime

# ====== 配置 ======
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'skills.json')
GITHUB_API = 'https://api.github.com'

# 搜索关键词（覆盖 Hermes / Claude / Codex / OpenClaw / MCP 生态）
SEARCH_QUERIES = [
    'hermes+skill+agent+topic:skill',
    'claude+code+skill+topic:skill',
    'claude-code+mcp+skill',
    'codex+cli+skill+topic:skill',
    'openclaw+skill',
    'mcp+server+agent+topic:mcp',
]

# 分类关键词映射（根据描述自动归类）
# 注意：顺序越靠前优先级越高，精确匹配放前面
CATEGORY_KEYWORDS = {
    '办公必备': [
        'obsidian', 'note', 'notes', 'document', 'office', 'excel', 'word',
        'ppt', 'email', 'calendar', 'workspace', 'productivity', '写周报',
        '表格', '文档', '办公', '协作', 'enterprise', '企业', 'project management',
        'team', 'notebooklm', 'open-design',
    ],
    'AI调教': [
        'memory', 'agent-skill', 'skill-collection', 'skill collection',
        'awesome-skill', 'skill库', 'skill合集', 'self-improve',
        'self-evolution', 'self evolution', '进化', 'optimize', '优化',
        'training', 'prompt', '超级库', 'awesome list', 'curated list',
        'cowagent', 'ecc', 'agent优化', 'ecosystem', '资源导航', '资源库',
    ],
    '自媒体人': [
        'writing', 'blog', 'social media', 'content creation', 'newsletter',
        '文案', '写作', 'media', 'avoid-ai', 'anti-ai', 'ai writing',
        'last30days', 'trending', 'viral', '自媒体',
    ],
    '网站设计': [
        'frontend', 'backend', 'fullstack', 'web app', 'website',
        'low-code', 'lowcode', '低代码', 'jeecgboot', '生成系统',
        'desktop app', 'electron', 'figma', 'ui design', 'component',
        'tailwind', 'css', 'html', 'react', 'vue', 'next.js',
    ],
    '图片生成': [
        'image generation', 'image gen', 'draw', 'illustration',
        '图片', '设计', '画图', '素材', 'comfyui', 'stable diffusion',
        'midjourney', '封面', 'canva',
    ],
    '视频制作': [
        'video', 'animation', '剪辑', '视频', 'subtitle', '配音',
        'video generation', 'short video', '短视频',
    ],
    '学习必备': [
        'research', 'paper', 'study', 'learn', 'education', 'tutorial',
        'tutor', '学习', '论文', '研究', 'academic', 'course', 'guide',
        '读书', '英语', 'language', 'deeplake', 'dataset', 'training data',
    ],
    '电商带货': [
        'ecommerce', 'shop', 'product', '电商', '商品', '带货',
        'marketing', 'seo', '广告', 'promotion',
    ],
    '数据分析': [
        'data analysis', 'data analytics', 'chart', 'dashboard',
        '数据', '分析', '报表', 'visualization', 'excel', 'spreadsheet',
        'mcp-toolbox', 'analytics',
    ],
    '其他': [],
}

# 平台关键词映射
PLATFORM_KEYWORDS = {
    'hermes': ['hermes', 'nousresearch'],
    'claude': ['claude', 'anthropic'],
    'codex': ['codex', 'openai'],
    'openclaw': ['openclaw', 'claw'],
    'mcp': ['mcp'],
    'gemini': ['gemini', 'google'],
}


def github_request(path: str) -> dict | None:
    """调用 GitHub API"""
    url = f'{GITHUB_API}{path}'
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    # 可选：加 Token 提高频率限制
    # token = os.environ.get('GITHUB_TOKEN')
    # if token:
    #     req.add_header('Authorization', f'token {token}')

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'  HTTP Error {e.code}: {url}')
        if e.code == 403:
            print('  ⚠️  API 频率限制，等 60 秒后重试...')
            time.sleep(60)
            return None
        return None
    except Exception as e:
        print(f'  Error: {e}')
        return None


def classify_category(name: str, desc: str, tags: list[str]) -> str:
    """根据名称+描述自动归类"""
    text = f'{name} {desc} {" ".join(tags)}'.lower()

    for cat, keywords in CATEGORY_KEYWORDS.items():
        if cat == '其他':
            continue
        for kw in keywords:
            if kw.lower() in text:
                return cat
    return '其他'


def detect_platforms(description: str, repo_name: str) -> list[str]:
    """检测兼容平台"""
    text = f'{description} {repo_name}'.lower()
    platforms = []
    for plat, keywords in PLATFORM_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                platforms.append(plat)
                break
    if not platforms:
        platforms.append('all')
    return platforms


def generate_benefit(name: str, description: str) -> str:
    """根据名称和描述生成一句话利益点"""
    # 关键词模板
    templates = [
        (['note', 'obsidian', 'knowledge', '文档', '笔记'], '让AI管理你的笔记和知识库，查找资料不用自己翻'),
        (['memory', 'remember', '记忆'], '让AI记住你的所有信息，告别每次都要重新介绍的烦恼'),
        (['search', 'web', 'search engine', '搜索'], '让AI自己上网查资料，比手动搜索快得多'),
        (['security', 'audit', 'safe', '安全', '审计'], '让AI帮你检查安全漏洞，保护代码和数据安全'),
        (['write', 'writing', 'blog', 'content', '写作', '内容'], '让AI帮你写文章和内容，再也不怕写东西'),
        (['code', 'program', 'develop', '编程', '开发'], '让AI帮你编写代码，提升开发效率'),
        (['research', 'paper', 'scientific', '研究', '论文', '科研'], '让AI帮你做研究，读论文列提纲'),
        (['low-code', 'lowcode', '低代码', 'platform'], '一句话生成整套系统，让AI帮你完成重复工作'),
        (['optimize', '进化', 'improve', 'self'], '让AI学会自我优化，越用越聪明'),
        (['workspace', '工作台', 'desktop'], '在浏览器/桌面端管理AI，一切尽在掌握'),
        (['data', 'chart', 'analytics', '数据', '图表', '分析'], '让AI处理数据生成图表，一目了然'),
        (['design', 'image', '图片', '设计'], '让AI帮你做设计，不懂设计也能出图'),
        (['mcp', 'server'], '让AI通过MCP协议连接各种工具和服务'),
    ]

    text = f'{name} {description}'.lower()
    for keywords, benefit in templates:
        for kw in keywords:
            if kw in text:
                return benefit

    # 默认
    return f'装了这个Skill，你的AI就能用上{name}'


def generate_tags(name: str, description: str, category: str) -> list[str]:
    """生成标签"""
    text = f'{name} {description}'.lower()
    tag_map = {
        '笔记': ['笔记', 'note', 'obsidian', 'knowledge'],
        '记忆': ['记忆', 'memory', 'remember'],
        '搜索': ['搜索', 'search', 'web'],
        '安全': ['安全', 'security', 'audit', 'safe'],
        '写作': ['写作', 'write', 'writing', 'content'],
        '编程': ['编程', 'code', 'develop', 'program'],
        '低代码': ['低代码', 'lowcode', 'low-code'],
        '自动化': ['自动', 'auto', 'automation'],
        '教程': ['教程', 'tutorial', 'guide', '学习'],
        'ChatGPT': ['chatgpt', 'gpt', 'openai'],
        'Claude': ['claude', 'anthropic'],
        'MCP': ['mcp'],
        '企业级': ['enterprise', '企业', '团队'],
        '全平台': ['全平台', 'cross-platform', 'multi-platform'],
    }

    tags = []
    for tag, keywords in tag_map.items():
        for kw in keywords:
            if kw in text and tag not in tags:
                tags.append(tag)
                break

    # 保底标签
    if not tags:
        tags.append(category)

    return tags[:5]  # 最多5个


def fetch_skills_from_github() -> list[dict]:
    """从 GitHub 搜索并提取 Skill 数据"""
    all_items = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        print(f'🔍 搜索: {query}')
        data = github_request(f'/search/repositories?q={query}&sort=stars&order=desc&per_page=15')

        if not data or 'items' not in data:
            print('  无结果')
            continue

        for item in data['items']:
            repo_id = item['full_name']

            # 跳过已经收录的
            if repo_id in seen_ids:
                continue
            seen_ids.add(repo_id)

            name = item['name']
            full_name = item['full_name']
            description = item['description'] or ''
            stars = item['stargazers_count']
            updated = item['updated_at'][:10]
            license_info = item.get('license')
            license_name = license_info['spdx_id'] if license_info else 'N/A'
            html_url = item['html_url']
            topics = item.get('topics', [])
            forks = item.get('forks_count', 0)

            # 过滤：少于 10 star 的不收录（质量门槛）
            if stars < 10:
                continue

            # 过滤：描述太短的
            if len(description) < 20:
                description = f'{name} is an AI agent skill/tool for enhancing AI capabilities.'

            category = classify_category(name, description, topics)
            platforms = detect_platforms(description, full_name)
            benefit = generate_benefit(name, description)
            tags = generate_tags(name, description, category)

            # 生成唯一 ID
            skill_id = re.sub(r'[^a-z0-9-]', '', name.lower().replace('_', '-').replace(' ', '-'))[:50]
            if not skill_id:
                skill_id = f'skill-{len(all_items)}'

            skill = {
                'id': skill_id,
                'name': name,
                'benefit': benefit,
                'description': description[:300],  # 截断过长描述
                'category': category,
                'score': round(min(9.5, max(5.0, stars / 20000 + 5.0)), 1),
                'stars': stars,
                'downloads': stars + forks * 10,
                'updated': updated,
                'install': generate_install_command(name, platforms, html_url),
                'license': license_name,
                'url': html_url,
                'tags': tags,
                'source': 'github',
                'platforms': platforms,
                'created_at': datetime.now().strftime('%Y-%m-%d'),
            }

            all_items.append(skill)
            print(f'  ✅ {name} ({stars}⭐) → {category}')

        # 频率限制保护
        time.sleep(1)

    return all_items


def generate_install_command(name: str, platforms: list[str], url: str) -> str:
    """生成安装命令"""
    # 常见安装模式
    if 'hermes' in platforms or 'openclaw' in platforms:
        return f'npx skills add {name.lower().replace("_", "-").replace(" ", "-")}'
    elif 'claude' in platforms:
        return f'git clone {url}.git'
    else:
        return f'git clone {url}.git'


def merge_and_deduplicate(new_skills: list[dict], existing_skills: list[dict]) -> list[dict]:
    """合并新旧数据，去重（按url）"""
    url_map = {}
    for s in existing_skills:
        url_map[s['url']] = s

    for s in new_skills:
        if s['url'] not in url_map:
            url_map[s['url']] = s

    return list(url_map.values())


def main():
    print('=' * 50)
    print('  巧匠 · GitHub Skill 抓取器')
    print(f'  {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('=' * 50)

    # 读取已有数据
    existing = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f'\n📂 已有数据: {len(existing)} 个 Skill\n')

    # 抓取新数据
    new_skills = fetch_skills_from_github()
    print(f'\n🔎 本次抓取: {len(new_skills)} 个新 Skill')

    # 合并去重
    merged = merge_and_deduplicate(new_skills, existing)
    print(f'📊 合并后: {len(merged)} 个 Skill (去重)')

    # 按评分排序
    merged.sort(key=lambda s: s['score'], reverse=True)

    # 写入文件
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f'💾 已保存到: {DATA_FILE}')
    print('\n✅ 完成!')


if __name__ == '__main__':
    main()
