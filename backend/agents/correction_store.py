"""CorrectionStore — Thread-safe in-memory correction cache.

Stores the latest expression correction for each session.
The correction API endpoint reads from here — no DB changes needed.
"""

from typing import Dict, Optional, Any
import threading


class CorrectionStore:
    """Singleton store for latest correction per session."""

    _instance: Optional["CorrectionStore"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self._data_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "CorrectionStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def put(self, session_id: str, correction: Dict[str, Any]) -> None:
        with self._data_lock:
            self._data[session_id] = correction

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._data.get(session_id)

    def clear(self, session_id: str) -> None:
        with self._data_lock:
            self._data.pop(session_id, None)
