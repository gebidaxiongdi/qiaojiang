'use client';

import { useState, useMemo, useEffect } from 'react';
import { CATEGORIES } from '@/types/skill';
import { getSkills } from '@/lib/utils';
import SkillCard from '@/components/SkillCard';
import { useTheme } from './layout';

const skills = getSkills();

export default function Home() {
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [sort, setSort] = useState<'score' | 'downloads' | 'updated'>('score');
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const filtered = useMemo(() => {
    let result = [...skills];
    if (category !== 'all') result = result.filter(s => s.category === category);
    if (search.trim()) {
      const q = search.toLowerCase().trim();
      result = result.filter(s =>
        s.name.toLowerCase().includes(q) ||
        s.benefit.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q) ||
        s.tags.some(t => t.toLowerCase().includes(q)) ||
        s.category.includes(q)
      );
    }
    if (sort === 'score') result.sort((a, b) => b.score - a.score);
    else if (sort === 'downloads') result.sort((a, b) => b.downloads - a.downloads);
    else result.sort((a, b) => b.updated.localeCompare(a.updated));
    return result;
  }, [search, category, sort]);

  if (!mounted) return null;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      {/* ====== 主题切换按钮（右下角固定） ====== */}
      <button
        onClick={toggleTheme}
        style={{
          position: 'fixed', bottom: 24, right: 24,
          width: 48, height: 48,
          borderRadius: '50%',
          background: 'var(--accent)',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          fontSize: 20,
          boxShadow: '0 4px 16px rgba(139, 92, 246, 0.4)',
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s ease',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 6px 24px rgba(139, 92, 246, 0.6)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(139, 92, 246, 0.4)';
        }}
      >
        <i className={`fas fa-${theme === 'dark' ? 'moon' : 'sun'}`}></i>
      </button>

      {/* ====== HERO 区域 ====== */}
      <div
        className="hero"
        style={{
          background: 'var(--gradient-hero)',
          padding: '60px 20px 80px',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* 浮动光晕背景 */}
        <div
          style={{
            position: 'absolute',
            top: '-50%', left: '-50%',
            width: '200%', height: '200%',
            background:
              'radial-gradient(circle at 30% 50%, var(--accent-glow) 0%, transparent 50%), ' +
              'radial-gradient(circle at 70% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 50%)',
            animation: 'qjFloat 20s ease-in-out infinite',
            pointerEvents: 'none',
          }}
        />

        <div style={{ position: 'relative', zIndex: 1, maxWidth: 800, margin: '0 auto' }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 16 }}>
            <div
              style={{
                width: 42, height: 42,
                background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                borderRadius: 12,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 22, color: 'white',
                boxShadow: '0 4px 12px rgba(139,92,246,0.3)',
              }}
            >
              <i className="fas fa-wand-magic-sparkles"></i>
            </div>
            <span
              style={{
                fontSize: 28, fontWeight: 800,
                background: 'linear-gradient(135deg, #c4b5fd, #818cf8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              巧匠
            </span>
            <span
              style={{
                fontSize: 14,
                color: 'var(--text-muted)',
                background: 'var(--accent-glow)',
                padding: '2px 10px',
                borderRadius: 12,
                border: '1px solid rgba(139,92,246,0.2)',
                fontWeight: 500,
              }}
            >
              Beta
            </span>
          </div>

          {/* 标题 */}
          <h1 className="hero-title" style={{ fontSize: 36, fontWeight: 800, marginBottom: 8, lineHeight: 1.3 }}>
            给你的 AI 装上
            <span
              style={{
                background: 'linear-gradient(135deg, #c084fc, #818cf8)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              超能力
            </span>
          </h1>

          <p style={{ fontSize: 16, color: 'var(--text-secondary)', marginBottom: 32, maxWidth: 520, margin: '0 auto 32px', lineHeight: 1.6 }}>
            搜一搜，看看有什么好玩的 Skill 能让你的 AI 更强大👇
          </p>

          {/* 搜索框 */}
          <div style={{ position: 'relative', maxWidth: 640, margin: '0 auto' }}>
            <i
              className="fas fa-search"
              style={{
                position: 'absolute', left: 20, top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
                fontSize: 16, zIndex: 2,
              }}
            />
            <input
              className="search-box"
              type="text"
              placeholder={'搜 Skill... 比如「写代码」「查资料」「做设计」'}
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                background: 'var(--bg-card)',
                border: '2px solid var(--border)',
                borderRadius: 16,
                padding: '16px 24px 16px 52px',
                width: '100%',
                color: 'var(--text-primary)',
                fontSize: 16,
                outline: 'none',
                transition: 'all 0.3s ease',
                boxShadow: 'var(--shadow)',
              }}
              onFocus={e => {
                e.currentTarget.style.borderColor = 'var(--accent)';
                e.currentTarget.style.boxShadow = '0 0 0 4px var(--accent-glow)';
              }}
              onBlur={e => {
                e.currentTarget.style.borderColor = 'var(--border)';
                e.currentTarget.style.boxShadow = 'var(--shadow)';
              }}
            />
          </div>

          {/* 热门搜索标签 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>🔥 热门：</span>
            {['代码', '安全', '搜索', '文档', '记忆'].map(tag => (
              <span
                key={tag}
                className="tag"
                onClick={() => setSearch(tag)}
                style={{ cursor: 'pointer' }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ====== 统计条（负边距 -32px） ====== */}
      <div style={{ maxWidth: 1200, margin: '-32px auto 0', padding: '0 16px', position: 'relative', zIndex: 10 }}>
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 16,
            padding: '20px 28px',
            boxShadow: 'var(--shadow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
          }}
        >
          {/* 左侧统计 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: 'var(--text-muted)' }}>
              <i className="fas fa-database" style={{ color: 'var(--accent-light)' }}></i> 收录 <strong style={{ color: 'var(--text-primary)' }}>{skills.length}</strong> 个 Skill
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: 'var(--text-muted)' }}>
              <i className="fas fa-code-branch" style={{ color: 'var(--accent-light)' }}></i> 来自 <strong style={{ color: 'var(--text-primary)' }}>4</strong> 个平台
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: 'var(--text-muted)' }}>
              <i className="fas fa-clock" style={{ color: 'var(--accent-light)' }}></i> 每 <strong style={{ color: 'var(--text-primary)' }}>6h</strong> 更新
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 13, color: 'var(--text-muted)' }}>
              <i className="fas fa-shield" style={{ color: '#22c55e' }}></i> 安全评分解锁
            </span>
          </div>
          {/* 右侧排序 */}
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>排序：</span>
            {([
              { key: 'score' as const, label: '评分', icon: 'star' },
              { key: 'downloads' as const, label: '下载', icon: 'download' },
              { key: 'updated' as const, label: '最新', icon: 'clock' },
            ]).map(s => (
              <button
                key={s.key}
                onClick={() => setSort(s.key)}
                style={{
                  padding: '6px 14px', borderRadius: 8, fontSize: 13,
                  cursor: 'pointer', transition: 'all 0.2s ease',
                  border: `1px solid ${sort === s.key ? 'var(--accent)' : 'var(--border)'}`,
                  background: sort === s.key ? 'var(--accent-glow)' : 'transparent',
                  color: sort === s.key ? 'var(--accent-light)' : 'var(--text-secondary)',
                  display: 'flex', alignItems: 'center', gap: 4,
                  fontFamily: "'Noto Sans SC', sans-serif",
                }}
              >
                <i className={`fas fa-${s.icon}`}></i> {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ====== 分类筛选 ====== */}
      <div style={{ maxWidth: 1200, margin: '24px auto', padding: '0 16px' }}>
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4, WebkitOverflowScrolling: 'touch' }}>
          <button
            onClick={() => setCategory('all')}
            style={{
              padding: '8px 20px', borderRadius: 24, fontSize: 14, fontWeight: 500,
              cursor: 'pointer', transition: 'all 0.2s ease', whiteSpace: 'nowrap',
              border: `1px solid ${category === 'all' ? 'var(--accent)' : 'var(--border)'}`,
              background: category === 'all' ? 'var(--accent)' : 'transparent',
              color: category === 'all' ? 'white' : 'var(--text-secondary)',
              fontFamily: "'Noto Sans SC', sans-serif",
            }}
          >
            ✨ 全部
          </button>
          {CATEGORIES.map(cat => (
            <button
              key={cat.key}
              onClick={() => setCategory(cat.key)}
              style={{
                padding: '8px 20px', borderRadius: 24, fontSize: 14, fontWeight: 500,
                cursor: 'pointer', transition: 'all 0.2s ease', whiteSpace: 'nowrap',
                border: `1px solid ${category === cat.key ? 'var(--accent)' : 'var(--border)'}`,
                background: category === cat.key ? 'var(--accent)' : 'transparent',
                color: category === cat.key ? 'white' : 'var(--text-secondary)',
                fontFamily: "'Noto Sans SC', sans-serif",
              }}
              onMouseEnter={e => {
                if (category !== cat.key) {
                  e.currentTarget.style.borderColor = 'var(--accent)';
                  e.currentTarget.style.color = 'var(--accent-light)';
                  e.currentTarget.style.background = 'var(--accent-glow)';
                }
              }}
              onMouseLeave={e => {
                if (category !== cat.key) {
                  e.currentTarget.style.borderColor = 'var(--border)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                  e.currentTarget.style.background = 'transparent';
                }
              }}
            >
              {cat.icon} {cat.key}
            </button>
          ))}
        </div>
      </div>

      {/* ====== Skill 卡片网格 ====== */}
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px 80px' }}>
        {filtered.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filtered.map(s => (
              <SkillCard key={s.id} skill={s} />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>没找到相关 Skill</h3>
            <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>试试换个关键词搜索吧～</p>
          </div>
        )}
      </main>

      {/* ====== Footer ====== */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '32px 16px', textAlign: 'center' }}>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.8 }}>
          <i className="fas fa-wand-magic-sparkles" style={{ color: 'var(--accent-light)' }}></i> 巧匠 · AI Skill 推荐站
          <span style={{ margin: '0 8px' }}>|</span>
          数据来源：GitHub / skills.sh / Dify Marketplace
          <br />
          <span style={{ fontSize: 12 }}>发现侵权内容？<a href="#" style={{ color: 'var(--accent-light)' }}>联系我们</a>，24h内删除</span>
        </p>
      </footer>
    </div>
  );
}
