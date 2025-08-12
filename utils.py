import re
import io
import collections,math
from typing import List
import difflib
from pypdf import PdfReader

BULLET_RE = re.compile(
    r"^\s*(?:[\u2022\u2023\u25E6\u2043\u2219\-\*\u00B7]|[0-9]+[.)])\s*"
)  # •, -, *, 1)

def extract_text_from_pdf(file_obj) -> str:
    try:
        file_obj.seek(0)
    except Exception:
        pass

    # Read the file content
    if hasattr(file_obj, 'read'):
        data = file_obj.read()
    else:
        data = file_obj
    
    # Convert to BytesIO if needed
    if not isinstance(data, (bytes, bytearray)):
        data = io.BytesIO(data).read()
    
    reader = PdfReader(io.BytesIO(data))
    
    raw_lines: list[str] = []
    
    # Extract text from each page using pypdf
    for page in reader.pages:
        page_text = page.extract_text() or ""
        raw_lines.extend(page_text.splitlines())

    merged_lines: list[str] = []
    current_bullet: str | None = None

    def flush_bullet():
        nonlocal current_bullet
        if current_bullet is not None:
            merged_lines.append(current_bullet.strip())
            current_bullet = None

    for ln in raw_lines:
        if not ln.strip():
            # Blank line
            flush_bullet()
            merged_lines.append("")
            continue

        if BULLET_RE.match(ln):
            # New bullet
            flush_bullet()
            current_bullet = ln.strip()
            continue

        #Continuation of a bullet
        if current_bullet is not None:
            if ln.startswith(" ") or (not BULLET_RE.match(ln) and not is_heading(ln)):
                current_bullet += " " + ln.strip()
                continue

        #non-bullet line(heading/section/etc.)
        flush_bullet()
        merged_lines.append(ln.strip())

    flush_bullet()

    return "\n".join(merged_lines)

#Parse Before / After
BEFORE_AFTER = re.compile(
    r"\*\*Before\*\*:\s*(.*?)\s*\n\s*\*\*After\*\*:\s*(.*?)\s*(?:\n|$)",
    re.I | re.S,
)

def extract_rewrites(feedback: str):
    rewrites = [{"before": b.strip(), "after": a.strip()} for b, a in BEFORE_AFTER.findall(feedback)]
    print("[extract_rewrites] Extracted rewrites:", rewrites)
    return rewrites

# strip leading bullet symbols/spaces for matching
BULLET_PREFIX = re.compile(r"^[\s•\-\*\u2022\u25E6\u2043\u22190-9.)]+")

def clean(text: str) -> str:
    return BULLET_PREFIX.sub("", text).strip()

def replace_bullets_whole_text(original_text: str, rewrites):
    """
    Replace each 'before' bullet from feedback with its 'after' text in the
    original resume, line by line, preserving the original bullet prefix.

    Matching is robust to leading bullet symbols, extra whitespace, and case.
    We try: exact normalized match → contains either way → fuzzy match.
    """
    def split_prefix(line: str):
        # Return (prefix_including_bullet, content_without_prefix)
        m = re.match(r"^\s*(?:[\u2022\u2023\u25E6\u2043\u2219\-\*\u00B7]|[0-9]+[.)])\s*", line)
        if m:
            return m.group(0), line[m.end():]
        return "", line.strip()

    def norm(txt: str) -> str:
        # Strip bullet prefix, collapse spaces, lowercase, remove most punctuation
        stripped = clean(txt)
        stripped = re.sub(r"[^a-z0-9%+.$/ ]+", " ", stripped.lower())
        return " ".join(stripped.split())

    def sim(a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a, b).ratio()

    lines = original_text.splitlines()
    #normalized contents for faster matching
    line_parts = [] 
    for ln in lines:
        prefix, content = split_prefix(ln)
        line_parts.append((prefix, content, norm(content)))

    for rw in rewrites:
        before = rw.get("before", "").strip()
        after = rw.get("after", "").strip()
        if not before or not after:
            print("[replace_bullets] Skipping empty pair:", rw)
            continue

        target_norm = norm(before)
        replaced = False

        # Pass 1: exact normalized match
        for i, (prefix, content, content_norm) in enumerate(line_parts):
            if content_norm == target_norm:
                print(f"[replace_bullets] Exact match → replacing line {i}: '{content[:60]}...'")
                lines[i] = f"{prefix}{after}"
                line_parts[i] = (prefix, after, norm(after))
                replaced = True
                break
        if replaced:
            continue

        # Pass 2: contains match (either direction)
        for i, (prefix, content, content_norm) in enumerate(line_parts):
            if target_norm and (target_norm in content_norm or content_norm in target_norm):
                print(f"[replace_bullets] Contains match → replacing line {i}: '{content[:60]}...'")
                lines[i] = f"{prefix}{after}"
                line_parts[i] = (prefix, after, norm(after))
                replaced = True
                break
        if replaced:
            continue

        # Pass 3: fuzzy match using difflib
        best_i, best_score = -1, 0.0
        for i, (_, content, content_norm) in enumerate(line_parts):
            score = sim(content_norm, target_norm)
            if score > best_score:
                best_score = score
                best_i = i
        if best_score >= 0.82 and best_i >= 0:
            prefix, content, _ = line_parts[best_i]
            print(f"[replace_bullets] Fuzzy match ({best_score:.2f}) → replacing line {best_i}: '{content[:60]}...'")
            lines[best_i] = f"{prefix}{after}"
            line_parts[best_i] = (prefix, after, norm(after))
            replaced = True

        if not replaced:
            print(f"[replace_bullets] NOT found → '{before[:70]}...'")

    return "\n".join(lines)

HEADINGS = {
    "education","work experience","experience","skills","projects",
    "certifications","activities","achievements","publications",
    "summary","objective","awards"
}

def is_heading(s: str) -> bool:
    t = s.strip()
    if not t:
        return False
    if t == t.upper() and len(t.split()) <= 6:
        return True
    if t.lower() in HEADINGS:
        return True
    if re.match(r"^[A-Z][A-Za-z &/\\-]+$", t) and len(t.split()) <= 6:
        return True
    return False

job_role_to_industry = {
    "Software Engineer": "Tech / Software Engineering",
    "Data Scientist": "Tech / Data Science & AI",
    "Product Manager": "Tech / Product Strategy",
    "UX Designer": "Design / User Experience",
    "Cybersecurity Analyst": "Information Security"
}

STOP = {
    "a","an","the","and","or","to","for","of","in","on","with",
    "by","from","at","as","is","are","be","was","were","this","that",
    "it","its","your","you","our","we","they","their"
}

def top_keywords(job_desc: str, k: int = 9) -> List[str]:
    text = re.sub(r"[^A-Za-z0-9 ]+", " ", job_desc.lower())
    tokens = [t for t in text.split() if t not in STOP and len(t) > 2]

    #unigram counts
    unigram_counter = collections.Counter(tokens)
    
    #bigram counts
    bigrams = [" ".join(bg) for bg in zip(tokens, tokens[1:])]
    bigrams = [
        b for b in bigrams
        if all(word not in STOP for word in b.split())
           and not b.isdigit()
    ]
    bigram_counter = collections.Counter(bigrams)

    #pick top keywords separately then combine
    #Get top unigrams (60% of k)
    unigram_count = max(1, int(k * 0.6))
    top_unigrams = [w.title().strip() for w, _ in unigram_counter.most_common(unigram_count * 2)]  # Get more to filter
    
    # Get top bigrams (40% of k) 
    bigram_count = k - unigram_count
    top_bigrams = [w.title().strip() for w, _ in bigram_counter.most_common(bigram_count * 2)]  # Get more to filter
    
    # Filter out numeric-only or single letters from both
    filtered_unigrams = [w for w in top_unigrams if not re.fullmatch(r"\d+", w) and len(w) > 1]
    filtered_bigrams = [w for w in top_bigrams if not re.fullmatch(r"\d+", w) and len(w) > 1]
    
    #Combine and return top k
    combined = filtered_unigrams[:unigram_count] + filtered_bigrams[:bigram_count]
    
    #If we don't have enough bigrams, fill with more unigrams
    if len(combined) < k:
        remaining_unigrams = [w for w in filtered_unigrams[unigram_count:] if w not in combined]
        combined.extend(remaining_unigrams[:k - len(combined)])
    
    return combined[:k]

ACTION_VERBS = {
    "led","built","designed","developed","implemented","created","deployed","optimized",
    "improved","automated","reduced","increased","launched","managed"
}

#checks amount of keywords in the updated resume
def keyword_score(resume_txt: str, jd_txt: str, weight=50):
    kws  = top_keywords(jd_txt, 20)                # pick 20 most salient
    hits = sum(1 for kw in kws if kw.lower() in resume_txt.lower())
    return weight * hits / len(kws or [1])

#checks if necessary sections are available
def section_score(resume_txt: str, weight=15):
    need = ["experience","education","skills"]
    have = sum(1 for s in need if s in resume_txt.lower())
    return weight * have / len(need)

#checks amount of numerical metrics in each bullet point(If atleast 1 is present in each bullet point then complete marks are given)
def impact_score(resume_txt: str, weight=15):
    nums = len(re.findall(r"\b\d[\d,\.]*\b", resume_txt))
    bullets = max(1, resume_txt.count("\n•")+resume_txt.count("\n-"))
    ratio = min(1, nums / bullets)                # want at least 1 number per bullet
    return weight * ratio

#checks amount of action verbs used(At 15 function gives full point)
def verb_score(resume_txt: str, weight=10):
    verbs = sum(1 for v in ACTION_VERBS if re.search(fr"\b{v}\b", resume_txt.lower()))
    return weight * min(1, verbs/15)         

#checks the length of the resume and assigns a score
def length_score(resume_txt: str, weight=10):
    words = len(resume_txt.split())
    if 250 <= words <= 900:   return weight           
    if words < 150:           return weight*0.3
    if words > 1200:          return weight*0.3
    return weight*0.6                                  # borderline

def ats_score(resume_txt: str, jd_txt: str="") -> int:
    return round(
          keyword_score(resume_txt, jd_txt)
        + section_score(resume_txt)
        + impact_score(resume_txt)
        + verb_score(resume_txt)
        + length_score(resume_txt)
    )