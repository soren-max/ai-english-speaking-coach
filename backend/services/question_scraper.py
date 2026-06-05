"""QuestionScraper — Fetches fresh interview questions from public sources.

Uses httpx to pull from GitHub repos and parse questions from markdown.
Gracefully handles network failures — question bank always has seed data.
"""

import re
from typing import Dict, List, Any, Optional

import httpx

from services.question_bank import bank


# ── GitHub sources with interview questions ──

GITHUB_SOURCES: List[Dict[str, Any]] = [
    # System Design Primer — has a dedicated "design" question section
    {
        "url": "https://raw.githubusercontent.com/donnemartin/system-design-primer/master/README.md",
        "position": "Backend Engineer",
        "section_markers": ["interview questions", "design a"],
    },
    # LeetCode-style interview questions collection
    {
        "url": "https://raw.githubusercontent.com/hxu296/leetcode-company-wise-interview-questions/master/README.md",
        "position": "Software Engineer",
        "section_markers": [],
    },
    # Coding interview university
    {
        "url": "https://raw.githubusercontent.com/jwasham/coding-interview-university/master/README.md",
        "position": "Software Engineer",
        "section_markers": [],
    },
]

TIMEOUT_SEC = 15


async def fetch_from_github() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch questions from GitHub raw sources.

    Falls back to empty dict if all sources fail.
    """
    result: Dict[str, List[Dict[str, Any]]] = {}

    async with httpx.AsyncClient(timeout=TIMEOUT_SEC, follow_redirects=True) as client:
        for source in GITHUB_SOURCES:
            try:
                resp = await client.get(
                    source["url"],
                    headers={"User-Agent": "InterviewGPT/1.0"},
                )
                if resp.status_code != 200:
                    continue

                text = resp.text
                questions = _extract_questions(text)

                if questions:
                    pos = source["position"]
                    if pos not in result:
                        result[pos] = []
                    for q_text in questions:
                        result[pos].append({
                            "question": q_text,
                            "topic": _classify_topic(q_text),
                            "difficulty": _estimate_difficulty(q_text),
                            "source": "github",
                        })

            except (httpx.HTTPError, httpx.TimeoutException, Exception):
                continue

    return result


def _extract_questions(text: str) -> List[str]:
    """Extract interview questions from markdown text.

    Uses multiple strategies:
    1. Look for lines starting with "Q:" or "Question:" (common in interview repos)
    2. Look for numbered lists ending with ?
    3. Look for bullet points ending with ? that contain interview keywords
    4. Fallback: any line ending with ? that mentions technical topics
    """
    questions: List[str] = []
    seen: set = set()

    # Strategy 1: Q: / Question: prefixed lines
    for match in re.finditer(r'(?:^|\n)\s*(?:[Qq]uestion[:\s]+|[Qq]:\s*)(.+?\?)', text, re.MULTILINE):
        q = match.group(1).strip()
        if 30 <= len(q) <= 500:
            key = q.lower()[:100]
            if key not in seen:
                seen.add(key)
                questions.append(q)

    lines = text.split("\n")

    for line in lines:
        raw = line.strip()
        # Remove markdown link syntax, bold, italic
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw)
        clean = re.sub(r'[*_#`]', '', clean)
        clean = re.sub(r'^\s*[\d]+\.\s*', '', clean)
        clean = re.sub(r'^\s*[-*+]\s+', '', clean)
        clean = clean.strip()

        # Only process unprocessed lines that end with ?
        if not clean.endswith("?"):
            continue
        key = clean.lower()[:100]
        if key in seen:
            continue
        if len(clean) < 30 or len(clean) > 500:
            continue

        # Filter out non-interview content
        skip_words = [
            "contribute", "contributing", "license", "installation",
            "setup", "prerequisites", "table of contents", "todo",
            "resources", "reference", "more info", "getting started",
            "what's next", "how to contribute",
        ]
        if any(w in clean.lower() for w in skip_words):
            continue

        # Prefer lines with technical interview keywords
        tech_keywords = [
            "design", "implement", "algorithm", "database", "system",
            "architecture", "scale", "api", "framework", "test",
            "optimize", "deploy", "cache", "distributed",
        ]
        has_tech = any(w in clean.lower() for w in tech_keywords)

        if has_tech:
            seen.add(key)
            questions.append(clean)

    return questions


def _classify_topic(question: str) -> str:
    """Classify a question into a topic area."""
    q = question.lower()
    if any(w in q for w in ["design", "architecture", "scale", "distributed", "system"]):
        return "system_design"
    if any(w in q for w in ["database", "sql", "nosql", "index", "query", "postgres"]):
        return "database"
    if any(w in q for w in ["algorithm", "sort", "search", "complexity", "data structure"]):
        return "algorithms"
    if any(w in q for w in ["cache", "redis", "cdn", "caching"]):
        return "caching"
    if any(w in q for w in ["api", "rest", "grpc", "endpoint", "graphql"]):
        return "api_design"
    if any(w in q for w in ["test", "testing", "unit", "integration", "tdd"]):
        return "testing"
    if any(w in q for w in ["deploy", "ci/cd", "pipeline", "devops", "docker", "k8s"]):
        return "devops"
    if any(w in q for w in ["ml", "machine learning", "model", "train", "neural", "deep learning"]):
        return "machine_learning"
    if any(w in q for w in ["thread", "concurrency", "parallel", "async"]):
        return "concurrency"
    return "general"


def _estimate_difficulty(question: str) -> int:
    """Estimate question difficulty (1-5)."""
    q = question.lower()
    score = 2
    depth_signals = ["design", "distributed", "scale", "optimize", "trade-off",
                     "compare", "vs", "million", "billion", "consistent",
                     "fault tolerant", "high availability"]
    for s in depth_signals:
        if s in q:
            score += 1
    if len(question) > 150:
        score += 0.5
    return min(max(int(score), 1), 5)
