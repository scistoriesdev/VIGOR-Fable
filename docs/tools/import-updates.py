#!/usr/bin/env python3
"""Regenerate _updates/*.html and assets/img/updates/posts/ from the client's
Salesforce CMS export (the "content" and "media-content" zips).

    python3 docs/tools/import-updates.py content.zip media.zip

What it does: one page per cms_blog_post (front matter + cleaned body HTML),
banner/inline images copied in, resized to ≤1600px and recompressed, the
YouTube embed moved to the privacy domain, live-site links pointed at this
site. Posts without a date get `undated: true` and an `order` matching the
live index. Cards keep the live site's 675×506 thumbnail crops when present.
Skips `autoimmune-allegory` (an earlier near-duplicate of autoimmunity-allegory).
"""
import sys, zipfile, json, re, os, subprocess, unicodedata, html, tempfile

LOGO_KEYS = {"MC43LMZZLXEVBQLMVWZUWMHXNTPE", "MCNCSLU6UPOZCP3DFDVMAVE5XCFI"}  # old purple-butterfly logo
UNDATED_ORDER = {"january-updates-from-the-vigor-team": 1, "november-updates-from-the-vigor-team": 2,
                 "july-updates-from-the-vigor-team": 3, "team-spotlight-priscilla-romano-md": 4}
SKIP = {"autoimmune-allegory"}

def safe(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9._()-]+", "-", n)

def dims(p):
    o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", o).group(1)), int(re.search(r"pixelHeight: (\d+)", o).group(1))

def main(content_zip, media_zip):
    tmp = tempfile.mkdtemp()
    content, media_dir = os.path.join(tmp, "c"), os.path.join(tmp, "m")
    os.makedirs(content); os.makedirs(media_dir)
    zipfile.ZipFile(content_zip).extractall(content)
    z = zipfile.ZipFile(media_zip)
    for info in z.infolist():
        if info.is_dir(): continue
        with z.open(info) as s, open(os.path.join(media_dir, safe(os.path.basename(info.filename))), "wb") as d: d.write(s.read())
    media = {}
    for f in os.listdir(media_dir):
        if f.endswith(".json"):
            m = json.load(open(os.path.join(media_dir, f))); b = m["body"]
            media[m["contentKey"]] = {"file": safe(b["source"]["ref"]), "name": m["urlName"], "alt": (b.get("altText") or "").strip()}
    os.makedirs("assets/img/updates/posts", exist_ok=True); os.makedirs("_updates", exist_ok=True)
    thumbs = {f[:-4]: "/assets/img/updates/" + f for f in os.listdir("assets/img/updates") if f.endswith(".jpg")}
    placed = {}

    def place(key):
        if key in placed: return placed[key]
        m = media[key]; ext = os.path.splitext(m["file"])[1].lower()
        out = "assets/img/updates/posts/" + m["name"] + ext
        subprocess.run(["cp", os.path.join(media_dir, m["file"]), out], check=True)
        w, h = dims(out)
        if w > 1600: subprocess.run(["sips", "-Z", "1600", out], capture_output=True); w, h = dims(out)
        if os.path.getsize(out) > 600000 and ext == ".png":
            new = out[:-4] + ".jpg"; subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", out, "--out", new], capture_output=True); os.remove(out); out = new
        elif os.path.getsize(out) > 400000:
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", out, "--out", out], capture_output=True)
        placed[key] = ("/" + out, w, h, m["alt"]); return placed[key]

    def clean(b):
        b = b.replace("&nbsp;", " ")
        b = re.sub(r"<p>\s*(<br\s*/?>\s*)*</p>", "", b)
        b = re.sub(r"</?span[^>]*>", "", b)
        b = b.replace("<u>", "<strong>").replace("</u>", "</strong>")
        b = b.replace("<h1>", "<h2>").replace("</h1>", "</h2>").replace("<h4>", "<h3>").replace("</h4>", "</h3>")
        b = re.sub(r'<(p|h2|h3|li)\s+style="text-align: center;"', r'<\1 class="post-body__center"', b)
        b = re.sub(r'\s*style="[^"]*"', "", b)
        b = b.replace("<h2>", '<h2 class="t-heading-card">').replace("<h3>", '<h3 class="t-ui-strong">')
        b = re.sub(r'<p( class="post-body__center")?>', lambda m: '<p class="t-body%s">' % (" post-body__center" if m.group(1) else ""), b)
        b = re.sub(r"<(ul|ol)>", r'<\1 class="t-body">', b)
        def img(m):
            key = re.search(r"/cms/media/([A-Z0-9]+)", m.group(0)).group(1); p, w, h, alt = place(key)
            return "<img src=\"{{ '%s' | relative_url }}\" width=\"%d\" height=\"%d\" alt=\"%s\" decoding=\"async\">" % (p, w, h, html.escape(alt))
        b = re.sub(r"<img[^>]*>", img, b)
        def iframe(m):
            v = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]+)", m.group(1))
            return '<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/%s" title="Video" loading="lazy" allow="fullscreen; picture-in-picture"></iframe></div>' % v.group(1) if v else ""
        b = re.sub(r'<iframe[^>]*src="([^"]+)"[^>]*>\s*</iframe>', iframe, b)
        b = b.replace('href="https://vigor.umassmed.edu/vigor/s/blog"', "href=\"{{ '/updates/' | relative_url }}\"").replace('href="https://vigor.umassmed.edu"', "href=\"{{ '/' | relative_url }}\"")
        b = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener"', b)
        return re.sub(r"(<br\s*/?>\s*){2,}", "<br>", b).strip()

    n = 0
    for f in sorted(os.listdir(content)):
        d = json.load(open(os.path.join(content, f))); b = d["body"]; slug = d["urlName"]
        if slug in SKIP: continue
        title = b["Title"]; date = b.get("Date", "")
        kind = "spotlight" if title.startswith("Team Spotlight") else ("update" if "Update" in title else "article")
        ref = b["Blog_Banner_Image"]["ref"]; banner = None if ref in LOGO_KEYS else place(ref)
        thumb = thumbs.get(slug, "") or (banner[0] if banner else "")
        prev = "_updates/%s.html" % slug; excerpt = ""
        if os.path.exists(prev):                      # keep the hand-written card excerpt across re-imports
            m = re.search(r'^excerpt: "(.*?)"', open(prev).read(), re.M); excerpt = m.group(1) if m else ""
        fm = ["---", 'title: "%s"' % title.replace('"', '\\"')]
        fm += ["date: %s" % date] if date else ["undated: true   # the CMS has no date for this post", "order: %s" % UNDATED_ORDER.get(slug, 99)]
        fm += ["kind: %s" % kind, 'excerpt: "%s"   # DRAFT — client to approve' % excerpt, 'thumbnail: "%s"' % thumb, 'banner: "%s"' % (banner[0] if banner else ""),
               "banner_w: %s" % (banner[1] if banner else ""), "banner_h: %s" % (banner[2] if banner else ""),
               'banner_alt: "%s"' % (banner[3].replace('"', "") if banner else ""),
               "live_url: https://vigor.umassmed.edu/vigor/s/blog/cms-blog-post/%s-%s" % (slug, d["contentKey"]), "---"]
        open("_updates/%s.html" % slug, "w").write("\n".join(fm) + "\n" + clean(b.get("Body", "") or "") + "\n"); n += 1
    print(n, "posts written;", len(placed), "images placed")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
