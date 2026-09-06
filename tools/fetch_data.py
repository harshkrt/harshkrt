"""Pull live GitHub data for the profile dashboard into data.json.

Runs locally (gh auth) and in Actions (GH_TOKEN env). No third-party services.
"""
import json, subprocess, sys, collections, datetime, os

USER = "harshkrt"
# Every email that is actually Harsh. The .local one is a historical
# misconfiguration (hostname-derived); its commits are real work.
MINE = ("harsh@harshs-macbook-air.local", "hktg480@gmail.com",
        "90552627+harshk-codes@users.noreply.github.com",
        "90552627+harshkrt@users.noreply.github.com")


def gh(path, paginate=True):
    cmd = ["gh", "api", path]
    if paginate:
        cmd.append("--paginate")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    if out.returncode != 0:
        print(f"  ! {path}: {out.stderr.strip()[:120]}", file=sys.stderr)
        return None
    txt = out.stdout.strip()
    if not txt:
        return None
    # --paginate concatenates JSON arrays; stitch them back together.
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        merged = []
        dec = json.JSONDecoder()
        i = 0
        while i < len(txt):
            while i < len(txt) and txt[i] in " \n\r\t":
                i += 1
            if i >= len(txt):
                break
            obj, i = dec.raw_decode(txt, i)
            merged.extend(obj if isinstance(obj, list) else [obj])
        return merged


def main():
    print("fetching profile...")
    prof = gh(f"users/{USER}", paginate=False) or {}

    print("fetching repos...")
    repos = [r for r in (gh(f"users/{USER}/repos?per_page=100&sort=pushed") or [])
             if not r["fork"]]

    langs = collections.Counter()
    commit_days = collections.Counter()
    total_commits = 0
    unlinked = 0

    for r in repos:
        name = r["name"]
        lb = gh(f"repos/{USER}/{name}/languages", paginate=False) or {}
        # The profile repo is scaffolding for this dashboard, not a project —
        # counting its generator scripts would inflate the language mix.
        if name != USER:
            for k, v in lb.items():
                langs[k] += v
        r["_langs"] = lb

        commits = gh(f"repos/{USER}/{name}/commits?per_page=100") or []
        if not isinstance(commits, list):
            commits = []
        n = 0
        dates = []
        for c in commits:
            author = (c.get("commit") or {}).get("author") or {}
            email = (author.get("email") or "").lower()
            if email and email not in MINE:
                continue  # someone else's commit
            n += 1
            total_commits += 1
            if not c.get("author"):
                unlinked += 1
            date = (author.get("date") or "")[:10]
            if date:
                commit_days[date] += 1
                dates.append(date)
        r["_commits"] = n
        r["_first"] = min(dates) if dates else None
        r["_last"] = max(dates) if dates else None
        print(f"  {name}: {n} commits, {len(lb)} langs")

    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "profile": {k: prof.get(k) for k in
                    ("login", "name", "bio", "location", "created_at",
                     "public_repos", "followers")},
        "languages": dict(langs.most_common()),
        "commit_days": dict(sorted(commit_days.items())),
        "total_commits": total_commits,
        "unlinked_commits": unlinked,
        "repos": [{
            "name": r["name"], "description": r.get("description"),
            "homepage": r.get("homepage"), "language": r.get("language"),
            "stars": r["stargazers_count"], "pushed_at": r["pushed_at"][:10],
            "topics": r.get("topics", []), "langs": r["_langs"],
            "commits": r["_commits"], "archived": r.get("archived", False),
            "first_commit": r["_first"], "last_commit": r["_last"],
            "created_at": r["created_at"][:10],
        } for r in repos],
    }

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "data.json"), "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nwrote data.json — {total_commits} commits "
          f"({unlinked} still unlinked), {len(repos)} repos")


if __name__ == "__main__":
    main()
