"use client";

import { useState, useEffect, useMemo, useRef } from "react";
import { CATEGORIES } from "@/types/skill";
import SkillCard from "@/components/SkillCard";
import { useTheme } from "./ThemeProvider";
import type { Skill } from "@/types/skill";

function SkeletonCard() {
  return (
    <div style={{ background: "var(--gradient-card)", border: "1px solid var(--border)", borderRadius: 16, padding: 20, minHeight: 260 }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <div style={{ width: "60%", height: 20, background: "var(--bg-primary)", borderRadius: 4, opacity: 0.5 }} />
        <div style={{ width: 40, height: 20, background: "var(--bg-primary)", borderRadius: 10, opacity: 0.3 }} />
      </div>
      <div style={{ width: "100%", height: 6, background: "var(--bg-primary)", borderRadius: 3, marginBottom: 12, opacity: 0.4 }} />
      <div style={{ width: "80%", height: 14, background: "var(--bg-primary)", borderRadius: 4, marginBottom: 8, opacity: 0.3 }} />
      <div style={{ width: "50%", height: 14, background: "var(--bg-primary)", borderRadius: 4, marginBottom: 16, opacity: 0.3 }} />
      <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
        <div style={{ width: 50, height: 22, background: "var(--bg-primary)", borderRadius: 20, opacity: 0.3 }} />
        <div style={{ width: 60, height: 22, background: "var(--bg-primary)", borderRadius: 20, opacity: 0.3 }} />
      </div>
      <div style={{ width: "100%", height: 32, background: "var(--bg-primary)", borderRadius: 8, opacity: 0.4 }} />
    </div>
  );
}

function ErrorFallback({ onRetry }: { onRetry: () => void }) {
  return (
    <div style={{ textAlign: "center", padding: "80px 20px" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>😵</div>
      <h3 style={{ fontSize: 18, marginBottom: 8 }}>加载失败了</h3>
      <p style={{ fontSize: 14, color: "var(--text-muted)", marginBottom: 20 }}>网络好像出了点问题，点一下重新加载</p>
      <button onClick={onRetry} style={{ padding: "10px 28px", borderRadius: 24, border: "none", background: "var(--accent)", color: "white", fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "'Noto Sans SC', sans-serif" }}>
        重新加载
      </button>
    </div>
  );
}

export default function Home() {
  const { theme, toggleTheme } = useTheme();
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [allSkills, setAllSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [mounted, setMounted] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => { setMounted(true); }, []);

  // Load skills.json
  useEffect(() => {
    setLoading(true);
    fetch("/skills.json")
      .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
      .then((data) => { setAllSkills(data); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  // Debounced search
  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setDebouncedSearch(search), 300);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [search]);

  // Filter + sort client-side
  const filtered = useMemo(() => {
    let result = [...allSkills];
    if (category !== "all") result = result.filter((s) => s.category === category);
    if (debouncedSearch.trim()) {
      const q = debouncedSearch.toLowerCase().trim();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.benefit.toLowerCase().includes(q) ||
          s.tags?.some((t: string) => t.toLowerCase().includes(q)) ||
          s.category.includes(q)
      );
    }
    result.sort((a, b) => b.downloads - a.downloads);
    return result;
  }, [allSkills, category, debouncedSearch]);

  if (!mounted) return null;

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", color: "var(--text-primary)" }}>
      {/* Theme toggle */}
      <button onClick={toggleTheme}
        style={{ position: "fixed", bottom: 24, right: 24, width: 48, height: 48, borderRadius: "50%", background: "var(--accent)", color: "white", border: "none", cursor: "pointer", fontSize: 20, boxShadow: "0 4px 16px rgba(139, 92, 246, 0.4)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.3s ease" }}
        onMouseEnter={e => { e.currentTarget.style.transform = "scale(1.1)"; e.currentTarget.style.boxShadow = "0 6px 24px rgba(139, 92, 246, 0.6)"; }}
        onMouseLeave={e => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.boxShadow = "0 4px 16px rgba(139, 92, 246, 0.4)"; }}
        aria-label={theme === "dark" ? "切换到亮色主题" : "切换到暗色主题"}>
        <i className={`fas fa-${theme === "dark" ? "moon" : "sun"}`}></i>
      </button>

      {/* Hero */}
      <div className="hero" style={{ background: "var(--gradient-hero)", padding: "60px 20px 80px", textAlign: "center", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", top: "-50%", left: "-50%", width: "200%", height: "200%", background: "radial-gradient(circle at 30% 50%, var(--accent-glow) 0%, transparent 50%), radial-gradient(circle at 70% 50%, rgba(59, 130, 246, 0.08) 0%, transparent 50%)", animation: "qjFloat 20s ease-in-out infinite", pointerEvents: "none" }} />
        <div style={{ position: "relative", zIndex: 1, maxWidth: 800, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 16 }}>
            <div style={{ width: 42, height: 42, background: "linear-gradient(135deg, #8b5cf6, #6366f1)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, color: "white", boxShadow: "0 4px 12px rgba(139,92,246,0.3)" }}>
              <i className="fas fa-wand-magic-sparkles"></i>
            </div>
            <span style={{ fontSize: 28, fontWeight: 800, background: "linear-gradient(135deg, #c4b5fd, #818cf8)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>巧匠</span>
            <span style={{ fontSize: 14, color: "var(--text-muted)", background: "var(--accent-glow)", padding: "2px 10px", borderRadius: 12, border: "1px solid rgba(139,92,246,0.2)", fontWeight: 500 }}>Beta</span>
          </div>
          <h1 className="hero-title" style={{ fontSize: 36, fontWeight: 800, marginBottom: 12 }}>
            发现最好用的 <span style={{ color: "var(--accent-light)" }}>AI Skill</span>
          </h1>
          <p style={{ fontSize: 16, color: "var(--text-secondary)", marginBottom: 32, lineHeight: 1.6 }}>
            收录 {allSkills.length || 347} 个 AI 技能包 · 按下载量排序 · 一键安装
          </p>
          <div style={{ maxWidth: 480, margin: "0 auto", position: "relative" }}>
            <i className="fas fa-search" style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)", fontSize: 14 }}></i>
            <input className="search-box" type="search" placeholder="搜一搜，看看有什么好玩的 Skill..." value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: "100%", padding: "14px 16px 14px 44px", borderRadius: 12, border: "1px solid var(--border)", background: "var(--bg-input)", color: "var(--text-primary)", fontSize: 15, outline: "none", transition: "all 0.3s ease", fontFamily: "'Noto Sans SC', sans-serif" }}
              onFocus={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-glow)"; }}
              onBlur={(e) => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.boxShadow = "none"; }}
              aria-label="搜索 Skill" />
          </div>
        </div>
      </div>

      {/* Category filter */}
      <div style={{ maxWidth: 1200, margin: "24px auto", padding: "0 16px" }}>
        <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }} role="tablist" aria-label="分类筛选">
          <button onClick={() => setCategory("all")}
            style={{ padding: "8px 20px", borderRadius: 24, fontSize: 14, fontWeight: 500, cursor: "pointer", transition: "all 0.2s ease", whiteSpace: "nowrap", border: `1px solid ${category === "all" ? "var(--accent)" : "var(--border)"}`, background: category === "all" ? "var(--accent)" : "transparent", color: category === "all" ? "white" : "var(--text-secondary)", fontFamily: "'Noto Sans SC', sans-serif" }}
            role="tab" aria-selected={category === "all"}>🏠 全部</button>
          {CATEGORIES.map((cat) => (
            <button key={cat.key} onClick={() => setCategory(cat.key)}
              style={{ padding: "8px 20px", borderRadius: 24, fontSize: 14, fontWeight: 500, cursor: "pointer", transition: "all 0.2s ease", whiteSpace: "nowrap", border: `1px solid ${category === cat.key ? "var(--accent)" : "var(--border)"}`, background: category === cat.key ? "var(--accent)" : "transparent", color: category === cat.key ? "white" : "var(--text-secondary)", fontFamily: "'Noto Sans SC', sans-serif" }}
              onMouseEnter={(e) => { if (category !== cat.key) { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.color = "var(--accent-light)"; e.currentTarget.style.background = "var(--accent-glow)"; }}}
              onMouseLeave={(e) => { if (category !== cat.key) { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.color = "var(--text-secondary)"; e.currentTarget.style.background = "transparent"; }}}
              role="tab" aria-selected={category === cat.key}>{cat.icon} {cat.key}</button>
          ))}
        </div>
      </div>

      {/* Skills grid */}
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "0 16px 80px" }}>
        {error ? (
          <ErrorFallback onRetry={() => window.location.reload()} />
        ) : loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : filtered.length > 0 ? (
          <>
            <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 16 }}>共 {filtered.length} 个 Skill · 按下载量排序</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 24 }}>
              {filtered.map((s) => <SkillCard key={s.id} skill={s} />)}
            </div>
          </>
        ) : (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
            <h3 style={{ fontSize: 18, marginBottom: 8 }}>没找到相关 Skill</h3>
            <p style={{ fontSize: 14, color: "var(--text-muted)" }}>试试换个关键词搜索吧～</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border)", padding: "32px 16px", textAlign: "center" }}>
        <p style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.8 }}>
          <i className="fas fa-wand-magic-sparkles" style={{ color: "var(--accent-light)" }}></i> 巧匠 · AI Skill 推荐站
          <span style={{ margin: "0 8px" }}>|</span>
          数据来源：GitHub / skills.sh / Dify Marketplace
          <br />
          <span style={{ fontSize: 12 }}>发现侵权内容？<a href="#" style={{ color: "var(--accent-light)" }}>联系我们</a>，24h内删除</span>
        </p>
      </footer>
    </div>
  );
}
