#!/usr/bin/env python3
"""Build the GitHub Pages site for focus-gap-analyses into docs/.

Usage (from anywhere):
    python3 scripts/build_pages.py

Reads analyses/*.md, index/*.html, assets/, and DISCLAIMER.md. Writes only
under docs/, which it empties and rebuilds on every run. Source files are
never modified. No network calls, no git commands.

Requires Python 3.9+ and the `markdown` package.
"""
from __future__ import annotations

import argparse
import html
import posixpath
import re
import shutil
import sys
from pathlib import Path
from string import Template
from urllib.parse import quote, unquote

try:
    import markdown
except ImportError:
    sys.exit("error: the 'markdown' package is required (pip install markdown)")

REPO_URL = "https://github.com/beau-finopsorg/focus-gap-analyses"
BLOB_URL = REPO_URL + "/blob/main/"
TREE_URL = REPO_URL + "/tree/main/"
EXPECTED_ANALYSES = 98

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

DASHBOARD_SRC = "index/FOCUS-Readiness-Dashboard.html"
BY_COMPANY_SRC = "index/gap-analyses-by-company.html"
DISCLAIMER_SRC = "DISCLAIMER.md"
SITE_CSS_SRC = "assets/site.css"

# Repo-relative source path -> docs-relative output path.
STATIC_MAP = {
    DASHBOARD_SRC: "index.html",
    BY_COMPANY_SRC: "by-company.html",
    DISCLAIMER_SRC: "DISCLAIMER.html",
}

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "smarty", "toc"]

ATTR_RE = re.compile(r"""(\s(?:href|src)\s*=\s*)(["'])(.*?)\2""", re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(r"(<script\b[^>]*>.*?</script\s*>)", re.IGNORECASE | re.DOTALL)
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700"
    "&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap"
)

# Fallbacks, used only if the dashboard asides cannot be found. Links are
# written relative to index/ so they go through the same rewriting.
FALLBACK_BANNER = """<aside class="unofficial-banner" role="note">
<p><strong>Unofficial community project.</strong> Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is not an official FOCUS, FinOps Foundation, or Linux Foundation publication. Ratings are a reading of public documentation, not a certification result. Official certification, where it exists, is labeled separately as FinOps Certified FOCUS Conformant. See the <a href="../DISCLAIMER.md">disclaimer</a>.</p>
</aside>"""

FALLBACK_FOOTER = """<aside class="unofficial-footer" role="note">
<p>Unofficial community project by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. Licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Product names and marks belong to their owners. The FinOps Open Cost and Usage Specification is published at <a href="https://focus.finops.org">focus.finops.org</a>. Found something wrong? Open an issue or pull request in the <a href="https://github.com/beau-finopsorg/focus-gap-analyses">GitHub repository</a>.</p>
</aside>"""

NAV_CSS = """
.pages-nav-bar{background:#fff;border-bottom:1px solid #d9dee3}
.pages-nav{display:flex;flex-wrap:wrap;align-items:center;gap:.25rem 1.25rem;max-width:1200px;margin:0 auto;padding:.55rem 1.25rem;font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:.9rem;font-weight:500;line-height:1.4}
.pages-nav a{color:#2B3F50;text-decoration:none;border-bottom:2px solid transparent;padding:.15rem 0}
.pages-nav a:hover,.pages-nav a:focus{border-bottom-color:#bd3bfd}
.pages-nav a[aria-current="page"]{color:#bd3bfd;border-bottom-color:#bd3bfd}
.pages-nav .pages-nav-src{margin-left:auto}
"""

PAGE_CSS = """
:root{--focus-dark:#2B3F50;--focus-purple:#bd3bfd;--ink:#1f2a33;--muted:#5b6b78;--rule:#d9dee3;--soft:#f5f7f9;--banner-bg:#fff8e8;--banner-border:#e6d19a}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.6;color:var(--ink);background:#fff}
a{color:var(--focus-purple);text-underline-offset:2px}
a:hover,a:focus{color:var(--focus-dark)}
.wrap{max-width:980px;margin:0 auto;padding:0 1.25rem}
.unofficial-banner{background:var(--banner-bg);border:1px solid var(--banner-border);border-radius:6px;padding:.75rem 1rem;margin:1.25rem 0 1.5rem;font-size:.92rem}
.unofficial-banner p,.unofficial-footer p{margin:.25rem 0}
article h1{color:var(--focus-dark);font-size:2rem;line-height:1.2;margin:.5rem 0 1rem}
article h2{color:var(--focus-dark);font-size:1.45rem;line-height:1.3;margin:2.25rem 0 .75rem;padding-bottom:.3rem;border-bottom:1px solid var(--rule)}
article h3{color:var(--focus-dark);font-size:1.15rem;margin:1.75rem 0 .5rem}
article h4{color:var(--focus-dark);font-size:1rem;margin:1.5rem 0 .5rem}
article li{margin:.2rem 0}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1rem 0 1.5rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--rule);padding:.45rem .6rem;text-align:left;vertical-align:top}
th{background:var(--focus-dark);color:#fff;font-weight:600}
th a{color:#fff}
tbody tr:nth-child(even){background:var(--soft)}
code{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em;background:var(--soft);padding:.1em .3em;border-radius:3px}
pre{background:var(--soft);border:1px solid var(--rule);border-radius:6px;padding:.85rem 1rem;overflow-x:auto;line-height:1.45}
pre code{background:none;padding:0;font-size:.85rem}
blockquote{margin:1rem 0;padding:.5rem 1rem;border-left:4px solid var(--focus-purple);background:var(--soft)}
blockquote p{margin:.35rem 0}
hr{border:0;border-top:1px solid var(--rule);margin:2rem 0}
.unofficial-footer{border-top:1px solid var(--rule);margin:2.5rem 0 2rem;padding-top:1rem;font-size:.88rem;color:var(--muted)}
"""

PAGE_TEMPLATE = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="$fonts">
<style>$css</style>
</head>
<body>
$nav
<div class="wrap">
$banner
<main>
<article>
$article
</article>
</main>
$footer
</div>
</body>
</html>
""")


class BuildError(Exception):
    pass


class Builder:
    def __init__(self) -> None:
        self.written: set[str] = set()
        self.assets: set[str] = set()
        self.warnings: list[str] = []

    # ---- paths and links -------------------------------------------------

    def output_for(self, target: str) -> str | None:
        """Map a repo-relative source path to a docs-relative output path."""
        if target in STATIC_MAP:
            return STATIC_MAP[target]
        if target.startswith("analyses/") and target.endswith(".md") and target.count("/") == 1:
            return target[:-3] + ".html"
        if target.startswith("assets/") and (ROOT / target).is_file():
            self.assets.add(target)
            return target
        return None

    def rewrite_url(self, url: str, src_dir: str, out_dir: str) -> str:
        raw = html.unescape(url).strip()
        if not raw or raw.startswith(("#", "/", "?")) or SCHEME_RE.match(raw):
            return url
        path, has_frag, frag = raw.partition("#")
        path, has_query, query = path.partition("?")
        target = posixpath.normpath(posixpath.join(src_dir, unquote(path)))
        if target == ".." or target.startswith("../"):
            return url
        out = self.output_for(target)
        if out is not None:
            new = quote(posixpath.relpath(out, out_dir or "."), safe="/")
        elif target == ".":
            new = REPO_URL
        else:
            new = (TREE_URL if (ROOT / target).is_dir() else BLOB_URL) + quote(target, safe="/")
        if has_query:
            new += "?" + query
        if has_frag:
            new += "#" + frag
        return html.escape(new, quote=True)

    def rewrite_html(self, text: str, src_dir: str, out_dir: str, label: str) -> str:
        """Rewrite href/src values outside <script> blocks."""
        parts = SCRIPT_RE.split(text)
        for i in range(0, len(parts), 2):
            parts[i] = ATTR_RE.sub(
                lambda m: m.group(1) + m.group(2)
                + self.rewrite_url(m.group(3), src_dir, out_dir) + m.group(2),
                parts[i],
            )
        for i in range(1, len(parts), 2):
            if ".md" in parts[i] or "analyses/" in parts[i]:
                self.warnings.append(f"{label}: a <script> block mentions .md or analyses/; it was not rewritten")
        return "".join(parts)

    # ---- output ----------------------------------------------------------

    def write(self, rel: str, text: str) -> None:
        dest = DOCS / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        self.written.add(rel)

    def copy(self, src_rel: str, rel: str) -> None:
        src = ROOT / src_rel
        if not src.is_file():
            raise BuildError(f"missing source file: {src_rel}")
        dest = DOCS / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        self.written.add(rel)

    # ---- chrome ----------------------------------------------------------

    @staticmethod
    def nav(out_dir: str, current: str, source_url: str, source_label: str) -> str:
        items = [
            ("index.html", "Scorecard", "scorecard"),
            ("by-company.html", "By company", "by-company"),
            ("DISCLAIMER.html", "Disclaimer", "disclaimer"),
        ]
        links = []
        for href, label, key in items:
            rel = html.escape(posixpath.relpath(href, out_dir or "."), quote=True)
            current_attr = ' aria-current="page"' if key == current else ""
            links.append(f'<a href="{rel}"{current_attr}>{label}</a>')
        links.append(
            f'<a class="pages-nav-src" href="{html.escape(source_url, quote=True)}">'
            f"{html.escape(source_label)}</a>"
        )
        return (
            '<div class="pages-nav-bar"><nav class="pages-nav" aria-label="Site">'
            + "".join(links)
            + "</nav></div>"
        )

    def load_asides(self) -> tuple[str, str]:
        text = read(DASHBOARD_SRC)
        found = []
        for cls, fallback in (("unofficial-banner", FALLBACK_BANNER), ("unofficial-footer", FALLBACK_FOOTER)):
            m = re.search(
                r"<aside\b[^>]*\bclass\s*=\s*[\"'][^\"']*\b" + cls + r"\b[^\"']*[\"'][^>]*>.*?</aside\s*>",
                text,
                re.IGNORECASE | re.DOTALL,
            )
            if m:
                found.append(m.group(0))
            else:
                self.warnings.append(f"{DASHBOARD_SRC}: no {cls} aside found; using built-in wording")
                found.append(fallback)
        return found[0], found[1]

    # ---- pages -----------------------------------------------------------

    def build_index_page(self, src_rel: str, out_rel: str, current: str) -> None:
        text = read(src_rel)
        text = self.rewrite_html(text, posixpath.dirname(src_rel), "", src_rel)
        style = f"<style>{NAV_CSS}</style>\n"
        text, n = re.subn(r"</head\s*>", lambda m: style + m.group(0), text, count=1, flags=re.IGNORECASE)
        if n == 0:
            raise BuildError(f"{src_rel}: no </head> tag")
        nav = self.nav("", current, REPO_URL, "GitHub repo")
        text, n = re.subn(r"<body\b[^>]*>", lambda m: m.group(0) + "\n" + nav, text, count=1, flags=re.IGNORECASE)
        if n == 0:
            raise BuildError(f"{src_rel}: no <body> tag")
        self.write(out_rel, text)

    def build_md_page(self, src_rel: str, out_rel: str, current: str, suffix: str,
                      source_url: str, source_label: str, asides: tuple[str, str]) -> None:
        src_dir = posixpath.dirname(src_rel)
        out_dir = posixpath.dirname(out_rel)
        md = markdown.Markdown(extensions=MD_EXTENSIONS, output_format="html")
        body = md.convert(read(src_rel))
        body = re.sub(r"<table\b", '<div class="table-wrap"><table', body, flags=re.IGNORECASE)
        body = re.sub(r"</table\s*>", "</table></div>", body, flags=re.IGNORECASE)
        body = self.rewrite_html(body, src_dir, out_dir, src_rel)
        title = first_h1(body, Path(src_rel).stem) + suffix
        banner = self.rewrite_html(asides[0], "index", out_dir, DASHBOARD_SRC)
        footer = self.rewrite_html(asides[1], "index", out_dir, DASHBOARD_SRC)
        # Insert the article after Template.substitute so a "$" in a report
        # body cannot be treated as a placeholder.
        page = PAGE_TEMPLATE.substitute(
            title=html.escape(title),
            fonts=FONTS_HREF,
            css=PAGE_CSS + NAV_CSS,
            nav=self.nav(out_dir, current, source_url, source_label),
            banner=banner,
            article="__ARTICLE__",
            footer=footer,
        ).replace("__ARTICLE__", body)
        self.write(out_rel, page)

    # ---- checks ----------------------------------------------------------

    def broken_links(self) -> list[str]:
        problems = []
        for rel in sorted(self.written):
            if not rel.endswith(".html"):
                continue
            page_dir = posixpath.dirname(rel)
            parts = SCRIPT_RE.split((DOCS / rel).read_text(encoding="utf-8"))
            for part in parts[0::2]:
                for m in ATTR_RE.finditer(part):
                    raw = html.unescape(m.group(3)).strip()
                    if not raw or raw.startswith(("#", "/", "?")) or SCHEME_RE.match(raw):
                        continue
                    path = unquote(raw.split("#", 1)[0].split("?", 1)[0])
                    target = posixpath.normpath(posixpath.join(page_dir, path))
                    if path.endswith("/"):
                        target = posixpath.join(target, "index.html")
                    if target not in self.written:
                        problems.append(f"{rel}: {raw}")
        return problems


def read(src_rel: str) -> str:
    path = ROOT / src_rel
    if not path.is_file():
        raise BuildError(f"missing source file: {src_rel}")
    return path.read_text(encoding="utf-8")


def first_h1(body: str, fallback: str) -> str:
    m = H1_RE.search(body)
    if not m:
        return fallback
    text = " ".join(html.unescape(TAG_RE.sub("", m.group(1))).split())
    return text or fallback


def reset_docs() -> None:
    if DOCS.is_symlink() or (DOCS.exists() and not DOCS.is_dir()):
        raise BuildError(f"{DOCS} exists and is not a plain directory; refusing to touch it")
    DOCS.mkdir(exist_ok=True)
    for child in DOCS.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def build(expected: int) -> int:
    if not (ROOT / "analyses").is_dir():
        raise BuildError(f"{ROOT} does not look like the repo root (no analyses/ directory)")
    sources = sorted((ROOT / "analyses").glob("*.md"))

    reset_docs()
    b = Builder()
    b.write(".nojekyll", "")
    b.copy(SITE_CSS_SRC, SITE_CSS_SRC)

    b.build_index_page(DASHBOARD_SRC, "index.html", "scorecard")
    b.build_index_page(BY_COMPANY_SRC, "by-company.html", "by-company")

    asides = b.load_asides()
    b.build_md_page(DISCLAIMER_SRC, "DISCLAIMER.html", "disclaimer", " | FOCUS gap analyses",
                    REPO_URL, "GitHub repo", asides)
    for src in sources:
        name = src.name
        b.build_md_page(f"analyses/{name}", f"analyses/{src.stem}.html", "", " | FOCUS gap analysis",
                        BLOB_URL + "analyses/" + quote(name), "Source on GitHub", asides)

    for asset in sorted(b.assets - b.written):
        b.copy(asset, asset)

    errors = []
    html_out = sorted(p.name for p in (DOCS / "analyses").glob("*.html"))
    if len(html_out) != expected:
        errors.append(f"expected {expected} analysis HTML files, found {len(html_out)}")
    missing = [s.name for s in sources if not (DOCS / "analyses" / (s.stem + ".html")).is_file()]
    errors += [f"no HTML output for analyses/{name}" for name in missing]
    errors += [f"broken link {p}" for p in b.broken_links()]

    print(f"Repo root:        {ROOT}")
    print(f"Source reports:   {len(sources)}")
    print(f"Analysis pages:   {len(html_out)} (expected {expected})")
    print(f"Files in docs/:   {len(b.written)}")
    for w in b.warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        print(f"FAILED with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("OK. docs/ is ready for GitHub Pages (main branch, /docs).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the GitHub Pages site into docs/.")
    parser.add_argument("--expect", type=int, default=EXPECTED_ANALYSES,
                        help=f"expected number of analysis pages (default {EXPECTED_ANALYSES})")
    args = parser.parse_args()
    try:
        return build(args.expect)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
