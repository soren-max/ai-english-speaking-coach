"""StrategyStore — In-memory cache for strategy analysis results.

Thread-safe singleton. No DB needed — stores the latest strategy
analysis for each session so the REST API can serve it.
"""

from typing import Dict, Optional, Any
import threading


class StrategyStore:
    """Singleton store for strategy analysis per session."""

    _instance: Optional["StrategyStore"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._data_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "StrategyStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def put(self, session_id: str, analysis: Dict[str, Any]) -> None:
        with self._data_lock:
            self._data[session_id] = analysis

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._data.get(session_id)

    def clear(self, session_id: str) -> None:
        with self._data_lock:
            self._data.pop(session_id, None)
