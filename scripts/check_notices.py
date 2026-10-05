"""Look for new exam notices on official sites and record them in notices.json.

It only DETECTS notices (title + link). It does not rewrite dates, fees or
syllabus, because parsing those from PDFs is unreliable. A human updates
data.json after the workflow opens an issue.
"""
import json, re, sys, datetime, urllib.request, urllib.parse
from html.parser import HTMLParser

SOURCES = {
    "ssc.gov.in": "https://ssc.gov.in/",
    "psc.wb.gov.in": "https://psc.wb.gov.in/",
    "prb.wb.gov.in": "https://prb.wb.gov.in/",
    "nrsc.gov.in": "https://www.nrsc.gov.in/",
    "niti.gov.in": "https://niti.gov.in/",
    "upsc.gov.in": "https://upsc.gov.in/",
    "ugcnet.nta.ac.in": "https://ugcnet.nta.ac.in/",
    "esri.in": "https://www.esri.in/",
    "harsac.org": "https://www.harsac.org/",
    "nabard.org": "https://www.nabard.org/",
    "recruitment.nic.in": "https://recruitment.nic.in/",
    "cdac.in": "https://www.cdac.in/",
    "meity.gov.in": "https://www.meity.gov.in/",
    "employmentnews.gov.in": "https://www.employmentnews.gov.in/",
    "ncs.gov.in": "https://www.ncs.gov.in/",
}
# Links on any source that look like a recruitment notice but match no listed exam
GENERIC = re.compile(r"recruit|vacanc|advertis|walk-in|young professional|\bjrf\b|career", re.I)
def host(url):
    return urllib.parse.urlparse(url).netloc.replace("www.", "")
HEADERS = {"User-Agent": "Mozilla/5.0 (exam-notice-checker; personal use)"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href, self.buf, self.out = None, [], []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href, self.buf = dict(attrs).get("href"), []

    def handle_data(self, data):
        if self.href is not None:
            self.buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            text = " ".join("".join(self.buf).split())
            if text:
                self.out.append((text, self.href))
            self.href = None


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def main():
    exams = json.load(open("data.json"))["exams"]
    state = json.load(open("notices.json"))
    seen = {n["url"] for n in state["notices"]}
    today = datetime.date.today().isoformat()
    new, errors = [], []

    for source, page in SOURCES.items():
        try:
            parser = Links()
            parser.feed(fetch(page))
        except Exception as e:  # site down or blocking: report, keep going
            errors.append(f"{source}: {e}")
            continue
        for text, href in parser.out:
            url = urllib.parse.urljoin(page, href)
            if url in seen or url.startswith("javascript"):
                continue
            low = text.lower()
            matched = False
            for ex in exams:
                if host(ex["site"]) != source:
                    continue
                if any(re.search(r"\b" + re.escape(k) + r"\b", low) for k in ex["keywords"]):
                    new.append({"title": text[:200], "url": url, "source": source,
                                "exam": ex["n"], "found": today})
                    seen.add(url)
                    matched = True
                    break
            if not matched and GENERIC.search(text) and url not in seen:
                new.append({"title": text[:200], "url": url, "source": source,
                            "exam": "Other (" + source + ")", "found": today})
                seen.add(url)

    state["notices"].extend(new)
    state["last_checked"] = today
    json.dump(state, open("notices.json", "w"), indent=1)

    for e in errors:
        print("WARN", e, file=sys.stderr)
    with open("new_notices.md", "w") as f:
        for n in new:
            f.write(f"- **{n['exam']}**: [{n['title']}]({n['url']}) ({n['source']})\n")
    print(f"{len(new)} new notice(s), {len(errors)} source error(s)")


if __name__ == "__main__":
    main()
