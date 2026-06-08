#!/usr/bin/env python3
"""
ECC → 巧匠 skill 导入脚本
从 ECC 的 skills/ 目录读取 SKILL.md，转化为巧匠的 JSON 格式
"""

import json
import os
import re
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ========== 配置 ==========
# 优先级：命令行参数 > 环境变量 > 默认值
_DEFAULT_ECC = os.environ.get("ECC_SKILLS_DIR", r"C:\Users\49053\ECC\skills")

parser = argparse.ArgumentParser(description="ECC → 巧匠 Skill 导入")
parser.add_argument("--ecc-path", help="ECC skills 目录路径", default=_DEFAULT_ECC)
args = parser.parse_args()

ECC_SKILLS_DIR = Path(args.ecc_path)
QIAOJIANG_DATA = Path(r"C:\Users\49053\qiaojiang\src\data\skills.json")
OUTPUT_FILE = Path(r"C:\Users\49053\qiaojiang\src\data\skills.json")

# ECC 内部 skill（不导入巧匠）
ECC_INTERNAL_SKILLS = {
    "configure-ecc", "ecc-guide", "ecc-tools-cost-audit", "agent-sort",
    "hookify-rules", "rules-distill", "skill-comply", "skill-scout",
    "skill-stocktake", "hermes-imports", "openclaw-persona-forge",
    "orch-add-feature", "orch-build-mvp", "orch-change-feature",
    "orch-fix-defect", "orch-pipeline", "orch-refine-code",
    "plan-orchestrate", "council", "ck", "nanoclaw-repl",
    "agentic-os", "dmux-workflows", "team-agent-orchestration",
    "enterprise-agent-ops", "uncloud", "dynamic-workflow-mode",
}

# skill 名 → 巧匠分类 映射（自动匹配不到的回退策略）
CATEGORY_KEYWORD_MAP = {
    "前端开发": ["frontend", "ui-demo", "design-system", "react", "css",
                "vue", "vite", "nextjs", "tailwind", "ui-to", "liquid-glass",
                "motion", "accessibility", "frontend-a11y",
                "make-interfaces", "inherit-legacy", "angular",
                "compose-multiplatform", "swiftui"],
    "后端开发": ["backend-patterns", "api-design", "api-connector",
                "docker-patterns", "kubernetes-patterns", "deployment-patterns",
                "nestjs", "fastapi", "dotnet", "laravel", "django",
                "springboot", "quarkus", "jpa", "mysql", "postgres",
                "redis", "prisma", "hexagonal-architecture",
                "mcp-server", "bun-runtime", "flox-environments",
                "nuxt4", "jira-integration"],
    "AI调教": ["prompt-optimizer", "safety-guard", "gateguard",
               "agent-eval", "agent-harness", "agent-introspection",
               "agent-architecture-audit", "agent-payment",
               "autonomous-loops", "autonomous-agent",
               "continuous-learning", "context-budget",
               "cost-aware-llm", "token-budget-advisor",
               "eval-harness", "verification-loop", "benchmark",
               "intent-driven", "ralphinho", "santa-method",
               "ai-first-engineering", "ai-regression-testing",
               "gan-style-harness", "claude-devfleet",
               "iterative-retrieval", "prompt-optimizer"],
    "学习必备": ["deep-research", "scientific", "documentation-lookup",
                "knowledge-ops", "codebase-onboarding", "code-tour",
                "architecture-decision", "blueprint", "coding-standards",
                "search-first", "exa-search", "codehealth",
                "plankton-code-quality", "product-capability",
                "product-lens", "strategic-compact",
                "benchmark-optimization", "regex-vs-llm"],
    "办公必备": ["email", "google-workspace", "messages-ops", "unified-notifications",
                "terminal-ops", "project-flow-ops", "workspace-surface",
                "automation-audit", "customer-billing", "finance-billing",
                "returns-reverse", "inventory-demand", "logistics-exception",
                "production-scheduling", "quality-nonconformance",
                "carrier-relationship", "energy-procurement",
                "customs-trade", "connections-optimizer",
                "github-ops", "crosspost", "lead-intelligence",
                "marketing-campaign", "team-builder"],
    "自媒体人": ["article-writing", "content-engine", "social-graph",
                "investor-materials", "investor-outreach",
                "market-research", "seo", "brand-voice",
                "social-publisher", "visa-doc-translate"],
    "视频制作": ["manim-video", "remotion-video-creation", "video-editing",
                "videodb", "fal-ai-media"],
    "数据分析": ["clickhouse-io", "postgres-patterns", "mysql-patterns",
                "database-migrations", "redis-patterns", "prisma-patterns",
                "scientific-db", "scientific-pkg", "data-scraper",
                "data-throughput", "recsys-pipeline"],
    "编程语言": ["python-patterns", "python-testing", "rust-patterns", "rust-testing",
                "golang-patterns", "golang-testing", "cpp-coding",
                "cpp-testing", "csharp-testing", "fsharp-testing",
                "java-coding", "kotlin-patterns", "kotlin-testing",
                "kotlin-coroutines", "kotlin-exposed", "kotlin-ktor",
                "dart-flutter", "flutter-dart", "swift-concurrency",
                "swift-actor", "swift-protocol", "perl-patterns",
                "perl-testing", "perl-security", "tinystruct",
                "dotnet-patterns", "nodejs-keccak256"],
    "框架教程": ["django-patterns", "django-security", "django-tdd", "django-verification",
                "django-celery", "springboot-patterns", "springboot-security",
                "springboot-tdd", "springboot-verification",
                "laravel-patterns", "laravel-security", "laravel-tdd",
                "laravel-verification", "laravel-plugin",
                "quarkus-patterns", "quarkus-security", "quarkus-tdd",
                "quarkus-verification", "fastapi-patterns",
                "nestjs-patterns", "pytorch-patterns",
                "react-patterns", "react-testing", "react-performance",
                "angular-developer", "mle-workflow"],
    "网络安全": ["security-review", "security-scan", "security-bounty-hunter",
                "hipaa-compliance", "healthcare-phi", "defi-amm-security",
                "llm-trading-agent", "network-bgp", "network-config",
                "network-interface", "cisco-ios", "netmiko-ssh",
                "homelab-network", "homelab-pihole", "homelab-vlan",
                "homelab-wireguard", "production-audit",
                "repo-scan", "error-handling"],
    "电商带货": ["payment", "x402", "agent-payment"],
    "图片生成": ["ios-icon-gen", "frontend-slides", "nutrient",
                "dashboard-builder", "ui-demo"],
    "测试工具": ["tdd-workflow", "e2e-testing", "browser-qa",
                "windows-desktop-e2e", "canary-watch",
                "agent-eval"],
    "其他": [],
}

# 分类优先级（第一个匹配到的生效，但使用评分制确保最相关的分类胜出）
CATEGORY_PRIORITY = [
    "电商带货", "视频制作", "图片生成", "网络安全",
    "编程语言", "框架教程", "前端开发", "后端开发",
    "数据分析", "测试工具", "AI调教", "学习必备",
    "办公必备", "自媒体人", "其他",
]

def parse_skill_md(filepath):
    """解析 SKILL.md，提取 frontmatter 和正文"""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    
    # 提取 frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return None, content
    
    fm_text = fm_match.group(1)
    frontmatter = {}
    for line in fm_text.strip().split('\n'):
        m = re.match(r'^(\w+):\s*(.*)', line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            frontmatter[key] = value
    
    body = content[fm_match.end():].strip()
    return frontmatter, body


def extract_benefit(name, description, body):
    """从 description 和 body 生成中文利益点"""
    name_lower = name.lower()
    
    # 根据 skill 类型生成针对性利益点
    benefit_map = {
        "accessibility": "让AI帮你检查网站是否对残障人士友好，符合无障碍标准",
        "agent-architecture-audit": "让AI给你的AI应用做全面体检，诊断12层架构问题",
        "agent-eval": "让AI帮你对比不同编码助手的表现，选出最省钱高效的",
        "agent-harness-construction": "让AI帮你优化工具定义和操作空间，提高任务完成率",
        "agentic-engineering": "让AI以工程师思维工作——先评估、再分解、再执行",
        "agent-introspection-debugging": "AI出错了？让它自己诊断自己，自动修复",
        "agent-payment-x402": "让AI能替你花钱——按任务预算调用付费API",
        "ai-first-engineering": "让团队适应AI优先的开发模式，充分发挥AI生产力",
        "ai-regression-testing": "AI写代码容易出相同错误？让它自己检查自己",
        "android-clean-architecture": "让AI遵循Android Clean Architecture最佳实践",
        "angular-developer": "让AI成为Angular专家，写出规范的组件和模块",
        "api-connector-builder": "让AI帮你对接第三方API，不用手写HTTP请求",
        "api-design": "让AI设计RESTful API，考虑一致性、版本化、错误处理",
        "architecture-decision-records": "让AI自动记录架构决策，团队新成员一看就懂",
        "article-writing": "让AI帮你写文章，从大纲到成稿一条龙",
        "automation-audit-ops": "让AI审计你的自动化流程，找出瓶颈和风险",
        "autonomous-agent-harness": "让AI搭建自主运行的代理系统，24小时不停工",
        "autonomous-loops": "让AI在安全边界内自主循环执行，你只需监督结果",
        "backend-patterns": "让AI遵循后端最佳实践——分层、依赖注入、错误处理",
        "benchmark": "让AI帮你跑基准测试，对比不同方案的性能",
        "benchmark-optimization-loop": "让AI自动优化性能，反复测试直到达标",
        "blender-motion-state-inspection": "让AI分析Blender动画状态，调试3D运动问题",
        "blueprint": "让AI生成项目蓝图，开工前把架构想清楚",
        "brand-voice": "让AI学会你的品牌调性，所有对外内容风格统一",
        "browser-qa": "让AI自动测试网页，点点点不用你动手",
        "bun-runtime": "让AI用Bun运行时优化JavaScript项目，启动速度更快",
        "canary-watch": "让AI监控部署后的金丝雀发布，异常自动回滚",
        "carrier-relationship-management": "让AI管理物流承运商关系，跟踪合同和绩效",
        "cisco-ios-patterns": "让AI帮你配置Cisco网络设备，不用背命令",
        "claude-devfleet": "让AI管理多Claude Code实例协同工作",
        "clickhouse-io": "让AI优化ClickHouse查询，数据分析速度起飞",
        "click-path-audit": "让AI审计用户点击路径，找出转化率瓶颈",
        "codebase-onboarding": "让AI帮你理解新代码库，入职新项目更快上手",
        "codehealth-mcp": "让AI通过MCP协议检查代码健康度，持续质量监控",
        "code-tour": "让AI带你逛代码库，新手也能快速熟悉项目结构",
        "coding-standards": "让AI强制执行编码规范，团队代码风格统一",
        "compose-multiplatform-patterns": "让AI按Jetpack Compose Multiplatform最佳实践开发",
        "connections-optimizer": "让AI优化人脉网络，发现最有价值的连接",
        "content-engine": "让AI成为你的内容引擎——批量生成高质量内容",
        "content-hash-cache-pattern": "让AI用内容哈希做缓存，避免重复计算",
        "context-budget": "让AI精打细算上下文窗口，防止超出token限制",
        "continuous-agent-loop": "让AI持续运行循环任务，定时检查、自动处理",
        "continuous-learning": "让AI从每次对话中学习，越用越懂你",
        "continuous-learning-v2": "让AI持续进化——自动提取模式生成新技能",
        "cost-aware-llm-pipeline": "让AI聪明选择模型——简单任务用便宜模型，复杂任务用强模型",
        "cost-tracking": "让AI跟踪API花费，预算超标自动预警",
        "cpp-coding-standards": "让AI按C++最佳规范编码，避免内存泄漏等坑",
        "cpp-testing": "让AI给C++代码写测试，覆盖边界条件和异常路径",
        "crosspost": "让AI一键把内容同步到多个平台",
        "csharp-testing": "让AI给C#代码写单元测试，确保.NET项目质量",
        "customer-billing-ops": "让AI处理客户计费流程，自动生成账单和处理纠纷",
        "customs-trade-compliance": "让AI检查跨境贸易合规，避免海关罚款",
        "dart-flutter-patterns": "让AI遵循Dart/Flutter最佳实践，写出高质量跨平台代码",
        "dashboard-builder": "让AI帮你搭建数据仪表盘，可视化关键指标",
        "database-migrations": "让AI帮你写数据库迁移脚本，数据变更零失误",
        "data-scraper-agent": "让AI自动抓取网页数据，不用写爬虫",
        "data-throughput-accelerator": "让AI优化数据处理流水线，吞吐量翻倍",
        "deep-research": "让AI帮你做深度研究，从海量资料中提炼洞见",
        "defi-amm-security": "让AI审计DeFi自动做市商合约安全，防止黑客攻击",
        "deployment-patterns": "让AI帮你规划部署策略，蓝绿部署/滚动更新一键配置",
        "design-system": "让AI帮你构建设计系统，组件库风格一致",
        "django-celery": "让AI配置Django + Celery异步任务，后台任务自动跑",
        "django-patterns": "让AI按Django最佳实践开发——MTV模式、ORM优化",
        "django-security": "让AI检查Django应用安全，防止SQL注入和XSS",
        "django-tdd": "让AI用测试驱动开发Django应用，先写测试再写代码",
        "django-verification": "让AI验证Django功能完整性，确保API和视图正常工作",
        "docker-patterns": "让AI写出最优Dockerfile，镜像更小构建更快",
        "documentation-lookup": "让AI帮你查API文档，不用离开编辑器",
        "dotnet-patterns": "让AI按.NET最佳实践开发，写出高质量C#代码",
        "e2e-testing": "让AI给你写端到端测试，关键用户流程全覆盖",
        "email-ops": "让AI处理邮件运营——模板、发送、跟踪一条龙",
        "energy-procurement": "让AI优化能源采购策略，降低电费成本",
        "error-handling": "让AI设计错误处理方案，优雅地处理所有异常",
        "eval-harness": "让AI搭建评估框架，量化AI助手表现",
        "evm-token-decimals": "让AI处理EVM代币精度，转账计算不出错",
        "exa-search": "让AI用Exa搜索引擎找信息，比普通搜索更精准",
        "fal-ai-media": "让AI用fal.ai生成图片和视频，创意内容一键出",
        "fastapi-patterns": "让AI按FastAPI最佳实践开发，异步API性能拉满",
        "finance-billing-ops": "让AI处理财务计费流程，发票、对账、催款自动完成",
        "flox-environments": "让AI用Flox管理开发环境，依赖冲突不再愁",
        "flutter-dart-code-review": "让AI审查Flutter/Dart代码质量",
        "foundation-models-on-device": "让AI在手机上跑基础模型，离线也能用AI",
        "frontend-a11y": "让AI帮你做前端无障碍适配，覆盖所有用户",
        "frontend-design-direction": "让AI帮你确定前端设计方向，从需求到设计稿",
        "frontend-patterns": "让AI遵循前端最佳实践——组件化、状态管理、性能优化",
        "frontend-slides": "让AI帮你生成HTML幻灯片，不用PPT软件",
        "fsharp-testing": "让AI给F#函数式代码写测试",
        "gan-style-harness": "让AI用GAN生成风格化内容，创意无限",
        "gateguard": "让AI守卫代码质量门禁，不符合标准不放行",
        "github-ops": "让AI帮你管理GitHub仓库——Issue、PR、Release全自动",
        "git-workflow": "让AI优化Git工作流，合并冲突少一半",
        "golang-patterns": "让AI按Go语言最佳实践开发，并发安全优雅",
        "golang-testing": "让AI给Go代码写测试，覆盖goroutine并发场景",
        "google-workspace-ops": "让AI操作Google Workspace——邮件、日历、文档全搞定",
        "healthcare-cdss-patterns": "让AI遵循医疗临床决策支持系统规范",
        "healthcare-emr-patterns": "让AI处理电子病历数据，符合医疗行业标准",
        "healthcare-eval-harness": "让AI评估医疗AI模型的安全性和效果",
        "healthcare-phi-compliance": "让AI保护患者隐私数据，符合HIPAA法规",
        "hexagonal-architecture": "让AI按六边形架构设计，业务逻辑与外部解耦",
        "hipaa-compliance": "让AI确保应用符合HIPAA医疗数据隐私法规",
        "homelab-network-readiness": "让AI帮你规划家庭实验室网络架构",
        "homelab-network-setup": "让AI帮你搭建家庭实验室网络",
        "homelab-pihole-dns": "让AI配置Pi-hole DNS，全家去广告",
        "homelab-vlan-segmentation": "让AI划分VLAN网络，家庭网络更安全",
        "homelab-wireguard-vpn": "让AI配置WireGuard VPN，远程访问家庭网络",
        "intent-driven-development": "让AI按意图驱动开发——你说要什么，它自动实现",
        "inventory-demand-planning": "让AI预测库存需求，缺货积压都减少",
        "investor-materials": "让AI帮你准备投资人材料，路演PPT和商业计划书",
        "investor-outreach": "让AI帮你写投资人沟通邮件，提高回复率",
        "ios-icon-gen": "让AI生成iOS应用图标，不用请设计师",
        "iterative-retrieval": "让AI迭代检索信息，一次找不全就再找一次",
        "ito-basket-compare": "让AI对比预测市场篮子，找出最佳投资组合",
        "ito-data-atlas-agent": "让AI分析预测市场数据图谱",
        "ito-market-intelligence": "让AI分析预测市场情报，发现套利机会",
        "ito-trade-planner": "让AI规划预测市场交易策略",
        "java-coding-standards": "让AI按Java编码规范写代码，团队风格一致",
        "jira-integration": "让AI与Jira集成——创建任务、更新进度、生成报告",
        "jpa-patterns": "让AI按JPA最佳实践操作数据库，ORM性能优化",
        "knowledge-ops": "让AI管理团队知识库，信息不丢失",
        "kotlin-coroutines-flows": "让AI用Kotlin协程和Flow处理异步，代码更简洁",
        "kotlin-exposed-patterns": "让AI用Kotlin Exposed框架操作数据库",
        "kotlin-ktor-patterns": "让AI按Ktor最佳实践开发后端服务",
        "kotlin-patterns": "让AI按Kotlin最佳实践开发，空安全、扩展函数用起来",
        "kotlin-testing": "让AI给Kotlin代码写测试",
        "kubernetes-patterns": "让AI帮你管理K8s集群——部署、扩缩容、配置",
        "laravel-patterns": "让AI按Laravel最佳实践开发，优雅的PHP代码",
        "laravel-plugin-discovery": "让AI自动发现和配置Laravel插件",
        "laravel-security": "让AI检查Laravel应用安全",
        "laravel-tdd": "让AI用测试驱动开发Laravel应用",
        "laravel-verification": "让AI验证Laravel功能完整性",
        "latency-critical-systems": "让AI优化延迟敏感系统，响应时间降到最低",
        "lead-intelligence": "让AI分析潜在客户情报，销售更有针对性",
        "liquid-glass-design": "让AI实现毛玻璃UI效果，界面更有质感",
        "llm-trading-agent-security": "让AI审计交易AI的安全性，防止金钱损失",
        "logistics-exception-management": "让AI处理物流异常——丢件、延迟自动响应",
        "make-interfaces-feel-better": "让AI改善界面交互体验，用户用着更顺手",
        "manim-video": "让AI生成3Blue1Brown风格的数学动画视频",
        "marketing-campaign": "让AI策划和执行营销活动，从文案到渠道一键搞定",
        "market-research": "让AI做市场调研，竞品分析、趋势预测",
        "mcp-server-patterns": "让AI帮你搭建MCP服务器，扩展AI工具生态",
        "messages-ops": "让AI管理消息队列，确保消息不丢失不重复",
        "mle-workflow": "让AI按ML工程最佳实践——实验追踪、模型评估、部署",
        "motion-advanced": "让AI实现高级动效，页面动感十足",
        "motion-foundations": "让AI实现基础动效，界面丝滑流畅",
        "motion-patterns": "让AI按动效最佳实践做交互动画",
        "motion-ui": "让AI给UI加过渡动画，用户体验提升",
        "mysql-patterns": "让AI优化MySQL查询和表设计，数据库性能拉满",
        "nestjs-patterns": "让AI按NestJS最佳实践开发后端，模块化、依赖注入",
        "netmiko-ssh-automation": "让AI自动配置网络设备，SSH批量操作",
        "network-bgp-diagnostics": "让AI诊断BGP网络故障",
        "network-config-validation": "让AI验证网络配置正确性",
        "network-interface-health": "让AI监控网络接口健康状态",
        "nextjs-turbopack": "让AI用Next.js Turbopack加速开发，热更新飞快",
        "nodejs-keccak256": "让AI处理Node.js keccak256哈希计算",
        "nutrient-document-processing": "让AI处理文档——PDF解析、格式转换",
        "nuxt4-patterns": "让AI按Nuxt 4最佳实践开发Vue应用",
        "parallel-execution-optimizer": "让AI并行执行任务，速度翻倍",
        "perl-patterns": "让AI按Perl最佳实践写脚本",
        "perl-security": "让AI检查Perl代码安全",
        "perl-testing": "让AI给Perl代码写测试",
        "plankton-code-quality": "让AI检查代码质量，小问题自动修复",
        "postgres-patterns": "让AI优化PostgreSQL——索引、查询、分区全搞定",
        "prediction-market-oracle-research": "让AI研究预测市场预言机数据",
        "prediction-market-risk-review": "让AI评估预测市场风险",
        "prisma-patterns": "让AI用Prisma操作数据库，类型安全不出错",
        "product-capability": "让AI梳理产品能力清单",
        "production-audit": "让AI审计生产环境——性能、安全、成本全覆盖",
        "production-scheduling": "让AI优化生产排程，产能利用率最大化",
        "product-lens": "让AI从用户视角分析产品",
        "project-flow-ops": "让AI管理项目流程，任务跟踪自动更新",
        "prompt-optimizer": "让AI优化你的提示词，输出质量更高",
        "python-patterns": "让AI按Python最佳实践开发，代码Pythonic",
        "python-testing": "让AI给Python代码写测试，pytest全覆盖",
        "pytorch-patterns": "让AI按PyTorch最佳实践训练模型",
        "quality-nonconformance": "让AI处理质量不合格报告",
        "quarkus-patterns": "让AI按Quarkus最佳实践开发Java微服务",
        "quarkus-security": "让AI检查Quarkus应用安全",
        "quarkus-tdd": "让AI用测试驱动开发Quarkus应用",
        "quarkus-verification": "让AI验证Quarkus功能完整性",
        "react-patterns": "让AI按React最佳实践开发，Hooks用对、性能优化",
        "react-performance": "让AI优化React性能，减少不必要的重渲染",
        "react-testing": "让AI给React组件写测试",
        "recsys-pipeline-architect": "让AI设计推荐系统架构",
        "recursive-decision-ledger": "让AI记录递归决策过程，复杂逻辑可追溯",
        "redis-patterns": "让AI优化Redis使用——缓存、队列、分布式锁",
        "regex-vs-llm-structured-text": "让AI判断用正则还是LLM提取结构化文本",
        "remotion-video-creation": "让AI用React代码生成视频，编程做视频",
        "repo-scan": "让AI扫描代码仓库，发现潜在问题",
        "research-ops": "让AI管理研究流程，文献、实验、笔记全记录",
        "returns-reverse-logistics": "让AI处理退货逆向物流",
        "rust-patterns": "让AI按Rust最佳实践开发，内存安全零成本抽象",
        "rust-testing": "让AI给Rust代码写测试",
        "safety-guard": "让AI做安全护栏，防止危险操作",
        "santa-method": "让AI用SANTA方法逐步推理，复杂问题也不出错",
        "scientific-db-pubmed-database": "让AI查询PubMed医学文献数据库",
        "scientific-db-uspto-database": "让AI查询USPTO专利数据库",
        "scientific-pkg-gget": "让AI用gget工具分析生物信息学数据",
        "scientific-thinking-literature-review": "让AI做文献综述，自动总结研究进展",
        "scientific-thinking-scholar-evaluation": "让AI评估学术论文质量",
        "search-first": "让AI搜索优先——遇到问题先查信息再回答",
        "security-bounty-hunter": "让AI帮你找安全漏洞，挖漏洞赚赏金",
        "security-review": "让AI审查代码安全，发现潜在漏洞",
        "security-scan": "让AI做全面安全扫描，1282项检查全覆盖",
        "seo": "让AI优化网站SEO，搜索排名往上涨",
        "social-graph-ranker": "让AI分析社交关系图谱",
        "social-publisher": "让AI自动发布内容到社交平台",
        "springboot-patterns": "让AI按Spring Boot最佳实践开发Java后端",
        "springboot-security": "让AI检查Spring Boot应用安全",
        "springboot-tdd": "让AI用测试驱动开发Spring Boot应用",
        "springboot-verification": "让AI验证Spring Boot功能完整性",
        "strategic-compact": "让AI帮你做战略规划",
        "swift-actor-persistence": "让AI用Swift Actor做数据持久化，线程安全",
        "swift-concurrency-6-2": "让AI用Swift 6.2并发特性写出安全异步代码",
        "swift-protocol-di-testing": "让AI用协议依赖注入测试Swift代码",
        "swiftui-patterns": "让AI按SwiftUI最佳实践开发iOS应用",
        "tdd-workflow": "让AI用TDD流程开发——红绿重构循环",
        "team-builder": "让AI帮你组建团队，匹配角色和技能",
        "terminal-ops": "让AI管理终端操作——命令历史、别名、自动化",
        "tinystruct-patterns": "让AI用TinyStruct框架开发",
        "token-budget-advisor": "让AI建议token预算，防止超支",
        "ui-demo": "让AI快速生成UI原型，想法变可交互页面",
        "ui-to-vue": "让AI把设计稿转成Vue组件",
        "unified-notifications-ops": "让AI统一管理所有通知，不遗漏重要消息",
        "verification-loop": "让AI反复验证——做完一步检查一步",
        "videodb": "让AI用VideoDB处理视频数据",
        "video-editing": "让AI剪辑视频，自动化编辑流程",
        "visa-doc-translate": "让AI翻译签证文件，表格格式不变",
        "vite-patterns": "让AI用Vite构建工具，开发体验丝滑",
        "windows-desktop-e2e": "让AI测试Windows桌面应用，自动化端到端测试",
        "workspace-surface-audit": "让AI审计工作空间配置",
        "x-api": "让AI发推、查时间线、管理X(Twitter)账号",
    }
    
    # 优先使用硬编码的利益点
    if name in benefit_map:
        return benefit_map[name]
    
    # 回退：从描述中提取
    desc = description or ""
    if isinstance(desc, str):
        desc_lower = desc.lower()
        # 尝试生成通用利益点
        if "security" in desc_lower or "audit" in desc_lower or "vulnerab" in desc_lower:
            return f"让AI帮你{desc[:60]}（自动安全检查）"
        if "test" in desc_lower or "tdd" in desc_lower:
            return f"让AI帮你{desc[:60]}（自动化测试）"
        return f"让AI帮你{desc[:60]}"
    
    return f"让AI帮你提升{name.replace('-',' ')}相关能力"


def categorize_skill(name, description, body):
    """根据名称和内容自动分类（评分制，最高分胜出）"""
    name_lower = name.lower()
    desc_lower = (description or "").lower()
    body_lower = (body or "").lower()
    name_slug = name_lower.replace("-", " ").replace("_", " ")
    
    # 评分：每个匹配得1分，名字匹配权重更高
    scores = {cat: 0 for cat in CATEGORY_PRIORITY}
    
    for cat in CATEGORY_PRIORITY:
        keywords = CATEGORY_KEYWORD_MAP.get(cat, [])
        for kw in keywords:
            kw_lower = kw.lower()
            # 名字中包含关键词 → 高权重（3分）
            if kw_lower in name_lower:
                scores[cat] += 3
            # 完整描述中包含 → 中权重（1分）
            elif kw_lower in desc_lower:
                scores[cat] += 1
            # 正文中包含 → 低权重（0.5分）
            elif len(kw_lower) > 4 and kw_lower in body_lower:
                scores[cat] += 0.5
    
    # 选最高分的
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        return best_cat
    
    return "其他"


def extract_tags(name, description, body):
    """提取标签（最多4个）"""
    name_lower = name.lower()
    desc_lower = (description or "").lower()
    combined = f"{name_lower} {desc_lower}"
    
    tag_keywords = {
        "编程": ["python", "java", "rust", "golang", "go", "cpp", "c++", 
                 "typescript", "javascript", "swift", "kotlin", "dart", "php",
                 "coding", "code", "编程", "developer", "pattern"],
        "安全": ["security", "audit", "vulnerab", "safety", "compliance",
                "hipaa", "phi", "guard", "防火墙"],
        "AI": ["agent", "llm", "ai", "model", "prompt", "autonomous",
               "learning", "intelligence", "机器学习"],
        "设计": ["design", "ui", "ux", "frontend", "motion", "accessibility",
                "css", "vue", "react", "美观"],
        "云原生": ["docker", "kubernetes", "k8s", "deploy", "cloud"],
        "数据": ["data", "database", "sql", "query", "migration", "analytics"],
        "测试": ["test", "tdd", "e2e", "verification", "qa"],
        "搜索": ["search", "research", "文献", "检索"],
        "视频": ["video", "manim", "remotion", "剪辑", "动画"],
        "移动端": ["ios", "android", "swiftui", "flutter", "mobile", "compose"],
        "后端": ["backend", "api", "server", "spring", "nestjs", "django",
                "laravel", "fastapi"],
        "办公": ["email", "notification", "workspace", "jira", "github",
                "billing", "finance"],
        "网络": ["network", "cisco", "bgp", "vlan", "vpn", "ssh"],
        "医疗": ["healthcare", "hipaa", "phi", "cdss", "emr", "clinical"],
        "金融": ["finance", "billing", "payment", "wallet", "defi", "trading"],
    }
    
    tags = set()
    for tag, kws in tag_keywords.items():
        for kw in kws:
            if kw.lower() in combined:
                tags.add(tag)
                break
        if len(tags) >= 4:
            break
    
    return list(tags) if tags else ["其他"]


def get_platforms(name, description, body):
    """判断skill适用的AI平台"""
    combined = f"{name} {description or ''} {body or ''}".lower()
    platforms = set()
    
    if "hermes" in combined:
        platforms.add("hermes")
    if "claude" in combined:
        platforms.add("claude")
    if "codex" in combined:
        platforms.add("codex")
    if "opencode" in combined or "open-code" in combined:
        platforms.add("opencode")
    if "cursor" in combined:
        platforms.add("cursor")
    if "gemini" in combined:
        platforms.add("gemini")
    if "mcp" in combined:
        platforms.add("mcp")
    
    # 默认：大部分ECC skill适用于claude和codex
    if not platforms:
        platforms = {"claude", "codex"}
    elif "mcp" in platforms and len(platforms) == 1:
        platforms.add("claude")
    
    return list(platforms)


def get_install_command(name):
    """生成安装命令"""
    return f"npx skills add {name}"


def main():
    print("=" * 60)
    print("🚀 ECC → 巧匠 Skill 导入工具")
    print("=" * 60)
    
    # 读取现有巧匠数据
    with open(QIAOJIANG_DATA, "r", encoding="utf-8") as f:
        existing_skills = json.load(f)
    
    existing_ids = {s["id"] for s in existing_skills}
    print(f"\n📊 巧匠当前: {len(existing_skills)} 个 skill")
    
    # 扫描ECC skills
    ecc_skills = []
    skipped_internal = 0
    skipped_dup = 0
    added = 0
    
    skill_dirs = sorted(os.listdir(ECC_SKILLS_DIR))
    print(f"📦 ECC skills 总数: {len(skill_dirs)}")
    
    for skill_name in skill_dirs:
        skill_path = ECC_SKILLS_DIR / skill_name
        
        if not skill_path.is_dir():
            continue
        
        # 跳过ECC内部skill
        if skill_name in ECC_INTERNAL_SKILLS:
            skipped_internal += 1
            continue
        
        # 跳过已存在的
        if skill_name in existing_ids:
            skipped_dup += 1
            continue
        
        # 读取SKILL.md
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            # 尝试其他常见文件名
            files = list(skill_path.glob("*.md"))
            if not files:
                continue
            skill_md = files[0]
        
        frontmatter, body = parse_skill_md(skill_md)
        if frontmatter is None:
            # 没有 frontmatter 也尝试解析
            body = skill_md.read_text(encoding="utf-8", errors="replace")
        
        description = ""
        if frontmatter and "description" in frontmatter:
            description = frontmatter["description"]
        
        # 提取信息
        benefit = extract_benefit(skill_name, description, body)
        category = categorize_skill(skill_name, description, body)
        tags = extract_tags(skill_name, description, body)
        platforms = get_platforms(skill_name, description, body)
        
        # 生成巧匠格式
        skill_entry = {
            "id": skill_name,
            "name": skill_name,
            "benefit": benefit,
            "description": description[:200] if description else f"ECC 生态 Skill：{skill_name}",
            "category": category,
            "score": 8.0,  # 默认评分，后续通过评分脚本调整
            "stars": 0,
            "downloads": 0,
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "install": get_install_command(skill_name),
            "license": "MIT",
            "url": f"https://github.com/affaan-m/ECC/tree/main/skills/{skill_name}",
            "tags": tags,
            "source": "ecc",
            "platforms": platforms,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "ecc_url": f"https://github.com/affaan-m/ECC/tree/main/skills/{skill_name}",
        }
        
        ecc_skills.append(skill_entry)
        added += 1
        
        if added <= 5:
            print(f"\n  ✅ [{added}] {skill_name}")
            print(f"     📝 {benefit}")
            print(f"     📂 {category} | 🏷️ {tags} | 📱 {platforms}")
    
    print(f"\n{'='*60}")
    print(f"📊 导入统计")
    print(f"   巧匠原有: {len(existing_skills)}")
    print(f"   ECC总技能: {len(skill_dirs)}")
    print(f"   跳过内部: {skipped_internal}")
    print(f"   跳过重复: {skipped_dup}")
    print(f"   ✅ 新增: {added}")
    print(f"   合并后: {len(existing_skills) + added}")
    print(f"{'='*60}")
    
    # 合并并写入
    all_skills = existing_skills + ecc_skills
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_skills, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已写入: {OUTPUT_FILE}")
    
    # 输出分类统计
    cats = {}
    for s in all_skills:
        c = s.get("category", "其他")
        cats[c] = cats.get(c, 0) + 1
    
    print(f"\n📂 分类分布:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    # 输出标签统计
    tag_count = {}
    for s in all_skills:
        for t in s.get("tags", []):
            tag_count[t] = tag_count.get(t, 0) + 1
    
    print(f"\n🏷️ Top标签:")
    for tag, count in sorted(tag_count.items(), key=lambda x: -x[1])[:10]:
        print(f"   #{tag}: {count}")


if __name__ == "__main__":
    main()
