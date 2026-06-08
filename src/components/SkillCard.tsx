'use client';

import { Skill } from '@/types/skill';
import { useState } from 'react';

export default function SkillCard({ skill }: { skill: Skill }) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(skill.install);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLiked(!liked);
  };

  const scoreColor = (score: number) => {
    if (score >= 8.5) return { color: '#22c55e', border: '3px solid #22c55e' };
    if (score >= 7) return { color: '#eab308', border: '3px solid #eab308' };
    return { color: '#ef4444', border: '3px solid #ef4444' };
  };

  const platformColor = (platform: string) => {
    if (platform.includes('hermes')) return { bg: 'rgba(139,92,246,0.12)', color: '#a78bfa', border: 'rgba(139,92,246,0.2)' };
    if (platform.includes('claude')) return { bg: 'rgba(245,158,11,0.12)', color: '#fbbf24', border: 'rgba(245,158,11,0.2)' };
    if (platform.includes('github') || platform.includes('codex')) return { bg: 'rgba(34,197,94,0.12)', color: '#4ade80', border: 'rgba(34,197,94,0.2)' };
    return { bg: 'var(--accent-glow)', color: 'var(--accent-light)', border: 'rgba(139,92,246,0.2)' };
  };

  const pc = platformColor(skill.platforms[0] || '');
  const sc = scoreColor(skill.score);

  return (
    <div
      className="skill-card group"
      style={{
        background: 'var(--gradient-card)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: 24,
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
      }}
      onClick={() => window.open(skill.url, '_blank')}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.borderColor = 'var(--accent)';
        e.currentTarget.style.boxShadow = '0 12px 40px rgba(139, 92, 246, 0.1)';
        // 顶部装饰条滑入
        const bar = e.currentTarget.querySelector('.card-top-bar') as HTMLElement;
        if (bar) bar.style.transform = 'scaleX(1)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = '';
        e.currentTarget.style.borderColor = 'var(--border)';
        e.currentTarget.style.boxShadow = 'none';
        const bar = e.currentTarget.querySelector('.card-top-bar') as HTMLElement;
        if (bar) bar.style.transform = 'scaleX(0)';
      }}
    >
      {/* hover时顶部出现3px渐变紫条 */}
      <div
        className="card-top-bar"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 3,
          background: 'linear-gradient(90deg, #8b5cf6, #6366f1, #8b5cf6)',
          transform: 'scaleX(0)',
          transformOrigin: 'left',
          transition: 'transform 0.3s ease',
        }}
      />

      {/* 第一行：名称 + 评分环 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 2, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            {skill.name}
            <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text-muted)' }}>v1.0</span>
          </h3>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 4 }}>
            {/* 平台标签 */}
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 4,
              padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 500,
              background: pc.bg, color: pc.color, border: `1px solid ${pc.border}`,
            }}>
              {skill.platforms.join(' / ')}
            </span>
            {/* 许可标签 */}
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 4,
              padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 500,
              background: 'rgba(34,197,94,0.1)', color: '#4ade80', border: '1px solid rgba(34,197,94,0.2)',
            }}>
              {skill.license}
            </span>
          </div>
        </div>
        {/* 评分环 44px */}
        <div style={{
          width: 44, height: 44, borderRadius: '50%', display: 'flex',
          alignItems: 'center', justifyContent: 'center', fontWeight: 700,
          fontSize: 14, flexShrink: 0, marginLeft: 12,
          color: sc.color, border: sc.border,
        }}>
          {skill.score}
        </div>
      </div>

      {/* 利益点（紫色高亮 15px/600） */}
      <p style={{
        fontSize: 15, fontWeight: 600, marginBottom: 8, lineHeight: 1.4,
        color: 'var(--accent-light)',
      }}>
        <i className="fas fa-star" style={{ fontSize: 10, marginRight: 4 }}></i>
        {skill.benefit}
      </p>

      {/* 描述（灰色 13px） */}
      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 12 }}>
        {skill.description}
      </p>

      {/* 标签行 */}
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 12 }}>
        {skill.tags.map(t => (
          <span key={t} className="tag" style={{ fontSize: 12, fontWeight: 500 }}>#{t}</span>
        ))}
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 4,
          padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 500,
          background: 'rgba(139,92,246,0.08)', color: 'var(--text-muted)', border: '1px solid var(--border)',
        }}>
          {skill.category}
        </span>
      </div>

      {/* 数据行：GitHub星 + 下载 + 日期 + 点赞 */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: 8, marginBottom: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 13, color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <i className="fab fa-github"></i> {(skill.stars / 1000).toFixed(1)}k
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <i className="fas fa-download"></i> {(skill.downloads / 1000).toFixed(1)}k
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <i className="fas fa-calendar"></i> {skill.updated}
          </span>
        </div>
        <button
          onClick={handleLike}
          style={{
            cursor: 'pointer', transition: 'all 0.2s ease',
            color: liked ? '#ef4444' : 'var(--text-muted)',
            transform: liked ? 'scale(1.2)' : 'scale(1)',
            background: 'none', border: 'none', fontSize: 14, padding: 0,
          }}
          onMouseEnter={e => { if (!liked) e.currentTarget.style.color = '#ef4444'; }}
          onMouseLeave={e => { if (!liked) e.currentTarget.style.color = 'var(--text-muted)'; }}
        >
          <i className="fas fa-heart"></i>
        </button>
      </div>

      {/* 安装命令 */}
      <div
        onClick={handleCopy}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
          padding: '8px 14px', borderRadius: 8,
          background: 'var(--bg-primary)', border: '1px solid var(--border)',
          color: 'var(--text-secondary)',
          fontFamily: "'Courier New', monospace", fontSize: 12,
          cursor: 'pointer', transition: 'all 0.2s ease',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.borderColor = 'var(--accent)';
          e.currentTarget.style.background = 'var(--accent-glow)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.borderColor = 'var(--border)';
          e.currentTarget.style.background = 'var(--bg-primary)';
        }}
        title="点击复制安装命令"
      >
        <code style={{ overflow: 'hidden', textOverflow: 'ellipsis', fontSize: 12, fontFamily: "'Courier New', monospace" }}>
          $ {skill.install}
        </code>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          {copied && <span style={{ fontSize: 12, color: '#22c55e' }}>✅ 已复制</span>}
          <i className="fas fa-copy" style={{ color: 'var(--accent-light)' }}></i>
        </span>
      </div>
    </div>
  );
}
