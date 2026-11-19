#!/usr/bin/env python3
"""운세 나침반 빌드 — data/dreams.json -> dist/ 정적 사이트 생성.
구조: 홈(검색) → 키워드 랜딩(상황 선택) → 상황별 결과 페이지 (입력→결과보기 흐름)."""
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

def ad():
    # 수동 슬롯이 없으면(자동광고만) 빈 광고 상자를 만들지 않는다 — 빈 공간만 생긴다.
    # 자동광고는 구글 스크립트가 알아서 자리를 잡는다. 슬롯을 설정하면 그때 상자가 생긴다.
    if not ADSENSE_CLIENT or not AD_SLOT:
        return ""
    return (f'<div class="ad"><ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{AD_SLOT}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></div>')

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
<meta name="naver-site-verification" content="120c5b1ca1cf7137de31a13d4352a702cf13457f">
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
<header class="top"><a class="brand" href="/">🧭 {SITE_NAME}</a><nav><a href="/#dreams">꿈해몽</a></nav></header>
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

def _asset_path(base):
    for ext in ("jpg", "png"):
        p = ROOT / "assets" / f"{base}.{ext}"
        if p.exists():
            return p
    return None

def _fonts():
    from PIL import ImageFont
    bold = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    return ImageFont.truetype(bold, 30), ImageFont.truetype(bold, 64)

def composite_card(asset_base, out_name, big_text, brand_line):
    """일러스트(assets) 위에 하단 남색 반투명 띠+글자를 얹은 공유 카드(1200×630 JPG)."""
    from PIL import Image, ImageDraw
    out = DIST / "cards" / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    src = _asset_path(asset_base)
    if src is None:
        return False
    img = Image.open(src).convert("RGB")
    if img.size != (1200, 630):
        img = img.resize((1200, 630))
    band = Image.new("RGBA", (1200, 150), (18, 58, 109, 208))
    img.paste(band, (0, 630 - 150), band)
    d = ImageDraw.Draw(img)
    f_brand, f_big = _fonts()
    d.text((48, 630 - 150 + 14), brand_line, font=f_brand, fill=(243, 201, 105))
    d.text((48, 630 - 150 + 54), big_text, font=f_big, fill=(255, 255, 255))
    img.save(out, "JPEG", quality=88)
    return True

def make_card(item):
    if composite_card(item["slug"], f"{item['slug']}.jpg", f"{item['keyword']} 꿈해몽", SITE_NAME):
        return
    from PIL import Image, ImageDraw, ImageFont
    out = DIST / "cards" / f"{item['slug']}.jpg"
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
    img.save(out, "JPEG", quality=88)

def rel_block(item, by_keyword):
    rel = [by_keyword[r] for r in item.get("related", []) if r in by_keyword]
    if not rel:
        return ""
    links = "".join(f'<a class="chip" href="/d/{r["slug"]}.html">{esc(r["keyword"])} 꿈해몽</a>' for r in rel)
    return f'<section class="rel"><h2>함께 보는 꿈해몽</h2><div class="chips">{links}</div></section>'

def landing(item, by_keyword):
    kw = item["keyword"]
    title = f"{kw} 꿈해몽 — 어떤 꿈이었나요? | {SITE_NAME}"
    desc = item["intro"][:150]
    parts = [head(title, desc, f"/d/{item['slug']}.html", f"/cards/{item['slug']}.jpg")]
    parts.append(f'<p class="crumb"><a href="/">홈</a> · <a href="/c/{CAT_SLUG.get(item["category"], "things")}.html">{esc(item["category"])}</a> · 꿈해몽</p>')
    parts.append(f"<h1>{esc(kw)} 꿈해몽</h1>")
    parts.append(f'<p class="intro">{esc(item["intro"])}</p>')
    parts.append(ad())
    parts.append(f'<section class="pick"><h2>어떤 {esc(kw)} 꿈이었나요?</h2><p class="picksub">꿈 내용을 골라보세요. 상황마다 풀이가 다릅니다.</p>')
    btns = []
    for n, s in enumerate(item["situations"], 1):
        cls = TONE_CLASS.get(s["tone"], "mid")
        btns.append(
            f'<a class="sitbtn" href="/d/{item["slug"]}/{n}.html">'
            f'<span class="sitbtn-t">{esc(s["title"])}</span>'
            f'<span class="tone {cls}">{esc(s["tone"])}</span>'
            f'<span class="sitbtn-go">결과 확인하기 ›</span></a>')
    parts.append("".join(btns) + "</section>")
    parts.append(rel_block(item, by_keyword))
    parts.append(FOOT)
    return "".join(parts)

def result_page(item, n, s, by_keyword):
    kw = item["keyword"]
    title = f"{s['title']} 해몽 — {s['tone']} | {SITE_NAME}"
    desc = s["meaning"][:150]
    parts = [head(title, desc, f"/d/{item['slug']}/{n}.html", f"/cards/{item['slug']}.jpg")]
    parts.append(f'<p class="crumb"><a href="/">홈</a> · <a href="/d/{item["slug"]}.html">{esc(kw)} 꿈해몽</a> · 결과</p>')
    cls = TONE_CLASS.get(s["tone"], "mid")
    parts.append(f'<h1>{esc(s["title"])} <span class="tone {cls}">{esc(s["tone"])}</span></h1>')
    parts.append(ad())
    parts.append(f'<section class="sit"><p class="meaning">{esc(s["meaning"])}</p></section>')
    parts.append(ad())
    others = []
    for m, o in enumerate(item["situations"], 1):
        if m == n:
            continue
        others.append(f'<a class="sitbtn small" href="/d/{item["slug"]}/{m}.html"><span class="sitbtn-t">{esc(o["title"])}</span><span class="sitbtn-go">결과 확인하기 ›</span></a>')
    parts.append(f'<section class="pick"><h2>다른 {esc(kw)} 꿈도 확인해 보세요</h2>' + "".join(others) + "</section>")
    parts.append(rel_block(item, by_keyword))
    parts.append(f'<p class="center"><a class="btn" href="/">다른 꿈 검색하기</a></p>')
    parts.append(FOOT)
    return "".join(parts)

def index(items):
    title = f"{SITE_NAME} | 꿈해몽 — 상황별 꿈풀이"
    desc = "어젯밤 그 꿈, 무슨 뜻일까요? 키워드를 입력하고 상황을 고르면 해몽을 확인할 수 있습니다."
    parts = [head(title, desc, "/", "/cards/home.jpg")]
    parts.append("<h1>어젯밤 꿈, 무슨 뜻일까요?</h1>")
    parts.append('<div class="search"><input id="q" type="search" placeholder="꿈 키워드 입력 (예: 돼지, 똥, 떨어지는 꿈)" autocomplete="off"><button id="go" type="button">결과 확인하기</button><div id="noresult" class="hidden">찾는 키워드가 아직 없어요. 아래 목록에서 골라보세요.</div></div>')
    cats = []
    for cat, cslug in CAT_SLUG.items():
        group = [i for i in items if i["category"] == cat]
        if not group:
            continue
        cards = "".join(
            f'<a class="card" data-kw="{esc(i["keyword"])}" data-slug="{esc(i["slug"])}" href="/d/{i["slug"]}.html">'
            f'<span class="cardkw">{esc(i["keyword"])}</span><span class="cardsub">꿈해몽 · 상황 {len(i["situations"])}가지</span></a>'
            for i in group)
        cats.append(f'<section class="cat" id="cat-{cslug}"><h2><a href="/c/{cslug}.html">{esc(cat)}</a></h2><div class="grid">{cards}</div></section>')
    parts.append('<div id="dreams">' + "".join(cats) + "</div>")
    parts.append(FOOT)
    return "".join(parts)

def category_page(cat, cslug, items):
    group = [i for i in items if i["category"] == cat]
    title = f"{cat} 꿈해몽 모음 | {SITE_NAME}"
    parts = [head(title, f"{cat} 관련 꿈해몽 {len(group)}가지 키워드를 모았습니다.", f"/c/{cslug}.html", f"/cards/cat_{cslug}.jpg")]
    parts.append(f'<p class="crumb"><a href="/">홈</a> · 꿈해몽</p><h1>{esc(cat)} 꿈해몽</h1>')
    cards = "".join(
        f'<a class="card" href="/d/{i["slug"]}.html"><span class="cardkw">{esc(i["keyword"])}</span>'
        f'<span class="cardsub">{esc(i["intro"][:60])}…</span></a>' for i in group)
    parts.append(f'<div class="grid">{cards}</div>')
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
    composite_card("home", "home.jpg", SITE_NAME, "꿈해몽 · 상황별 풀이")
    for cat, cslug in CAT_SLUG.items():
        if any(i["category"] == cat for i in items):
            composite_card(f"cat_{cslug}", f"cat_{cslug}.jpg", f"{cat} 꿈해몽", SITE_NAME)
    n_results = 0
    for item in items:
        make_card(item)
        (DIST / "d" / f"{item['slug']}.html").write_text(landing(item, by_keyword), encoding="utf-8")
        sub = DIST / "d" / item["slug"]
        sub.mkdir(exist_ok=True)
        for n, s in enumerate(item["situations"], 1):
            (sub / f"{n}.html").write_text(result_page(item, n, s, by_keyword), encoding="utf-8")
            n_results += 1
    for cat, cslug in CAT_SLUG.items():
        if any(i["category"] == cat for i in items):
            (DIST / "c" / f"{cslug}.html").write_text(category_page(cat, cslug, items), encoding="utf-8")
    (DIST / "index.html").write_text(index(items), encoding="utf-8")
    urls = ["/"] + [f"/c/{CAT_SLUG[i['category']]}.html" for i in items] \
        + [f"/d/{i['slug']}.html" for i in items] \
        + [f"/d/{i['slug']}/{n}.html" for i in items for n in range(1, len(i["situations"]) + 1)]
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
    print(f"built {len(items)} landings, {n_results} result pages, {len(urls)} sitemap urls")

if __name__ == "__main__":
    main()
