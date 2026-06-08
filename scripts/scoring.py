"""
巧匠 · 跨平台公平评分系统

设计原则：
1. 每个维度(0-10分)在各自平台内归一化
2. 平台不直接比较数值，比较相对排名
3. GitHub 用 stars，skills.sh 用 installs，都在各自数据集内排百分位
"""

# ====== 评分维度与权重 ======
WEIGHTS = {
    'popularity': 0.30,    # 受欢迎度 - stars/installs 在各自平台排位
    'security': 0.25,      # 安全可靠 - 协议/来源信任度
    'developer': 0.25,     # 开发方实力 - 组织/公司实力
    'freshness': 0.20,     # 维护活跃 - 更新时间
}

# ====== 安全评分 ======
LICENSE_SCORE = {
    'MIT': 10, 'APACHE-2.0': 10, 'APACHE-2': 10,
    'BSD': 9, 'BSD-2': 9, 'BSD-3': 9, 'ISC': 9,
    'UNLICENSE': 9, 'CC0-1.0': 9,
    'GPL-3.0': 7, 'GPL-2.0': 7, 'LGPL': 7, 'LGPL-2.1': 7, 'AGPL-3.0': 7,
    'MPL-2.0': 7,
}

# 来源信任度（skills.sh）
SOURCE_TRUST = {
    'vercel-labs': 10, 'vercel': 10,
    'anthropic': 10, 'anthropics': 10,
    'microsoft': 9, 'google': 9, 'google-labs': 9,
    'supabase': 8, 'remotion-dev': 8,
    'mattpocock': 7,
}

# 知名组织名单
WELL_KNOWN_ORGS = {
    'vercel', 'vercel-labs', 'anthropic', 'anthropics', 'microsoft',
    'google', 'google-labs', 'openai', 'meta', 'aws', 'amazon',
    'github', 'gitlab', 'supabase', 'netlify', 'cloudflare',
    'nousresearch', 'sickn33', 'affaan-m',
    'prompt-security', 'codejunkie99', 'anysearch-ai',
    'zhayujie', 'op7418', 'jnMetaCode', 'mukul975',
    'wanshuiyin', 'liyupi', 'EXboys', 'ksimback',
    'kepano', 'conorbronsdon', 'AMAP-ML', 'jeecgboot',
    'outsourc-e', 'ComposioHQ', '0xNyk',
    'activepieces', 'headroom', 'mcp-use',
}


def calc_popularity(value: float, max_value: float) -> float:
    """计算受欢迎度（0-10），对数归一化"""
    if max_value <= 0 or value <= 0:
        return 0
    # 使用对数比例，避免头部项目碾压长尾
    ratio = value / max_value
    score = min(10, ratio * 10)
    return round(score, 1)


def calc_security_github(license_id: str) -> float:
    """GitHub 安全评分"""
    if not license_id:
        return 2
    return LICENSE_SCORE.get(license_id.upper(), 5)


def calc_security_skillssh(source: str) -> float:
    """skills.sh 安全评分（根据来源信任度）"""
    org = source.split('/')[0] if '/' in source else source
    return SOURCE_TRUST.get(org, 6)


def calc_developer_github(full_name: str, followers: int = 0) -> float:
    """GitHub 开发者实力评分"""
    org = full_name.split('/')[0] if '/' in full_name else ''
    if org in WELL_KNOWN_ORGS:
        return 10 if followers > 10000 else 9
    if followers > 5000:
        return 8
    if followers > 1000:
        return 7
    if followers > 100:
        return 6
    return 5


def calc_developer_skillssh(source: str) -> float:
    """skills.sh 开发者实力"""
    org = source.split('/')[0] if '/' in source else source
    if org in WELL_KNOWN_ORGS:
        return 9
    return 6


def calc_freshness(updated: str) -> float:
    """维护活跃度评分"""
    from datetime import datetime as dt
    try:
        updated_dt = dt.strptime(updated, '%Y-%m-%d')
        days_old = (dt.now() - updated_dt).days
    except:
        return 3

    if days_old < 7: return 10
    if days_old < 30: return 9
    if days_old < 60: return 8
    if days_old < 90: return 7
    if days_old < 180: return 6
    if days_old < 365: return 4
    if days_old < 730: return 2
    return 1


def compute_final_score(pop_score: float, sec_score: float, dev_score: float, fresh_score: float) -> float:
    """计算最终综合评分"""
    score = (
        pop_score * WEIGHTS['popularity'] +
        sec_score * WEIGHTS['security'] +
        dev_score * WEIGHTS['developer'] +
        fresh_score * WEIGHTS['freshness']
    )
    return round(min(10, max(1, score)), 1)


def normalize_scores(skills: list[dict], source_key: str, value_key: str):
    """在同一个数据源内归一化分数"""
    # 找出当前数据源的最大值
    max_val = 0
    for s in skills:
        if s.get('source') == source_key:
            val = s.get(value_key, 0) or 0
            if val > max_val:
                max_val = val

    if max_val <= 0:
        return

    # 重新计算所有人的 popularity
    for s in skills:
        if s.get('source') == source_key:
            val = s.get(value_key, 0) or 0
            pop = calc_popularity(val, max_val)
            # 重新计算总分
            sec = s.get('_sec_score', 5)
            dev = s.get('_dev_score', 5)
            fresh = calc_freshness(s.get('updated', ''))
            s['score'] = compute_final_score(pop, sec, dev, fresh)
