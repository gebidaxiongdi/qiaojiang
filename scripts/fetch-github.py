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
# 策略：精确匹配优先，通配匹配在后，同一条目内按优先级排序
CATEGORY_KEYWORDS = {
    'AI调教': [
        # 精确匹配（长关键词优先）
        'memory system', 'memory enhancement',
        'skill collection', 'skill registry', 'skill management',
        'awesome list', 'curated list',
        'self-evolution', 'self improvement', 'self-improving',
        'agent harness', 'agent optimization',
        'meta-skill', 'tool calling platform',
        'runtime patch', 'session management',
        'skill library', 'ecosystem', '资源导航',
        'cowagent', 'ecc agent', 'observability',
        'workflow automation', 'agentic proxy',
        'skill observability', 'stitch', 'superpowers',
        'buildwithclaude', 'memory system', 'lychee',
    ],
    '自媒体人': [
        'writing skill', 'blog post', 'social media', 'content creation',
        'newsletter', 'trending content', 'last 30 days', 'last30days',
        'avoid ai', 'anti ai', 'anti-ai slop',
        '写作', '文案', 'content writer', 'rewrite',
        'no-no-debug',
    ],
    '办公必备': [
        'note taking', 'obsidian', 'notebooklm', 'knowledge management',
        'document', 'office', 'excel', 'spreadsheet',
        'presentation', 'slides', 'ppt', 'pitch deck',
        'enterprise', 'team collaboration', 'project management',
        'productivity', '写周报', '表格', '文档', '办公',
        'im platform', 'telegram', 'wechat', 'messaging bridge',
        'claude-to-im', 'open-design', 'user research',
    ],
    '网站设计': [
        'frontend', 'backend', 'fullstack', 'web app',
        'low-code', 'lowcode', 'jeecgboot',
        'desktop app', 'electron', 'figma',
        'mobile automation', 'ios build', 'xcode',
        'unity engine', 'unity3d', 'game engine',
        'sandbox', 'browser', 'shell', 'terminal control',
        'linux desktop', 'wayland', 'gnome',
        'color science', 'color space',
        'desktop commander', 'mcp server for',
        'mobile-mcp', 'unity-mcp', 'casdoor',
        'peekaboo', 'sso', 'identity', 'auth',
    ],
    '学习必备': [
        'research paper', 'scientific research', 'academic paper',
        'tutorial', 'tutor', 'course', 'guide', 'study',
        'learning', 'math', 'mathematics', 'deeplake', 'dataset',
        '学习', '论文', '研究', '读书', '英语', 'language learning',
        'search engine', 'web search', 'hexstrike', 'rocketride',
        'cybersecurity', 'security framework',
    ],
    '图片生成': [
        'image generation', 'image generator', 'image creation',
        'generative media', 'media generation',
        'comfyui', 'stable diffusion', 'midjourney',
        'illustration', '画图', '素材', '封面',
    ],
    '视频制作': [
        'video generation', 'video creator', 'animation tool',
        'graphify', 'chart animation', '数据可视化',
        '剪辑', '视频制作', 'subtitle', '配音',
    ],
    '数据分析': [
        'data analysis', 'data analytics', 'data visualization',
        'chart', 'dashboard', 'mcp-toolbox',
        '数据', '分析', '报表', 'analytics',
    ],
    '电商带货': [
        'ecommerce', 'shopify', '商品管理', '带货',
        'marketing', 'seo', '广告', 'promotion',
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
    """根据名称和描述生成一句话利益点（用户视角）"""
    text = f'{name} {description}'.lower()

    # 精确匹配优先（长关键词优先匹配）
    precise = [
        # 笔记/文档
        (['obsidian'], '记笔记时AI自动整理和查找，想找什么直接问就行'),
        (['notebooklm', 'notebook'], '用AI管理学习笔记，自动归纳重点，复习效率翻倍'),
        (['knowledge', '知识库'], '把公司资料交给AI管理，员工问什么AI都能答'),
        # 记忆
        (['memory', 'remember'], '让AI拥有长期记忆，每次对话都记得你是谁、聊过什么'),
        # 搜索
        (['search', 'search engine', 'web search'], '让AI自己上网查资料，搜到的结果比手动搜索更精准'),
        # 安全
        (['security', 'audit', 'cyber'], '写代码时AI自动做安全审查，揪出漏洞和风险'),
        (['pentest', 'penetration'], '让AI帮你做渗透测试，找出系统安全隐患'),
        # 写作
        (['writing', 'content', 'blog'], '写文章时AI帮你优化表达，改掉AI腔，读起来更像真人写的'),
        (['rewrite', 'anti-ai', 'avoid'], '写完后AI帮你去掉AI味，让文章读起来更像人写的'),
        # 编程
        (['frontend', 'react', 'vue', 'css', 'tailwind'], '写前端页面时AI给你最佳实践建议，代码质量更高'),
        (['backend', 'api', 'fullstack'], '开发后端时AI帮你设计API和架构，减少返工'),
        (['code', 'programming', 'develop'], '写代码时AI实时辅助，提升开发效率减少bug'),
        (['low-code', 'lowcode', 'jeecgboot'], '不懂代码也能用AI生成管理系统，一句话搞定增删改查'),
        # 研究
        (['research', 'paper', 'scientific'], '做研究时AI帮你读论文、找资料、列提纲，效率翻倍'),
        (['tutor', 'tutorial', 'course', 'study'], '学习新知识时AI当你的私人老师，随时解答问题'),
        (['math', 'mathematics'], '做数学题或数据计算时AI帮你推导和验证结果'),
        # 数据
        (['data analysis', 'data analytics', 'dashboard'], '处理数据时AI自动出图表和分析报告，不用自己画'),
        (['chart', 'visualization'], '有数据要展示时AI自动生成图表，一目了然'),
        # 设计
        (['image', 'generative', 'illustration'], '需要配图时AI直接生成，不用找素材也不用自己画'),
        (['design', 'figma'], '做UI设计时AI帮你出方案和组件库，设计效率翻倍'),
        # 视频
        (['video', 'animation', 'remotion'], '做视频时AI帮你生成动画和特效，剪片子更快'),
        (['graphify'], '把数据一键变成动态图表视频，汇报演示更生动'),
        # 企业
        (['enterprise', 'team'], '团队协作时AI帮你管理项目进度和任务分配'),
        (['workspace'], '在浏览器里直接管理AI和Skill，不用装任何客户端'),
        # 平台
        (['mcp'], '通过MCP协议让AI连接各种外部工具和数据源'),
        (['desktop', 'electron'], '在桌面端管理所有AI模型和Skill，还能手机远程控制'),
        # 优化
        (['optimize', 'improve', 'evolu'], '让AI学会自我优化，越用越顺手，越来越聪明'),
        (['skill', 'collection', 'awesome'], '一次性获得大量AI Skill合集，不用一个个去搜'),
        # 自动化
        (['automation', 'workflow'], '让AI自动执行重复工作流程，省下时间做更重要的事'),
        # 测试
        (['testing', 'test', 'debug'], '写测试用例时AI自动生成，覆盖更多场景少出bug'),
        # 其他具体
        (['claude', 'anthropic'], '用Claude Code时扩展更多实用Skill，让Claude更强大'),
        (['hermes'], '用Hermes Agent时安装更多Skill，扩展AI能力边界'),
        (['unity', 'game'], '做游戏开发时AI帮你写Unity代码和测试，开发更快'),
        (['mobile', 'ios', 'xcode'], '开发iOS应用时AI帮你处理Xcode构建和自动化任务'),
        (['color'], '做设计时AI帮你选颜色搭配色，不懂色彩理论也能出好效果'),
        (['browser', 'sandbox'], '让AI在沙箱环境里安全运行代码和浏览器操作'),
        (['presentation', 'slides', 'ppt'], '做PPT时AI帮你排版设计，几分钟搞定精美演示文稿'),
        (['email', 'mail'], '写邮件时AI帮你起草和优化，沟通更高效'),
        (['note', 'document'], '处理文档时AI帮你整理和归档，找文件不再大海捞针'),
    ]

    for keywords, benefit in precise:
        for kw in keywords:
            if kw.lower() in text:
                return benefit

    # 兜底：从名称推断
    fallbacks = [
        (['ai', 'agent', 'mcp'], '让AI连接更多工具和服务，扩展能力边界'),
        (['vercel', 'next'], '做Web开发时AI给你最佳实践指导，少走弯路'),
        (['github', 'actions'], '用GitHub时AI帮你自动化工作流程'),
        (['llm', 'gpt', 'model'], '让AI更高效地调用大语言模型，节省Token费用'),
    ]
    for keywords, benefit in fallbacks:
        for kw in keywords:
            if kw.lower() in text:
                return benefit

    return f'装上这个Skill，你的AI就能处理{name}相关任务，省时省力'


def generate_tags(name: str, description: str, category: str) -> list[str]:
    """生成标签"""
    text = f'{name} {description}'.lower()
    tag_map = {
        '笔记': ['笔记', 'note', 'obsidian', 'knowledge'],
        '记忆': ['记忆', 'memory', 'remember', 'memor'],
        '搜索': ['搜索', 'search', 'web search'],
        '安全': ['安全', 'security', 'audit', 'safe', 'cyber', 'pentest'],
        '写作': ['写作', 'write', 'writing', 'content', 'blog', 'rewrite'],
        '编程': ['编程', 'code', 'develop', 'program', 'frontend', 'backend'],
        '低代码': ['低代码', 'lowcode', 'low-code', 'jeecgboot'],
        '自动化': ['自动', 'auto', 'automation', 'workflow'],
        '教程': ['教程', 'tutorial', 'guide', 'course'],
        'AI调教': ['调教', '进化', 'self', 'optimize', 'improve'],
        'Claude': ['claude', 'anthropic'],
        'Hermes': ['hermes', 'nous'],
        'MCP': ['mcp'],
        '设计': ['设计', 'design', 'figma', 'color', 'ui'],
        '数据': ['数据', 'data', 'chart', 'dashboard', 'analytics'],
        '视频': ['视频', 'video', 'animation', 'remotion', 'graphify'],
        '图片': ['图片', 'image', 'illustration', 'generative'],
        '企业级': ['enterprise', '企业', '团队'],
        '全平台': ['全平台', 'cross-platform', 'multi-platform'],
        '研究': ['研究', 'research', 'paper', 'scientific'],
        '游戏': ['游戏', 'unity', 'game'],
        '移动端': ['mobile', 'ios', 'xcode', 'app'],
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

            # ====== 评分计算（6维度） ======
            from datetime import datetime as dt
            updated_dt = dt.strptime(updated, '%Y-%m-%d')
            days_old = (dt.now() - updated_dt).days

            # 1. 社区人气 (20%) - stars
            star_score = min(10, stars / 5000)

            # 2. 用户采用 (15%) - downloads
            dls = stars + forks * 10
            dls_score = min(10, dls / 50000)

            # 3. 维护活跃 (20%) - 更新时间
            if days_old < 30: fresh_score = 10
            elif days_old < 90: fresh_score = 8.5
            elif days_old < 180: fresh_score = 7
            elif days_old < 365: fresh_score = 5
            elif days_old < 730: fresh_score = 3
            else: fresh_score = 1.5

            # 4. 安全可靠 (20%) - license
            lic = (license_info.get('spdx_id', '') if license_info else '').upper()
            if lic in ('MIT', 'APACHE-2.0', 'APACHE-2'): safe_score = 9
            elif lic in ('BSD', 'ISC', 'UNLICENSE', 'CC0-1.0'): safe_score = 8
            elif lic in ('GPL-3.0', 'GPL-2.0', 'LGPL', 'AGPL-3.0'): safe_score = 6.5
            elif lic and lic != 'N/A' and lic != 'NOASSERTION': safe_score = 5
            else: safe_score = 3

            # 5. 项目健全 (15%) - 综合质量
            quality = 0
            if license_info and license_info.get('spdx_id'): quality += 2.5
            if len(description) > 50: quality += 2.5
            if stars > 1000: quality += 2.5
            if len(topics) > 0: quality += 2.5
            quality_score = quality

            # 6. 平台兼容 (10%) - 平台数
            plat_count = len(platforms)
            plat_score = min(10, plat_count * 2.5)

            # 综合评分
            final_score = round(
                star_score * 0.20 +
                dls_score * 0.15 +
                fresh_score * 0.20 +
                safe_score * 0.20 +
                quality_score * 0.15 +
                plat_score * 0.10,
                1
            )

            skill = {
                'id': skill_id,
                'name': name,
                'benefit': benefit,
                'description': description[:300],
                'category': category,
                'score': min(10, max(1, final_score)),
                'stars': stars,
                'downloads': dls,
                'updated': updated,
                'install': generate_install_command(name, platforms, html_url),
                'license': lic if lic else 'N/A',
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
