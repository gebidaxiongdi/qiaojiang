import type { Metadata } from "next";
import "./globals.css";
import ThemeProvider from "./ThemeProvider";

export const metadata: Metadata = {
  title: "巧匠 · AI Skill 推荐站 - 发现最好用的AI技能",
  description: "巧匠收录了347个AI Skill（技能包），涵盖编程、设计、办公、内容创作等领域。无论是编程新手还是资深开发者，都能找到提升AI效率的利器。",
  keywords: ["AI Skill", "AI技能", "Claude Skill", "Codex Skill", "AI工具", "编程辅助", "巧匠"],
  authors: [{ name: "巧匠" }],
  openGraph: {
    title: "巧匠 · AI Skill 推荐站",
    description: "发现347个提升AI效率的Skill技能包，编程、设计、办公、创作全覆盖。",
    type: "website",
    locale: "zh_CN",
    siteName: "巧匠",
    url: "https://qiaojiang.vercel.app",
  },
  twitter: {
    card: "summary_large_image",
    title: "巧匠 · AI Skill 推荐站",
    description: "发现347个提升AI效率的Skill技能包",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" data-theme="dark" suppressHydrationWarning>
      <head>
        {/* Inline script: prevent theme FOUC — runs before any paint */}
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var t=localStorage.getItem('qj_theme');if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}",
          }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
        <link rel="canonical" href="https://qiaojiang.vercel.app" />
      </head>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
