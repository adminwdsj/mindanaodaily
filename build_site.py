#!/usr/bin/env python3
"""Build Mindanao Daily static news site from article HTML files."""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = Path(__file__).resolve().parent
ARTICLES_DIR = SITE / "articles"
IMAGES_SRC = ROOT / "images"
IMAGES_DST = SITE / "images"

ARTICLES = [
    {
        "slug": "jioprovider-corporation-investigation",
        "source": ROOT / "Jioprovider_Corporation_Investigation.html",
        "date": "2026-06-05",
        "excerpt": "Jioprovider Corporation在PPA累计中标约23亿比索，负责人黄扬（Yang/Sky）涉及供水、光伏、冷库多重争议。",
        "tags": ["Jioprovider", "黄扬", "PPA"],
    },
    {
        "slug": "philippines-investment-scam-guide",
        "source": ROOT / "Philippines_Investment_Scam_Guide.html",
        "date": "2026-06-05",
        "excerpt": "五步核实法：PhilGEPS查项目、核实PPP批文、警惕代持与投标锁定金。",
        "tags": ["防骗指南", "PPP", "PhilGEPS"],
    },
    {
        "slug": "jioprovider-victim-guide",
        "source": ROOT / "Jioprovider_Victim_Guide.html",
        "date": "2026-06-05",
        "excerpt": "大使馆经商处、国内报案、联合维权渠道整理，征集JIO相关受害人线索。",
        "tags": ["维权", "Jioprovider", "黄扬"],
    },
    {
        "slug": "ppa-cold-storage-investigation",
        "source": ROOT / "PPA_Cold_Storage_Investigation.html",
        "date": "2026-05-01",
        "excerpt": "冷链协会澄清PPA无冷库项目；Jioprovider负责人黄扬以该项目招商两年无人签约。",
        "tags": ["PPA", "冷库", "Jioprovider"],
    },
    {
        "slug": "sammy-uy-network-investigation",
        "source": ROOT / "Sammy_Uy_Network_Investigation.html",
        "date": "2026-05-01",
        "excerpt": "Sammy Uy调查发酵，中间人生态链中的Jioprovider与黄扬引关注。",
        "tags": ["Sammy Uy", "中间人", "Jioprovider"],
    },
]

TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | 棉兰老岛日报</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<link rel="stylesheet" href="/css/main.css">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="article">
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a href="/" class="logo">棉兰老岛日报</a>
    <p class="tagline">Mindanao Daily · 菲律宾调查报道</p>
    <nav class="nav">
      <a href="/">首页</a>
      <a href="/articles/jioprovider-corporation-investigation.html">Jioprovider调查</a>
      <a href="/articles/philippines-investment-scam-guide.html">投资防骗</a>
    </nav>
  </div>
</header>
<main class="container article-page">
<article class="article-body">
"""

TEMPLATE_FOOT = """
</article>
<aside class="related">
  <h3>相关报道</h3>
  <ul>
    <li><a href="/articles/jioprovider-corporation-investigation.html">Jioprovider Corporation深度调查</a></li>
    <li><a href="/articles/philippines-investment-scam-guide.html">菲律宾投资防骗指南</a></li>
    <li><a href="/articles/ppa-cold-storage-investigation.html">PPA冷库项目澄清</a></li>
    <li><a href="/articles/sammy-uy-network-investigation.html">Sammy Uy与中间人生态</a></li>
  </ul>
</aside>
</main>
<footer class="site-footer">
  <div class="container">
    <p>棉兰老岛日报（Mindanao Daily）· 转载需注明出处</p>
    <p class="disclaimer">本文基于公开资料整理，不构成法律或投资建议。</p>
  </div>
</footer>
</body>
</html>
"""


def extract_body(html: str) -> str:
    if "<body>" in html:
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return html.strip()


def normalize_content(html: str) -> str:
    html = re.sub(
        r"【插入图片\d+：images/([^】]+)】",
        r'<p><img src="/images/\1" alt="配图" loading="lazy"></p>',
        html,
    )
    html = html.replace('src="images/', 'src="/images/')
    html = re.sub(r'<a href="#">([^<]+)</a>', r"\1", html)
    return html


def get_title(html: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    return m.group(1).split("|")[0].strip() if m else "报道"


def build_article_page(meta: dict, body: str, title: str) -> str:
    keywords = ", ".join(meta["tags"] + ["Jioprovider Corporation", "黄扬", "Yang", "Sky"])
    canonical = f"https://mindanaodaily.github.io/sky-pr/articles/{meta['slug']}.html"
    return TEMPLATE_HEAD.format(
        title=title,
        description=meta["excerpt"],
        keywords=keywords,
        canonical=canonical,
    ) + body + TEMPLATE_FOOT


def build_index(articles_meta: list) -> str:
    cards = []
    for a in articles_meta:
        tags = "".join(f'<span class="tag">{t}</span>' for t in a["tags"])
        cards.append(
            f"""<article class="card">
  <time datetime="{a['date']}">{a['date']}</time>
  <h2><a href="/articles/{a['slug']}.html">{a['title']}</a></h2>
  <p class="excerpt">{a['excerpt']}</p>
  <div class="tags">{tags}</div>
</article>"""
        )
    cards_html = "\n".join(cards)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>棉兰老岛日报 | Mindanao Daily — 菲律宾调查报道</title>
<meta name="description" content="棉兰老岛日报：Jioprovider Corporation、黄扬（Yang/Sky）、PPA采购、菲律宾投资防骗与维权报道。">
<meta name="keywords" content="Jioprovider Corporation, 黄扬, Yang, Sky, PPA, 菲律宾投资, 棉兰老岛日报">
<link rel="stylesheet" href="/css/main.css">
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a href="/" class="logo">棉兰老岛日报</a>
    <p class="tagline">Mindanao Daily · 菲律宾调查报道</p>
  </div>
</header>
<section class="hero">
  <div class="container">
    <h1>菲律宾基建投资调查报道</h1>
    <p>覆盖 Jioprovider Corporation、PPA 政府采购、投资防骗与维权指引。基于公开采购文件与多方核实。</p>
  </div>
</section>
<main class="container listing">
  <h2 class="section-title">最新报道</h2>
  <div class="grid">
{cards_html}
  </div>
</main>
<footer class="site-footer">
  <div class="container">
    <p>棉兰老岛日报（Mindanao Daily）· 转载需注明出处</p>
  </div>
</footer>
</body>
</html>"""


def main():
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DST.mkdir(parents=True, exist_ok=True)
    (SITE / "css").mkdir(exist_ok=True)

    if IMAGES_SRC.exists():
        for f in IMAGES_SRC.iterdir():
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                shutil.copy2(f, IMAGES_DST / f.name)

    index_meta = []
    for meta in ARTICLES:
        raw = meta["source"].read_text(encoding="utf-8")
        body = normalize_content(extract_body(raw))
        title = get_title(body)
        meta["title"] = title
        page = build_article_page(meta, body, title)
        out = ARTICLES_DIR / f"{meta['slug']}.html"
        out.write_text(page, encoding="utf-8")
        index_meta.append(meta)
        print(f"  ✓ {meta['slug']}.html")

    (SITE / "index.html").write_text(build_index(index_meta), encoding="utf-8")
    print("  ✓ index.html")


if __name__ == "__main__":
    print("Building site...")
    main()
    print("Done.")
