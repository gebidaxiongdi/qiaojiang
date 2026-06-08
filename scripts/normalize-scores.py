"""
巧匠 · 跨平台评分归一化
读取 skills.json，按平台归一化评分，确保公平
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from scoring import (
    calc_popularity, calc_security_github, calc_security_skillssh,
    calc_developer_github, calc_developer_skillssh,
    calc_freshness, compute_final_score
)

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'skills.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        skills = json.load(f)

    print(f'📊 共 {len(skills)} 个 Skill')

    # ====== 第一步：计算各平台统计量 ======
    github_skills = [s for s in skills if s.get('source') == 'github']
    skillssh_skills = [s for s in skills if s.get('source') == 'skills-sh']

    # GitHub: max_stars
    github_max_stars = max((s.get('stars', 0) or 0) for s in github_skills) if github_skills else 1
    # skills.sh: max_downloads (installs)
    skillssh_max_dls = max((s.get('downloads', 0) or 0) for s in skillssh_skills) if skillssh_skills else 1

    print(f'  GitHub 最高星: {github_max_stars}')
    print(f'  skills.sh 最高安装: {skillssh_max_dls}')

    # ====== 第二步：逐项评分 ======
    for s in skills:
        source = s.get('source', 'github')

        if source == 'github':
            stars = s.get('stars', 0) or 0
            full_name = s.get('url', '').replace('https://github.com/', '')
            license_id = s.get('license', '')

            pop_score = calc_popularity(stars, github_max_stars)
            sec_score = calc_security_github(license_id)
            dev_score = calc_developer_github(full_name, stars)
        else:
            dls = s.get('downloads', 0) or 0
            source_str = s.get('url', '').replace('https://github.com/', '')

            pop_score = calc_popularity(dls, skillssh_max_dls)
            sec_score = calc_security_skillssh(source_str or 'unknown')
            dev_score = calc_developer_skillssh(source_str or 'unknown')

        fresh_score = calc_freshness(s.get('updated', ''))
        final_score = compute_final_score(pop_score, sec_score, dev_score, fresh_score)

        s['score'] = final_score
        # 存中间分用于调试
        s['_scores'] = {
            'popularity': pop_score,
            'security': sec_score,
            'developer': dev_score,
            'freshness': fresh_score,
        }

    # ====== 第三步：保存 ======
    # 按评分降序
    skills.sort(key=lambda s: s['score'], reverse=True)

    # 清理中间分（不写到前端数据中）
    for s in skills:
        s.pop('_scores', None)

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(skills, f, ensure_ascii=False, indent=2)

    # 统计
    avg = sum(s['score'] for s in skills) / len(skills)
    print(f'\n✅ 评分归一化完成')
    print(f'   平均分: {avg:.1f}')
    print(f'   TOP 5:')
    for s in skills[:5]:
        src = s.get('source', '?')
        val = s.get('stars', s.get('downloads', 0))
        print(f'     {s["score"]}分 - {s["name"]} ({val:,}) [{src}]')

    # 检查跨平台公平性
    gh_avg = sum(s['score'] for s in skills if s.get('source') == 'github') / max(len(github_skills), 1)
    ss_avg = sum(s['score'] for s in skills if s.get('source') == 'skills-sh') / max(len(skillssh_skills), 1)
    print(f'   GitHub 平均分: {gh_avg:.1f}')
    print(f'   skills.sh 平均分: {ss_avg:.1f}')


if __name__ == '__main__':
    main()
