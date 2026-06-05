"""QuestionBank — File-backed interview question store.

Maps positions to curated interview questions.
Auto-populates with high-quality seed data on first use.
Refresh endpoint fetches fresh questions from public GitHub sources.
"""

import json
import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from core.config import settings


# ── Built-in seed questions (high quality, curated) ──

SEED_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {
    "Backend Engineer": [
        {"question": "Design a URL shortening service like TinyURL. Walk through traffic estimates, data model, API design, and scaling strategy.", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "How would you design a rate limiter for a high-traffic API? Compare token bucket vs. leaky bucket approaches.", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "Explain database indexing strategies. When would you use a B-tree vs a hash index?", "topic": "database", "difficulty": 3, "source": "curated"},
        {"question": "Design a real-time chat system that supports 10M concurrent users.", "topic": "system_design", "difficulty": 5, "source": "curated"},
        {"question": "What is the difference between REST and gRPC? When would you choose each?", "topic": "api_design", "difficulty": 2, "source": "curated"},
        {"question": "How does consistent hashing work and why is it important in distributed systems?", "topic": "distributed_systems", "difficulty": 4, "source": "curated"},
        {"question": "Design a payment system that handles idempotency and prevents double charges.", "topic": "system_design", "difficulty": 5, "source": "curated"},
        {"question": "Compare SQL vs NoSQL databases. How would you choose between PostgreSQL and MongoDB?", "topic": "database", "difficulty": 3, "source": "curated"},
        {"question": "Explain the CAP theorem. How does it affect distributed database design?", "topic": "distributed_systems", "difficulty": 3, "source": "curated"},
        {"question": "Design a caching strategy for a read-heavy social media feed. How do you handle cache invalidation?", "topic": "caching", "difficulty": 4, "source": "curated"},
        {"question": "How would you design a webhook delivery system with retry logic and exactly-once semantics?", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "What is the difference between process and thread? How does the GIL affect Python concurrency?", "topic": "concurrency", "difficulty": 3, "source": "curated"},
        {"question": "Design a distributed job scheduler that can handle millions of scheduled tasks.", "topic": "system_design", "difficulty": 5, "source": "curated"},
        {"question": "Explain how you would design a search autocomplete system (like Google Suggest).", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "What strategies do you use for database migration in a zero-downtime deployment?", "topic": "database", "difficulty": 3, "source": "curated"},
    ],
    "Software Engineer": [
        {"question": "Design a parking lot system. Cover object-oriented design patterns.", "topic": "ood", "difficulty": 3, "source": "curated"},
        {"question": "Implement a function to detect a cycle in a linked list. What is the time and space complexity?", "topic": "algorithms", "difficulty": 3, "source": "curated"},
        {"question": "Design a collaborative document editing system like Google Docs.", "topic": "system_design", "difficulty": 5, "source": "curated"},
        {"question": "Explain the Observer pattern. When would you use it instead of Pub-Sub?", "topic": "design_patterns", "difficulty": 2, "source": "curated"},
        {"question": "How would you design a web crawler that can crawl 1 billion pages?", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "Write a function to determine if two strings are anagrams. Optimize for large inputs.", "topic": "algorithms", "difficulty": 2, "source": "curated"},
        {"question": "Design a version control system like Git. How does branching work internally?", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "What is dependency injection? How does it improve testability?", "topic": "design_patterns", "difficulty": 2, "source": "curated"},
        {"question": "Explain the difference between vertical and horizontal scaling. When would you choose each?", "topic": "architecture", "difficulty": 2, "source": "curated"},
        {"question": "Design a social media news feed algorithm that balances relevance and recency.", "topic": "system_design", "difficulty": 4, "source": "curated"},
        {"question": "How do you handle error handling in a microservices architecture? What is a circuit breaker?", "topic": "architecture", "difficulty": 3, "source": "curated"},
        {"question": "Design a key-value store with ACID transactions.", "topic": "system_design", "difficulty": 5, "source": "curated"},
        {"question": "Explain the SOLID principles with concrete examples.", "topic": "ood", "difficulty": 3, "source": "curated"},
        {"question": "How would you design a logging system for a distributed application?", "topic": "system_design", "difficulty": 3, "source": "curated"},
    ],
    "AI Engineer": [
        {"question": "Design a recommendation system for a video streaming platform like Netflix.", "topic": "ml_system_design", "difficulty": 4, "source": "curated"},
        {"question": "Explain the Transformer architecture. How does self-attention work?", "topic": "deep_learning", "difficulty": 4, "source": "curated"},
        {"question": "Design a real-time fraud detection pipeline. How do you handle data drift?", "topic": "ml_system_design", "difficulty": 5, "source": "curated"},
        {"question": "What is the difference between L1 and L2 regularization? When would you use each?", "topic": "ml_theory", "difficulty": 3, "source": "curated"},
        {"question": "Design an LLM serving platform with low latency. How do you handle context windows?", "topic": "ml_system_design", "difficulty": 5, "source": "curated"},
        {"question": "Explain the RAG (Retrieval Augmented Generation) architecture. How would you evaluate its performance?", "topic": "llm", "difficulty": 4, "source": "curated"},
        {"question": "How do you handle class imbalance in a classification problem? Compare SMOTE vs weighted loss.", "topic": "ml_theory", "difficulty": 3, "source": "curated"},
        {"question": "Design a model training infrastructure that supports distributed training.", "topic": "mlops", "difficulty": 4, "source": "curated"},
        {"question": "What is the bias-variance tradeoff? How does it affect model selection?", "topic": "ml_theory", "difficulty": 3, "source": "curated"},
        {"question": "Design an A/B testing framework for evaluating model performance in production.", "topic": "mlops", "difficulty": 4, "source": "curated"},
        {"question": "Explain how embeddings work. How would you train a custom embedding for a domain-specific task?", "topic": "nlp", "difficulty": 3, "source": "curated"},
        {"question": "Design a search engine using vector similarity. How do you handle scaling to billions of vectors?", "topic": "ml_system_design", "difficulty": 5, "source": "curated"},
        {"question": "How do you detect and mitigate bias in ML models? Give concrete examples.", "topic": "ml_ethics", "difficulty": 3, "source": "curated"},
    ],
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BANK_FILE = os.path.join(DATA_DIR, "question_bank.json")


class QuestionBank:
    """File-backed question bank with refresh capability."""

    def __init__(self) -> None:
        self._questions: Dict[str, List[Dict[str, Any]]] = {}
        self._load()

    # ── Public API ──

    def get_questions(
        self,
        position: str,
        topic: Optional[str] = None,
        difficulty: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get questions for a position, with optional filters."""
        questions = self._questions.get(position, [])
        if not questions:
            questions = SEED_QUESTIONS.get(position, [])

        filtered = list(questions)
        if topic:
            filtered = [q for q in filtered if q.get("topic") == topic]
        if difficulty:
            filtered = [q for q in filtered if q.get("difficulty") == difficulty]

        # Shuffle for variety
        random.shuffle(filtered)
        return filtered[:limit]

    def get_all_positions(self) -> List[str]:
        """Get all positions with questions."""
        keys = set(self._questions.keys()) | set(SEED_QUESTIONS.keys())
        return sorted(keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get question bank statistics."""
        total = 0
        by_position: Dict[str, int] = {}
        by_topic: Dict[str, int] = {}

        for pos, questions in self._get_all().items():
            count = len(questions)
            total += count
            by_position[pos] = count
            for q in questions:
                topic = q.get("topic", "other")
                by_topic[topic] = by_topic.get(topic, 0) + 1

        return {
            "total_questions": total,
            "positions": len(by_position),
            "by_position": by_position,
            "by_topic": by_topic,
            "last_updated": self._get_last_updated(),
        }

    def refresh(self, new_questions: Dict[str, List[Dict[str, Any]]]) -> int:
        """Merge new questions into the bank. Returns count added."""
        count = 0
        for position, questions in new_questions.items():
            if position not in self._questions:
                self._questions[position] = []
            existing = {q["question"] for q in self._questions[position]}
            for q in questions:
                if q["question"] not in existing:
                    q["source"] = q.get("source", "web")
                    q["updated"] = datetime.now(timezone.utc).isoformat()[:10]
                    self._questions[position].append(q)
                    existing.add(q["question"])
                    count += 1

        self._save()
        return count

    # ── Internal ──

    def _get_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return merged seed + stored questions."""
        merged = {}
        for pos in set(list(SEED_QUESTIONS.keys()) + list(self._questions.keys())):
            seed = SEED_QUESTIONS.get(pos, [])
            stored = self._questions.get(pos, [])
            seen = {q["question"] for q in seed}
            merged[pos] = seed + [q for q in stored if q["question"] not in seen]
        return merged

    def _load(self) -> None:
        """Load questions from JSON file."""
        if os.path.exists(BANK_FILE):
            try:
                with open(BANK_FILE, "r") as f:
                    self._questions = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._questions = {}

    def _save(self) -> None:
        """Save questions to JSON file."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(BANK_FILE, "w") as f:
            json.dump(self._questions, f, indent=2, ensure_ascii=False)

    def _get_last_updated(self) -> Optional[str]:
        """Get the last modified time of the bank file."""
        if os.path.exists(BANK_FILE):
            ts = os.path.getmtime(BANK_FILE)
            return datetime.fromtimestamp(ts).isoformat()[:10]
        return None


# Singleton
bank = QuestionBank()
