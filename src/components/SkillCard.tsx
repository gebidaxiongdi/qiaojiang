"use client";

import { useState } from "react";
import type { Skill } from "@/types/skill";

const platformColors: Record<string, { bg: string; color: string; border: string }> = {
  hermes: { bg: "rgba(139,92,246,0.12)", color: "#a78bfa", border: "rgba(139,92,246,0.2)" },
  claude: { bg: "rgba(245,158,11,0.12)", color: "#fbbf24", border: "rgba(245,158,11,0.2)" },
  codex: { bg: "rgba(34,197,94,0.12)", color: "#4ade80", border: "rgba(34,197,94,0.2)" },
};

function getPlatformStyle(platform: string) {
  for (const [key, val] of Object.entries(platformColors)) {
    if (platform.includes(key)) return val;
  }
  return { bg: "var(--accent-glow)", color: "var(--accent-light)", border: "rgba(139,92,246,0.2)" };
}

const HOT_THRESHOLD = 100000;

export default function SkillCard({ skill }: { skill: Skill }) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(skill.install);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* fallback */ }
  };

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLiked(!liked);
  };

  const isHot = skill.downloads >= HOT_THRESHOLD;

  return (
    <div
      className="skill-card group"
      style={{
        background: "var(--gradient-card)",
        border: "1px solid var(--border)",
        borderRadius: 16,
        overflow: "hidden",
        transition: "all 0.3s ease",
        position: "relative",
        display: "flex",
        flexDirection: "column",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "var(--shadow)";
        e.currentTarget.style.borderColor = "var(--accent)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
        e.currentTarget.style.borderColor = "var(--border)";
      }}
    >
      {isHot && (
        <div
          style={{
            position: "absolute", top: 12, right: 12,
            background: "linear-gradient(135deg, #f59e0b, #ef4444)",
            color: "white", fontSize: 11, fontWeight: 700,
            padding: "3px 10px", borderRadius: 20, zIndex: 2,
            boxShadow: "0 2px 8px rgba(239,68,68,0.4)",
            display: "flex", alignItems: "center", gap: 4,
          }}
        >
          🔥 热门推荐
        </div>
      )}

      <div style={{ padding: 20, flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Name + platforms */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {skill.name}
          </h3>
          {skill.platforms?.map((p: string) => {
            const ps = getPlatformStyle(p);
            return (
              <span key={p} style={{ fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 10, background: ps.bg, color: ps.color, border: `1px solid ${ps.border}`, whiteSpace: "nowrap", flexShrink: 0 }}>
                {p}
              </span>
            );
          })}
        </div>

        {/* Downloads bar */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
          <i className="fas fa-download" style={{ fontSize: 12, color: "var(--accent-light)" }}></i>
          <div style={{ flex: 1, height: 6, background: "var(--bg-primary)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{ width: `${Math.min(100, (skill.downloads / 2000000) * 100)}%`, height: "100%", background: "linear-gradient(90deg, var(--accent), #6366f1)", borderRadius: 3, transition: "width 0.6s ease" }} />
          </div>
          <span style={{ fontSize: 12, fontWeight: 600, color: "var(--accent-light)", whiteSpace: "nowrap" }}>
            {(skill.downloads / 10000).toFixed(1)}万
          </span>
        </div>

        {/* Benefit — 一句大白话，小白看完就知道这是干啥的 */}
        <p style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, lineHeight: 1.5, color: "var(--accent-light)" }}>
          <i className="fas fa-star" style={{ fontSize: 10, marginRight: 4 }}></i>
          {skill.benefit}
        </p>

        {/* Tags */}
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: 12, marginTop: "auto" }}>
          {skill.tags?.slice(0, 3).map((t: string) => (
            <span key={t} className="tag" style={{ fontSize: 11 }}>#{t}</span>
          ))}
          <span style={{ display: "inline-flex", alignItems: "center", gap: 4, padding: "3px 10px", borderRadius: 20, fontSize: 11, fontWeight: 500, background: "rgba(139,92,246,0.08)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
            {skill.category}
          </span>
        </div>

        {/* Stats: stars + date + like */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 12, color: "var(--text-muted)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <i className="fab fa-github"></i> {(skill.stars / 1000).toFixed(1)}k
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <i className="fas fa-calendar"></i> {skill.updated}
            </span>
          </div>
          <button onClick={handleLike} style={{ cursor: "pointer", transition: "all 0.2s ease", color: liked ? "#ef4444" : "var(--text-muted)", transform: liked ? "scale(1.2)" : "scale(1)", background: "none", border: "none", fontSize: 14, padding: 0 }}
            onMouseEnter={(e) => { if (!liked) e.currentTarget.style.color = "#ef4444"; }}
            onMouseLeave={(e) => { if (!liked) e.currentTarget.style.color = "var(--text-muted)"; }}
            aria-label="收藏">
            <i className="fas fa-heart"></i>
          </button>
        </div>

        {/* Install command */}
        <div onClick={handleCopy} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, padding: "8px 14px", borderRadius: 8, background: "var(--bg-primary)", border: "1px solid var(--border)", color: "var(--text-secondary)", fontFamily: "'Courier New', monospace", fontSize: 12, cursor: "pointer", transition: "all 0.2s ease" }}
          onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.background = "var(--accent-glow)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.background = "var(--bg-primary)"; }}
          title="点击复制安装命令" role="button" tabIndex={0} aria-label="复制安装命令">
          <code style={{ overflow: "hidden", textOverflow: "ellipsis", fontSize: 12, fontFamily: "'Courier New', monospace" }}>$ {skill.install}</code>
          <span style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
            {copied && <span style={{ fontSize: 12, color: "#22c55e" }}>✓ 已复制</span>}
            <i className="fas fa-copy" style={{ color: "var(--accent-light)" }}></i>
          </span>
        </div>
      </div>
    </div>
  );
}
