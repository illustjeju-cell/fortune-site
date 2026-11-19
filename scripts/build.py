#!/usr/bin/env python3
"""운세 나침반 빌드 — data/dreams.json -> dist/ 정적 사이트 생성."""
import json, os, html, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE_URL = os.environ.get("SITE_URL", "https://unse.acoustic42.com").rstrip("/")
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "")
AD_SLOT = os.environ.get("AD_SLOT", "")
CNAME = os.environ.get("CNAME", "")
GA_ID = "GT-NSSSWH8S"
SITE_NAME = "운세 나침반"
NAVY = (18, 58, 109)

CAT_SLUG = {"동물": "animal", "자연·날씨": "nature", "사람·신체": "people",
            "행동·상황": "action", "사물·기타": "things"}
TONE_CLASS = {"길몽": "good", "흉몽": "bad", "중립": "mid", "태몽": "tae"}

def esc(s):
    return html.escape(str(s), quote=True)

def ad(slot_kind):
    if not ADSENSE_CLIENT:
        return ""
    if AD_SLOT:
        return (f'<div class="ad"><ins class="adsbygoogle" style="display:block" '
                f'data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT}" '
                f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
                f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></div>')
    return '<div class="ad ad-auto"></div>'

def head(title, desc, path, og_img=None):
    ads = ""
    if ADSENSE_CLIENT:
        ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
               f'?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>')
    og = f"{SITE_URL}{path}"
    img = f'<meta property="og:image" content="{SITE_URL}{og_img}">' if og_img else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{og}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{og}">
{img}
<meta name="twitter:card" content="summary_large_image">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
{ads}
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top"><a class="brand" href="/">🧭 {SITE_NAME}</a><nav><a href="/#dreams">꿈해몽</a><a href="/saju.html">사주</a></nav></header>
<main>
"""

FOOT = """
</main>
<footer class="foot">
<p>운세 나침반의 해몽은 전통적인 상징 해석을 바탕으로 한 참고용 콘텐츠입니다. 중요한 결정은 꿈보다 현실의 정보를 먼저 확인하세요.</p>
<p>© 운세 나침반</p>
</footer>
<script src="/app.js"></script>
</body>
</html>"""

def make_card(item):
    """OG 카드 1200x630 생성."""
    from PIL import Image, ImageDraw, ImageFont
    out = DIST / "cards" / f"{item['slug']}.png"
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1200, 630), (255, 255, 255))
    d = ImageDraw.Draw(img)
    bold = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    reg = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    f_brand = ImageFont.truetype(bold, 44)
    f_big = ImageFont.truetype(bold, 120)
    f_sub = ImageFont.truetype(reg, 46)
    d.rectangle([0, 0, 1200, 110], fill=NAVY)
    d.text((48, 30), SITE_NAME, font=f_brand, fill=(255, 255, 255))
    d.text((48, 190), f"{item['keyword']} 꿈", font=f_big, fill=(20, 20, 20))
    d.text((48, 360), "상황별 꿈해몽 풀이", font=f_sub, fill=(90, 90, 90))
    d.rectangle([0, 560, 1200, 630], fill=NAVY)
    img.save(out)

def detail(item, by_keyword):
    kw = item["keyword"]
    title = f"{kw} 꿈해몽 — 상황별 풀이 총정리 | {SITE_NAME}"
    desc = item["intro"][:150]
    parts = [head(title, desc, f"/d/{item['slug']}.html", f"/cards/{item['slug']}.png")]
    parts.append(f'<p class="crumb"><a href="/">홈</a> · <a href="/c/{CAT_SLUG.get(item["category"], "things")}.html">{esc(item["category"])}</a> · 꿈해몽</p>')
    parts.append(f"<h1>{esc(kw)} 꿈해몽</h1>")
    parts.append(f'<p class="intro">{esc(item["intro"])}</p>')
    parts.append(ad("top"))
    for s in item["situations"]:
        cls = TONE_CLASS.get(s["tone"], "mid")
        parts.append(
            f'<section class="sit"><h2>{esc(s["title"])} '
            f'<span class="tone {cls}">{esc(s["tone"])}</span></h2>'
            f'<p>{esc(s["meaning"])}</p></section>')
    parts.append(ad("bottom"))
    rel = [by_keyword[r] for r in item.get("related", []) if r in by_keyword]
    if rel:
        links = "".join(f'<a class="chip" href="/d/{r["slug"]}.html">{esc(r["keyword"])} 꿈해몽</a>' for r in rel)
        parts.append(f'<section class="rel"><h2>함께 보는 꿈해몽</h2><div class="chips">{links}</div></section>')
    parts.append(f'<section class="next"><h2>내 사주도 궁금하다면</h2><p>생년월일로 보는 사주 풀이가 곧 열립니다.</p><a class="btn" href="/saju.html">사주 풀이 미리 보기</a></section>')
    parts.append(FOOT)
    return "".join(parts)

def index(items):
    title = f"{SITE_NAME} | 꿈해몽·사주·오늘의 운세"
    desc = "어젯밤 그 꿈, 무슨 뜻일까요? 키워드로 찾는 상황별 꿈해몽과 사주 풀이."
    parts = [head(title, desc, "/")]
    parts.append(f"<h1>어젯밤 꿈, 무슨 뜻일까요?</h1>")
    parts.append('<div class="search"><input id="q" type="search" placeholder="꿈 키워드 검색 (예: 돼지, 똥, 떨어지는 꿈)" autocomplete="off"><div id="noresult" class="hidden">찾는 키워드가 아직 없어요. 아래 목록에서 골라보세요.</div></div>')
    parts.append('<section class="soon"><h2>🔮 사주 풀이</h2><p>생년월일시로 보는 평생사주 — 준비 중입니다.</p><a class="btn" href="/saju.html">미리 보기</a></section>')
    cats = []
    for cat, cslug in CAT_SLUG.items():
        group = [i for i in items if i["category"] == cat]
        if not group:
            continue
        cards = "".join(
            f'<a class="card" data-kw="{esc(i["keyword"])}" href="/d/{i["slug"]}.html">'
            f'<span class="cardkw">{esc(i["keyword"])}</span><span class="cardsub">꿈해몽 · 상황 {len(i["situations"])}가지</span></a>'
            for i in group)
        cats.append(f'<section class="cat" id="cat-{cslug}"><h2><a href="/c/{cslug}.html">{esc(cat)}</a></h2><div class="grid">{cards}</div></section>')
    parts.append('<div id="dreams">' + "".join(cats) + "</div>")
    parts.append(FOOT)
    return "".join(parts)

def category_page(cat, cslug, items):
    group = [i for i in items if i["category"] == cat]
    title = f"{cat} 꿈해몽 모음 | {SITE_NAME}"
    parts = [head(title, f"{cat} 관련 꿈해몽 {len(group)}가지 키워드를 모았습니다.", f"/c/{cslug}.html")]
    parts.append(f'<p class="crumb"><a href="/">홈</a> · 꿈해몽</p><h1>{esc(cat)} 꿈해몽</h1>')
    cards = "".join(
        f'<a class="card" href="/d/{i["slug"]}.html"><span class="cardkw">{esc(i["keyword"])}</span>'
        f'<span class="cardsub">{esc(i["intro"][:60])}…</span></a>' for i in group)
    parts.append(f'<div class="grid">{cards}</div>')
    parts.append(FOOT)
    return "".join(parts)

def saju_page():
    title = f"사주 풀이 (준비 중) | {SITE_NAME}"
    parts = [head(title, "생년월일시로 보는 평생사주 풀이, 곧 열립니다.", "/saju.html")]
    parts.append("<h1>🔮 사주 풀이</h1>")
    parts.append('<section class="sit"><h2>곧 열립니다</h2><p>생년월일시를 넣으면 사주팔자와 오행을 계산해 성격·재물·애정·건강을 풀어주는 평생사주를 준비하고 있습니다. 계산 정확도를 검증하는 중이라 조금만 기다려 주세요.</p><p>그동안 어젯밤 꿈부터 풀어보세요.</p><a class="btn" href="/">꿈해몽 보러 가기</a></section>')
    parts.append(FOOT)
    return "".join(parts)

def main():
    data = json.loads((ROOT / "data" / "dreams.json").read_text(encoding="utf-8"))
    items = data["items"]
    by_keyword = {i["keyword"]: i for i in items}
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "d").mkdir(parents=True)
    (DIST / "c").mkdir(parents=True)
    shutil.copy(ROOT / "templates" / "style.css", DIST / "style.css")
    shutil.copy(ROOT / "templates" / "app.js", DIST / "app.js")
    for item in items:
        make_card(item)
        (DIST / "d" / f"{item['slug']}.html").write_text(detail(item, by_keyword), encoding="utf-8")
    for cat, cslug in CAT_SLUG.items():
        if any(i["category"] == cat for i in items):
            (DIST / "c" / f"{cslug}.html").write_text(category_page(cat, cslug, items), encoding="utf-8")
    (DIST / "index.html").write_text(index(items), encoding="utf-8")
    (DIST / "saju.html").write_text(saju_page(), encoding="utf-8")
    urls = ["/", "/saju.html"] + [f"/c/{CAT_SLUG[i['category']]}.html" for i in items] + [f"/d/{i['slug']}.html" for i in items]
    urls = sorted(set(urls))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{SITE_URL}{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    if ADSENSE_CLIENT:
        pub = ADSENSE_CLIENT.replace("ca-", "")
        (DIST / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    if CNAME:
        (DIST / "CNAME").write_text(CNAME + "\n", encoding="utf-8")
    print(f"built {len(items)} dream pages, {len(urls)} sitemap urls")

if __name__ == "__main__":
    main()
