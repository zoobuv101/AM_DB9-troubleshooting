#!/usr/bin/env python3
"""Build workshop-guide pages from guides-src/*.json.

Each spec describes one guide (title, description, a list of content blocks). The script
  * renders the page in the same house style as the hand-written ref-*.html guides,
  * adds it to the guide list and renumbers every guide ("NN / MM" kicker, "More from the workshop
    reference" chips, previous/next links) on all ref-*.html pages and reference.html,
  * adds it to sitemap.xml,
  * adds a "Full step-by-step guide" link to its log entry on index.html (spec key log_anchor).

A spec that still contains a "[NEEDED" marker is NOT built, so a half-written draft can't go live.
Run from anywhere:  python3 scripts/build_guides.py        (add --check to only report what is ready)
Output is plain static HTML; there is no build step on the server.
"""
import glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://db9v12.co.uk"
TEMPLATE = "ref-rear-light-condensation.html"   # head (CSS), nav and footer are taken from here
CHIP_RE = re.compile(r'<a class="chip(?: current)?" href="(ref-[^"]+)\.html"><div class="chip-num">\d+ /</div>'
                     r'<div class="chip-title">(.*?)</div><div class="chip-note">(.*?)</div></a>')


def rd(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def wr(name, text):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def esc(s):
    return html.escape(s, quote=True)


def one(pattern, repl, text, flags=0):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"pattern not found: {pattern}")
    return new


# ---------------------------------------------------------------- content blocks
def thumb_for(src):
    base = os.path.basename(src)
    t = os.path.join("photos", "thumbs", base)
    return t if os.path.exists(os.path.join(ROOT, t)) and not src.startswith("photos/thumbs/") else src


def render_block(b):
    if "p" in b:
        paras = b["p"] if isinstance(b["p"], list) else [b["p"]]
        return "\n".join(f"<p>{p}</p>" for p in paras)
    if "h2" in b:
        return f"<h2>{b['h2']}</h2>"
    if "h3" in b:
        return f"<h3>{b['h3']}</h3>"
    if "info" in b:
        return f'<div class="info-box">ℹ {b["info"]}</div>'
    if "warn" in b:
        return f'<div class="warn-box">⚠ {b["warn"]}</div>'
    if "steps" in b:
        s = b["steps"]
        items = "\n".join(f"  <li>{i}</li>" for i in s["items"])
        return f"<h3>{s.get('title', 'The plan')}</h3>\n<ol class=\"steps\">\n{items}\n</ol>"
    if "ul" in b:
        items = "\n".join(f"  <li>{i}</li>" for i in b["ul"])
        return f'<ul class="plain-list">\n{items}\n</ul>'
    if "figs" in b:
        links = "".join(
            f'<a href="{f["src"]}" target="_blank" rel="noopener"><img src="{f.get("thumb") or thumb_for(f["src"])}" '
            f'alt="{esc(f["alt"])}" loading="lazy"></a>' for f in b["figs"])
        return f'<div class="figs">{links}</div>'
    if "table" in b:
        t = b["table"]
        head = "".join(f"<th>{c}</th>" for c in t["head"])
        rows = "\n".join("    <tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in t["rows"])
        title = f"<h3>{t['title']}</h3>\n" if t.get("title") else ""
        return (f'{title}<div class="table-wrap"><table class="mapping-table">\n  <thead><tr>{head}</tr></thead>\n'
                f'  <tbody>\n{rows}\n  </tbody>\n</table></div>')
    if "raw" in b:
        return b["raw"]
    raise SystemExit(f"unknown block: {list(b)}")


# ---------------------------------------------------------------- page pieces
def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>\n"


def render_page(spec, tpl):
    head = tpl.split("<body>", 1)[0]
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head, flags=re.S)
    slug, title, desc = spec["slug"], spec["title"], spec["description"]
    url = f"{SITE}/{slug}.html"
    og = f"{SITE}/{spec['og_image']}"
    head = one(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', head)
    head = one(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = one(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', head)
    head = one(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', head)
    head = one(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', head)
    head = one(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{og}">', head)
    head = one(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", head)
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "inLanguage": "en-GB",
           "url": url, "mainEntityOfPage": url, "image": [og], "datePublished": spec["published"],
           "dateModified": spec.get("modified", spec["published"]), "about": "Aston Martin DB9",
           "publisher": {"@type": "Organization", "name": "DB9 V12 Owner's Log", "url": SITE + "/"}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "DB9 V12 Owner's Log", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Workshop reference", "item": SITE + "/reference.html"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    head = head.replace("</head>", jsonld(art) + jsonld(crumbs) + "</head>", 1)
    nav = re.search(r"<nav>.*?</nav>", tpl, re.S).group(0)
    footer = tpl[tpl.index('<div style="margin-top:48px;padding-top:20px'):]
    meta = "".join(f"<span>{m}</span>" for m in spec["meta"])
    body = "\n\n".join(render_block(b) for b in spec["blocks"])
    return (f'{head}<body>\n\n{nav}\n\n<div class="page-hero">\n  <div class="page-kicker">Workshop Reference · 00 / 00</div>\n'
            f'  <h1 class="ref-title">{spec["h1"]}</h1>\n  <div class="page-meta">{meta}<span><a href="reference.html">← All reference topics</a></span></div>\n'
            f'</div>\n\n{body}\n\n<div class="ref-nav">\n</div>\n\n<h3>More from the workshop reference</h3>\n<div class="chips">\n</div>\n\n{footer}')


def chips_html(guides, current):
    return "\n".join(
        f'  <a class="chip{" current" if g["slug"] == current else ""}" href="{g["slug"]}.html"><div class="chip-num">{i:02d} /</div>'
        f'<div class="chip-title">{g["title"]}</div><div class="chip-note">{g["note"]}</div></a>'
        for i, g in enumerate(guides, 1))


def nav_html(guides, i):
    prev = (f'  <a class="prev" href="{guides[i-1]["slug"]}.html"><span class="lbl">← Previous</span>'
            f'<span class="ttl">{guides[i-1]["title"]}</span></a>') if i > 0 else '  <span class="spacer"></span>'
    nxt = (f'  <a class="next" href="{guides[i+1]["slug"]}.html"><span class="lbl">Next →</span>'
           f'<span class="ttl">{guides[i+1]["title"]}</span></a>') if i < len(guides) - 1 else '  <span class="spacer"></span>'
    idx = '  <a class="idx" href="reference.html"><span class="lbl">Index</span><span class="ttl">All reference</span></a>'
    return f'<div class="ref-nav">\n{prev}\n{idx}\n{nxt}\n</div>'


CHIPS_BLOCK = re.compile(r'<div class="chips">\n(?:  <a class="chip.*?</a>\n)*</div>', re.S)


def main():
    check_only = "--check" in sys.argv
    specs = []
    for path in sorted(glob.glob(os.path.join(ROOT, "guides-src", "*.json"))):
        with open(path, encoding="utf-8") as f:
            spec = json.load(f)
        needed = re.findall(r"\[NEEDED[^\]]*\]", json.dumps(spec, ensure_ascii=False))
        spec["_file"] = os.path.basename(path)
        spec["_needed"] = needed
        specs.append(spec)
    ready = [s for s in specs if not s["_needed"]]
    for s in specs:
        state = "READY" if not s["_needed"] else f"DRAFT, {len(s['_needed'])} item(s) still needed"
        print(f"  {s['_file']}: {state}")
        for n in s["_needed"]:
            print(f"      {n}")
    if check_only:
        return

    hub = rd("reference.html")
    guides = [{"slug": m.group(1), "title": m.group(2), "note": m.group(3)} for m in CHIP_RE.finditer(hub)]
    known = {g["slug"] for g in guides}
    for s in ready:
        if s["slug"] not in known:
            guides.append({"slug": s["slug"], "title": s.get("chip_title", s["h1"]), "note": s.get("chip_note", "")})
        else:  # keep chip text in step with the spec
            for g in guides:
                if g["slug"] == s["slug"]:
                    g["title"], g["note"] = s.get("chip_title", g["title"]), s.get("chip_note", g["note"])
    total = len(guides)

    tpl = rd(TEMPLATE)
    for s in ready:
        wr(s["slug"] + ".html", render_page(s, tpl))

    for i, g in enumerate(guides):
        name = g["slug"] + ".html"
        t = rd(name)
        t = re.sub(r"Workshop Reference · \d\d / \d\d", f"Workshop Reference · {i+1:02d} / {total:02d}", t, count=1)
        t = re.sub(r'<div class="ref-nav">.*?</div>', lambda m: nav_html(guides, i), t, count=1, flags=re.S)
        t = CHIPS_BLOCK.sub(lambda m: '<div class="chips">\n' + chips_html(guides, g["slug"]) + "\n</div>", t, count=1)
        wr(name, t)
    wr("reference.html", CHIPS_BLOCK.sub(lambda m: '<div class="chips">\n' + chips_html(guides, None) + "\n</div>", hub, count=1))

    sm = rd("sitemap.xml")
    for s in ready:
        loc = f"{SITE}/{s['slug']}.html"
        if loc not in sm:
            sm = sm.replace("</urlset>", f'  <url><loc>{loc}</loc><lastmod>{s.get("modified", s["published"])}</lastmod></url>\n</urlset>')
    wr("sitemap.xml", sm)

    idx = rd("index.html")
    for s in ready:
        anchor = s.get("log_anchor")
        if not anchor:
            continue
        start = idx.index(f'<div class="entry" id="{anchor}">')
        end = idx.find('<div class="entry"', start + 10)
        end = len(idx) if end == -1 else end
        block = idx[start:end]
        if f'href="{s["slug"]}.html"' in block:
            continue
        link = (f'          <a class="entry-go" style="display:block;margin-top:12px;" href="{s["slug"]}.html">'
                f'{s.get("log_link_text", "Full step-by-step guide →")}</a>\n')
        close = block.index("\n        </div>\n") + 1          # end of the entry's text column
        idx = idx[:start] + block[:close] + link + block[close:] + idx[end:]
    wr("index.html", idx)
    print(f"built {len(ready)} guide(s); {total} guides in the reference list")


if __name__ == "__main__":
    main()
