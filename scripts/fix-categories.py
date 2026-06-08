"""
修复分类：旧分类名称 → 新6分类映射
"""
import json
m = {
    '网站设计':'编码辅助','AI调教':'系统工具','学习必备':'信息搜索',
    '办公必备':'沟通协作','自媒体人':'内容创作','图片生成':'内容创作',
    '视频制作':'内容创作','电商带货':'内容创作','数据分析':'信息搜索',
    '其他':'系统工具','编程':'编码辅助','文档':'沟通协作','记忆':'系统工具',
    '搜索':'信息搜索','写作':'内容创作','安全':'系统工具',
}
with open('src/data/skills.json') as f:
    skills = json.load(f)
for s in skills:
    if s['category'] in m:
        s['category'] = m[s['category']]
with open('src/data/skills.json','w') as f:
    json.dump(skills, f, ensure_ascii=False, indent=2)
print(f'分类修复完成: {len(skills)}个Skill')
