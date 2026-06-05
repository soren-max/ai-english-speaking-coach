"""CommunityStore — File-based storage for shared answers and peer reviews.

Thread-safe singleton. Stores data in backend/data/community/ directory.
No database changes needed.
"""

import json
import os
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "community")
SHARES_FILE = os.path.join(DATA_DIR, "shares.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "reviews.json")


class CommunityStore:
    """Singleton store for shared answers and peer reviews."""

    _instance: Optional["CommunityStore"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._shares: Dict[str, Dict[str, Any]] = {}
        self._reviews: Dict[str, List[Dict[str, Any]]] = {}
        self._data_lock = threading.Lock()
        self._load()

    @classmethod
    def get_instance(cls) -> "CommunityStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ── Share CRUD ──

    def create_share(self, data: Dict[str, Any]) -> Dict[str, Any]:
        share_id = str(uuid4())
        share = {
            "id": share_id,
            "session_id": data.get("session_id", ""),
            "question": data.get("question", ""),
            "answer": data.get("answer", ""),
            "position": data.get("position", "Unknown"),
            "is_anonymous": data.get("is_anonymous", True),
            "shared_at": datetime.now(timezone.utc).isoformat(),
            "view_count": 0,
            "ai_review": data.get("ai_review", None),
        }
        with self._data_lock:
            self._shares[share_id] = share
            self._reviews[share_id] = []
            self._save()
        return share

    def get_share(self, share_id: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            share = self._shares.get(share_id)
            if share:
                share["view_count"] = share.get("view_count", 0) + 1
                self._save()
                return {**share}
            return None

    def list_shares(
        self,
        position: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        with self._data_lock:
            items = list(self._shares.values())
            if position:
                items = [s for s in items if s.get("position") == position]
            items.sort(key=lambda s: s.get("shared_at", ""), reverse=True)
            total = len(items)
            start = (page - 1) * page_size
            end = start + page_size
            page_items = items[start:end]
            return {"items": page_items, "total": total, "page": page, "page_size": page_size}

    # ── Review CRUD ──

    def add_review(self, share_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            if share_id not in self._shares:
                return None
            review = {
                "id": str(uuid4()),
                "share_id": share_id,
                "reviewer_name": data.get("reviewer_name", "Anonymous Peer"),
                "rating": data.get("rating", 0),
                "comment": data.get("comment", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if share_id not in self._reviews:
                self._reviews[share_id] = []
            self._reviews[share_id].append(review)
            self._save()
            return review

    def get_reviews(self, share_id: str) -> List[Dict[str, Any]]:
        with self._data_lock:
            return list(self._reviews.get(share_id, []))

    def get_avg_rating(self, share_id: str) -> float:
        reviews = self.get_reviews(share_id)
        if not reviews:
            return 0.0
        ratings = [r.get("rating", 0) for r in reviews if r.get("rating")]
        return round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    # ── Stats ──

    def get_stats(self) -> Dict[str, Any]:
        with self._data_lock:
            total_shares = len(self._shares)
            total_reviews = sum(len(v) for v in self._reviews.values())
            positions = {}
            for s in self._shares.values():
                pos = s.get("position", "Unknown")
                positions[pos] = positions.get(pos, 0) + 1
            return {
                "total_shares": total_shares,
                "total_reviews": total_reviews,
                "positions": positions,
                "avg_reviews_per_share": round(total_reviews / total_shares, 1) if total_shares else 0,
            }

    def position_exists(self, position: str) -> bool:
        with self._data_lock:
            return any(s.get("position") == position for s in self._shares.values())

    # ── Persistence ──

    def _load(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(SHARES_FILE):
            try:
                with open(SHARES_FILE, "r") as f:
                    self._shares = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._shares = {}
        if os.path.exists(REVIEWS_FILE):
            try:
                with open(REVIEWS_FILE, "r") as f:
                    self._reviews = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._reviews = {}

    def _save(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SHARES_FILE, "w") as f:
            json.dump(self._shares, f, indent=2, ensure_ascii=False)
        with open(REVIEWS_FILE, "w") as f:
            json.dump(self._reviews, f, indent=2, ensure_ascii=False)
