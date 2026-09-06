"""Render the dashboard SVG panels from data.json, in light and dark.

GitHub serves README images through camo, so everything must be self-contained:
no external fonts, no external CSS, no scripts. System font stacks only.
"""
import json, os, datetime, math

W = 880  # GitHub's README content column

DARK = dict(name="dark", bg="#0D1117", panel="#161B22", panel2="#1C2129",
            border="#30363D", text="#E6EDF3", muted="#8B949E", dim="#6E7681",
            accent="#58A6FF", green="#3FB950", purple="#BC8CFF",
            orange="#FFA657", grid="#21262D", track="#21262D")
LIGHT = dict(name="light", bg="#FFFFFF", panel="#F6F8FA", panel2="#EEF1F4",
             border="#D0D7DE", text="#1F2328", muted="#59636E", dim="#818B98",
             accent="#0969DA", green="#1A7F37", purple="#8250DF",
             orange="#BC4C00", grid="#EAEEF2", track="#E4E8EC")

LANG_COLOR = {
    "TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Python": "#3572A5",
    "C++": "#F34B7D", "CSS": "#663399", "HTML": "#E34C26",
    "Jupyter Notebook": "#DA5B0B", "EJS": "#A91E50", "Dockerfile": "#384D54",
    "Shell": "#89E051", "C": "#555555", "Java": "#B07219", "SCSS": "#C6538C",
}

SANS = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace")


CUR = DARK  # current palette; set by render()


def col(c, p=None):
    """Resolve a palette token ('accent') or pass a literal colour through."""
    pal = p or CUR
    return pal.get(c, c) if isinstance(c, str) else c


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def clip(s, n):
    s = str(s or "")
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def text(x, y, s, size=13, fill="text", weight=400, font=SANS, anchor="start",
         p=None, opacity=None, spacing=None):
    o = f' opacity="{opacity}"' if opacity is not None else ""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    c = col(fill, p)
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{c}" text-anchor="{anchor}"{o}{ls}>'
            f'{esc(s)}</text>')


def rect(x, y, w, h, fill, p=None, rx=6, stroke=None, sw=1, opacity=None):
    c = col(fill, p)
    st = ""
    if stroke:
        sc = col(stroke, p)
        st = f' stroke="{sc}" stroke-width="{sw}"'
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{c}"{st}{o}/>')


def head(w, h, p, grid=False):
    defs = ""
    body = rect(0, 0, w, h, "bg", p, rx=0)
    if grid:
        defs = (f'<defs><pattern id="g" width="22" height="22" '
                f'patternUnits="userSpaceOnUse">'
                f'<circle cx="1.5" cy="1.5" r="1.2" fill="{p["grid"]}"/>'
                f'</pattern>'
                f'<linearGradient id="vig" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="35%" stop-color="{p["bg"]}" stop-opacity="0"/>'
                f'<stop offset="100%" stop-color="{p["bg"]}" stop-opacity="0.95"/>'
                f'</linearGradient></defs>')
        body += f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
        body += f'<rect width="{w}" height="{h}" fill="url(#vig)"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">{defs}{body}')


def panel(x, y, w, h, p, title=None, ty=None):
    s = rect(x, y, w, h, "panel", p, rx=8, stroke="border")
    if title:
        s += text(x + 16, y + (ty or 24), title, 10.5, "dim", 600, MONO,
                  spacing="1.2")
    return s


# ---------------------------------------------------------------- header

def render_header(d, p):
    h = 188
    s = head(W, h, p, grid=True)

    # Mark: a small trace/span graph — the thing DTAD actually does.
    s += f'<g transform="translate(40,42)">'
    s += rect(0, 0, 52, 52, "panel", p, rx=13, stroke="border", sw=1.4)
    s += f'<circle cx="26" cy="15" r="3.6" fill="{p["accent"]}"/>'
    s += f'<circle cx="14" cy="36" r="3.6" fill="{p["green"]}"/>'
    s += f'<circle cx="38" cy="36" r="3.6" fill="{p["purple"]}"/>'
    for x2, y2 in ((14, 36), (38, 36)):
        s += (f'<line x1="26" y1="15" x2="{x2}" y2="{y2}" '
              f'stroke="{p["border"]}" stroke-width="1.6"/>')
    s += (f'<circle cx="26" cy="15" r="7" fill="none" stroke="{p["accent"]}" '
          f'stroke-width="1.2" opacity="0.5">'
          f'<animate attributeName="r" values="5;11;5" dur="3s" '
          f'repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0.6;0;0.6" dur="3s" '
          f'repeatCount="indefinite"/></circle>')
    s += '</g>'

    s += text(112, 66, d["profile"]["name"].strip(), 30, "text", 700)
    s += text(112, 92, "Full-stack engineer · building AI-native, "
                       "observable systems", 14, "muted", 400)

    # Status pills
    px = 112
    for label, col in (("Open to opportunities", "green"),
                       ("India · UTC+5:30", "muted"),
                       ("Building since 2021", "muted")):
        wpx = 8.2 * len(label) + 30
        s += rect(px, 108, wpx, 25, "panel", p, rx=12.5, stroke="border")
        s += (f'<circle cx="{px + 14}" cy="120.5" r="3.4" fill="{p[col]}">'
              + ('<animate attributeName="opacity" values="1;0.35;1" dur="2.2s"'
                 ' repeatCount="indefinite"/>' if col == "green" else "")
              + '</circle>')
        s += text(px + 24, 125, label, 11.5, "muted", 500, MONO)
        px += wpx + 9

    s += (f'<line x1="112" y1="152" x2="{W - 40}" y2="152" '
          f'stroke="{p["border"]}" stroke-width="1"/>')
    s += text(112, 172, "github.com/harshkrt", 11.5, "dim", 400, MONO)
    s += text(W - 40, 172, f"updated {d['generated'][:10]}", 11.5, "dim",
              400, MONO, anchor="end")
    return s + "</svg>"


# ---------------------------------------------------------------- overview

def render_overview(d, p):
    """Language mix + honest headline numbers, no vanity metrics."""
    h = 210
    s = head(W, h, p)

    langs = {k: v for k, v in d["languages"].items() if k in LANG_COLOR or True}
    total = sum(langs.values()) or 1
    top = list(langs.items())[:6]

    # --- left: KPI column
    cw = 250
    s += panel(0, 0, cw, h, p, "AT A GLANCE")

    shipped = sum(1 for r in d["repos"] if r["homepage"])
    years = datetime.date.today().year - int(d["profile"]["created_at"][:4])
    kpis = [(str(shipped), "apps deployed & live", "green"),
            (str(d["total_commits"]), "commits authored", "accent"),
            (str(len([r for r in d["repos"] if r["commits"] > 0])),
             "repositories built", "purple"),
            (f"{years}y", "writing code on GitHub", "orange")]
    y = 56
    for val, lab, col in kpis:
        s += f'<rect x="16" y="{y - 14}" width="3" height="30" rx="1.5" fill="{p[col]}"/>'
        s += text(30, y + 4, val, 21, "text", 700, MONO)
        s += text(30 + 11 * len(val) + 10, y + 3, lab, 11.5, "muted", 400)
        y += 38

    # --- right: language distribution
    x0 = cw + 14
    pw = W - x0
    s += panel(x0, 0, pw, h, p, "LANGUAGE DISTRIBUTION")

    bx, by, bw = x0 + 16, 46, pw - 32
    s += f'<clipPath id="lb"><rect x="{bx}" y="{by}" width="{bw}" height="13" rx="6.5"/></clipPath>'
    s += f'<g clip-path="url(#lb)">'
    cx = bx
    for name, size in top:
        seg = bw * size / total
        s += (f'<rect x="{cx:.2f}" y="{by}" width="{seg + 1:.2f}" height="13" '
              f'fill="{LANG_COLOR.get(name, p["dim"])}"/>')
        cx += seg
    if cx < bx + bw:
        s += (f'<rect x="{cx:.2f}" y="{by}" width="{bx + bw - cx:.2f}" '
              f'height="13" fill="{p["track"]}"/>')
    s += '</g>'

    # legend, two columns
    ly = 88
    for i, (name, size) in enumerate(top):
        col = i % 2
        row = i // 2
        lx = bx + col * (bw / 2)
        yy = ly + row * 27
        s += (f'<circle cx="{lx + 5}" cy="{yy - 4}" r="5" '
              f'fill="{LANG_COLOR.get(name, p["dim"])}"/>')
        s += text(lx + 18, yy, clip(name, 18), 12.5, "text", 500)
        s += text(lx + bw / 2 - 20, yy, f"{size / total * 100:.1f}%", 12,
                  "muted", 500, MONO, anchor="end")
    return s + "</svg>"


# ---------------------------------------------------------------- timeline

# Which era each project belongs to, for colour-coding the trajectory.
ERA = {
    "authentication-practice": "foundations", "first-cv": "foundations",
    "javascript-projects": "foundations", "Todo-list": "foundations",
    "Frontend-stuffs": "foundations", "My-Animations": "foundations",
    "DSA": "fundamentals", "Chain-Reaction": "fundamentals",
    "Portfolio": "fullstack", "crowdfunding-platform": "fullstack",
    "child-vaccination-tracking-system": "fullstack", "tenHours": "fullstack",
    "fleet-platform": "fullstack",
    "FinAgent": "ai", "DTAD": "ai",
}
ERA_COLOR = {"foundations": "dim", "fundamentals": "purple",
             "fullstack": "accent", "ai": "green"}
ERA_LABEL = [("foundations", "HTML/CSS/JS foundations"),
             ("fundamentals", "CS fundamentals"),
             ("fullstack", "Full-stack products"),
             ("ai", "AI & distributed systems")]


def render_timeline(d, p):
    """Every project as a bar spanning its real first→last commit date."""
    rows = [r for r in d["repos"]
            if r["commits"] and r["name"] != "harshkrt" and r["first_commit"]]
    rows.sort(key=lambda r: r["first_commit"])

    labw, rowh, padtop = 214, 25, 66
    h = padtop + len(rows) * rowh + 66
    s = head(W, h, p)
    s += panel(0, 0, W, h, p, "BUILD TIMELINE · WHAT I WAS LEARNING, WHEN")

    lo = datetime.date.fromisoformat(min(r["first_commit"] for r in rows))
    hi = datetime.date.today()
    lo = lo.replace(month=1, day=1)
    span = (hi - lo).days or 1
    x0, x1 = labw, W - 26
    tw = x1 - x0

    def px(datestr):
        dt = datetime.date.fromisoformat(datestr)
        return x0 + tw * (dt - lo).days / span

    # year gridlines
    for yr in range(lo.year, hi.year + 1):
        gx = px(f"{yr}-01-01")
        s += (f'<line x1="{gx:.1f}" y1="{padtop - 16}" x2="{gx:.1f}" '
              f'y2="{padtop + len(rows) * rowh - 6}" stroke="{col("border", p)}" '
              f'stroke-width="1" stroke-dasharray="2 4" opacity="0.7"/>')
        s += text(gx + 5, padtop - 22, str(yr), 10.5, "dim", 600, MONO)

    for i, r in enumerate(rows):
        y = padtop + i * rowh
        era = ERA.get(r["name"], "fullstack")
        c = col(ERA_COLOR[era], p)
        s += text(labw - 14, y + 4, clip(r["name"], 26), 11.5, "muted", 500,
                  MONO, anchor="end")

        a, b = px(r["first_commit"]), px(r["last_commit"])
        bw = max(b - a, 7)
        s += (f'<rect x="{a:.1f}" y="{y - 5}" width="{bw:.1f}" height="10" '
              f'rx="5" fill="{c}" opacity="0.9"><title>{esc(r["name"])}: '
              f'{r["first_commit"]} → {r["last_commit"]}, {r["commits"]} '
              f'commits</title></rect>')
        # end cap marks the most recent commit
        s += f'<circle cx="{b:.1f}" cy="{y}" r="3.4" fill="{c}"/>'
        if r["homepage"]:
            s += (f'<circle cx="{b + 12:.1f}" cy="{y}" r="2.6" fill="none" '
                  f'stroke="{col("green", p)}" stroke-width="1.4"/>')

    # legend — eras on one row, summary + deploy key on the next
    ly = padtop + len(rows) * rowh + 26
    lx = labw
    for key, label in ERA_LABEL:
        s += (f'<rect x="{lx}" y="{ly - 8}" width="15" height="8" rx="4" '
              f'fill="{col(ERA_COLOR[key], p)}"/>')
        s += text(lx + 21, ly, label, 10.4, "muted", 400)
        lx += 21 + 6.1 * len(label) + 20

    sy = ly + 21
    s += text(labw, sy, f"{len(rows)} projects · {d['total_commits']} commits · "
              f"first commit {min(r['first_commit'] for r in rows)}",
              10.4, "dim", 400)
    s += (f'<circle cx="{W - 116}" cy="{sy - 4}" r="2.6" fill="none" '
          f'stroke="{col("green", p)}" stroke-width="1.4"/>')
    s += text(W - 106, sy, "deployed & live", 10.4, "dim", 400)
    return s + "</svg>"


# ---------------------------------------------------------------- projects

# Curated: role + what makes each one non-trivial, grounded in real manifests.
FEATURED = [
    ("DTAD", "Distributed Trace Anomaly Detector",
     "OpenTelemetry spans → Node processor → FastAPI + scikit-learn scorer",
     ["Next.js", "OpenTelemetry", "FastAPI", "scikit-learn", "MongoDB"],
     "building"),
    ("tenHours", "Sanitary-care e-commerce",
     "Dual payment rails (Razorpay + Cashfree), Google OAuth, Cloudinary media",
     ["React", "Redux Toolkit", "Express", "MongoDB", "TypeScript"], "live"),
    ("child-vaccination-tracking-system", "Vaccination scheduler",
     "Cron-driven immunisation reminders over a typed Express/Mongo backend",
     ["React", "Express", "TypeScript", "node-cron"], "live"),
    ("fleet-platform", "Fleet management API",
     "Zod-validated routes, rate limiting, Jest + Supertest integration suite",
     ["Express", "MongoDB", "Zod", "Jest"], "live"),
    ("FinAgent", "Multi-agent KPI extraction",
     "LangGraph agents over Weaviate + Neo4j, text-to-SQL on local Ollama",
     ["LangGraph", "Weaviate", "Neo4j", "Ollama", "FastAPI"], "paused"),
    ("Portfolio", "Personal site",
     "Next.js + Framer Motion, EmailJS contact pipeline",
     ["Next.js", "Tailwind", "Framer Motion"], "live"),
]


def render_projects(d, p):
    by_name = {r["name"]: r for r in d["repos"]}
    cols, cw, ch, gx, gy = 2, (W - 14) / 2, 132, 14, 14
    rows = math.ceil(len(FEATURED) / cols)
    h = rows * ch + (rows - 1) * gy
    s = head(W, h, p)

    status_col = {"building": "orange", "live": "green", "paused": "dim"}
    for i, (name, title, blurb, tags, status) in enumerate(FEATURED):
        r = by_name.get(name, {})
        cx = (i % cols) * (cw + gx)
        cy = (i // cols) * (ch + gy)
        s += rect(cx, cy, cw, ch, "panel", p, rx=8, stroke="border")
        s += (f'<rect x="{cx}" y="{cy}" width="3" height="{ch}" rx="1.5" '
              f'fill="{p[status_col[status]]}"/>')

        s += text(cx + 18, cy + 28, title, 14.5, "text", 650)
        # status chip
        chip = status.upper()
        cwid = 7.4 * len(chip) + 18
        s += rect(cx + cw - cwid - 14, cy + 15, cwid, 18, "panel2", p, rx=9)
        s += text(cx + cw - cwid / 2 - 14, cy + 27.5, chip, 9, status_col[status],
                  700, MONO, anchor="middle", spacing="0.6", p=p)

        s += text(cx + 18, cy + 46, name, 11, "dim", 500, MONO)
        # blurb, wrapped to two lines
        words, line, lines = blurb.split(), "", []
        for wd in words:
            if len(line) + len(wd) + 1 > 52:
                lines.append(line)
                line = wd
            else:
                line = f"{line} {wd}".strip()
        lines.append(line)
        for j, ln in enumerate(lines[:2]):
            s += text(cx + 18, cy + 68 + j * 16, ln, 12, "muted", 400)

        tx = cx + 18
        for t in tags:
            twid = 6.6 * len(t) + 16
            if tx + twid > cx + cw - 14:
                break
            s += rect(tx, cy + ch - 30, twid, 19, "panel2", p, rx=4,
                      stroke="border")
            s += text(tx + twid / 2, cy + ch - 16.5, t, 9.8, "muted", 500,
                      MONO, anchor="middle")
            tx += twid + 6
    return s + "</svg>"


# ---------------------------------------------------------------- stack

# Grounded in the repos above: each entry is either a dependency in a real
# manifest, or a platform those repos actually deploy to / run on.
STACK = [
    ("LANGUAGES", "accent",
     ["TypeScript", "JavaScript", "Python", "C++", "SQL"]),
    ("FRONTEND", "purple",
     ["React", "Next.js", "Redux Toolkit", "Tailwind", "Radix UI",
      "Framer Motion", "Vite", "Chart.js"]),
    ("BACKEND", "green",
     ["Node.js", "Express", "FastAPI", "MongoDB", "PostgreSQL", "Mongoose",
      "JWT", "Zod", "REST"]),
    ("AI / DATA", "orange",
     ["LangGraph", "LangChain", "scikit-learn", "Weaviate", "Neo4j",
      "Ollama", "pandas", "sentence-transformers"]),
    ("INFRA / OPS", "muted",
     ["Docker", "OpenTelemetry", "RabbitMQ", "GitHub Actions", "Jest",
      "Supertest", "Vercel", "Cloudinary"]),
]


def render_stack(d, p):
    rowh, padtop = 40, 20
    h = padtop + len(STACK) * rowh + 16
    s = head(W, h, p)
    s += panel(0, 0, W, h, p)

    y = padtop + 22
    for label, accent, items in STACK:
        s += (f'<rect x="16" y="{y - 12}" width="3" height="17" rx="1.5" '
              f'fill="{col(accent, p)}"/>')
        s += text(28, y + 1, label, 9.6, "dim", 700, MONO, spacing="1.1")
        tx = 132
        for it in items:
            twid = 6.8 * len(it) + 18
            if tx + twid > W - 16:
                break
            s += rect(tx, y - 13, twid, 21, "panel2", p, rx=5, stroke="border")
            s += text(tx + twid / 2, y + 1.5, it, 10.6, "muted", 500, MONO,
                      anchor="middle")
            tx += twid + 7
        y += rowh
    return s + "</svg>"


# ---------------------------------------------------------------- arch

# DTAD's real shape, read off its manifests: instrumented Next.js frontend,
# a Node span processor, Mongo, and a FastAPI/scikit-learn scorer.
NODES = [
    ("Next.js app", "@opentelemetry/sdk-node", "accent"),
    ("OTLP / HTTP", "exporter-trace-otlp-http", "muted"),
    ("processor", "Express · Node", "purple"),
    ("MongoDB", "span store", "orange"),
    ("ml-service", "FastAPI · scikit-learn", "green"),
]


def render_arch(d, p):
    h = 152
    s = head(W, h, p)
    s += panel(0, 0, W, h, p, "DTAD · TRACE PIPELINE")

    n = len(NODES)
    pad, gap = 22, 16
    bw = (W - 2 * pad - (n - 1) * gap) / n
    by, bh = 56, 56
    for i, (title, sub, c) in enumerate(NODES):
        x = pad + i * (bw + gap)
        s += rect(x, by, bw, bh, "panel2", p, rx=7, stroke="border")
        s += (f'<rect x="{x}" y="{by}" width="{bw}" height="2.5" rx="1.2" '
              f'fill="{col(c, p)}"/>')
        s += text(x + bw / 2, by + 26, title, 12, "text", 600, anchor="middle")
        s += text(x + bw / 2, by + 42, clip(sub, 26), 9.6, "dim", 400, MONO,
                  anchor="middle")
        if i < n - 1:
            ax = x + bw + 3
            ay = by + bh / 2
            s += (f'<line x1="{ax}" y1="{ay}" x2="{ax + gap - 6}" y2="{ay}" '
                  f'stroke="{col("border", p)}" stroke-width="1.4"/>')
            s += (f'<path d="M{ax + gap - 9},{ay - 3.2} L{ax + gap - 4},{ay} '
                  f'L{ax + gap - 9},{ay + 3.2} Z" fill="{col("dim", p)}"/>')

    s += text(pad, 130, "spans emitted → batched → persisted → scored for "
              "anomalies → surfaced on the dashboard", 11, "muted", 400)
    return s + "</svg>"


# ---------------------------------------------------------------- main

PANELS = {
    "header": render_header,
    "overview": render_overview,
    "timeline": render_timeline,
    "projects": render_projects,
    "arch": render_arch,
    "stack": render_stack,
}


def main():
    global CUR
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(here, "data.json")))
    out = os.path.join(here, "assets")
    os.makedirs(out, exist_ok=True)

    for pal in (DARK, LIGHT):
        CUR = pal
        for name, fn in PANELS.items():
            svg = fn(d, pal)
            path = os.path.join(out, f"{name}-{pal['name']}.svg")
            with open(path, "w") as f:
                f.write(svg)
            print(f"  {os.path.relpath(path, here)}  {len(svg):>6} bytes")
    print(f"\nrendered {len(PANELS) * 2} panels")


if __name__ == "__main__":
    main()
