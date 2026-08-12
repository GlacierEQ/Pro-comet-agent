"""Executable universal connector abstraction for Pro Comet Agent.

The historical module claimed live OneDrive, Drive, Dropbox, Gmail, and GitHub
connectors while returning empty placeholder values. This replacement makes the
boundary truthful: concrete connectors must be registered explicitly, missing
connectors fail closed, and the generic orchestration/metrics/data utilities are
fully executable without pretending external access exists.
"""
from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import json
import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Iterable, Mapping, Sequence


class ConnectorSource(str, Enum):
    ONEDRIVE = "onedrive"
    GDRIVE = "gdrive"
    DROPBOX = "dropbox"
    GMAIL_CASEY = "gmail_casey"
    GMAIL_GLACIER = "gmail_glacier"
    GITHUB = "github"
    ALL = "all"


class ConnectorUnavailableError(RuntimeError):
    """Raised when a requested external connector has not been registered."""


class UnsupportedOperationError(RuntimeError):
    """Raised when a registered adapter does not expose the requested operation."""


@dataclass
class ToolMetrics:
    tool_name: str
    source: str
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    last_error: str | None = None
    last_error_time: str | None = None

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.call_count if self.call_count else 0.0

    @property
    def success_rate(self) -> float:
        return self.success_count / self.call_count if self.call_count else 1.0

    def record_success(self, latency_ms: float) -> None:
        self.call_count += 1
        self.success_count += 1
        self.total_latency_ms += latency_ms

    def record_error(self, error: BaseException, latency_ms: float) -> None:
        self.call_count += 1
        self.error_count += 1
        self.total_latency_ms += latency_ms
        self.last_error = f"{type(error).__name__}: {error}"
        self.last_error_time = datetime.now(timezone.utc).isoformat()

    def is_degraded(self, minimum_calls: int = 3, max_error_rate: float = 0.20) -> bool:
        return self.call_count >= minimum_calls and (self.error_count / self.call_count) > max_error_rate


class MetricsCollector:
    def __init__(self) -> None:
        self._metrics: dict[str, ToolMetrics] = {}
        self.started_at = datetime.now(timezone.utc)

    def get_or_create(self, tool_name: str, source: str) -> ToolMetrics:
        key = f"{tool_name}:{source}"
        if key not in self._metrics:
            self._metrics[key] = ToolMetrics(tool_name=tool_name, source=source)
        return self._metrics[key]

    def health_report(self) -> dict[str, Any]:
        values = list(self._metrics.values())
        total_calls = sum(item.call_count for item in values)
        total_success = sum(item.success_count for item in values)
        return {
            "started_at": self.started_at.isoformat(),
            "total_calls": total_calls,
            "success_count": total_success,
            "error_count": sum(item.error_count for item in values),
            "success_rate": total_success / total_calls if total_calls else 1.0,
            "degraded_tools": sorted(
                f"{item.tool_name}:{item.source}" for item in values if item.is_degraded()
            ),
            "tools": {
                f"{item.tool_name}:{item.source}": {
                    **asdict(item),
                    "avg_latency_ms": round(item.avg_latency_ms, 3),
                    "success_rate": round(item.success_rate, 6),
                }
                for item in values
            },
        }


class ConnectorAdapter(ABC):
    """Minimal asynchronous adapter contract used by the universal layer."""

    def __init__(self, source: ConnectorSource) -> None:
        if source is ConnectorSource.ALL:
            raise ValueError("ALL is a selector, not a concrete connector")
        self.source = source
        self.connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish the external connection or raise an exception."""

    @abstractmethod
    async def search(self, query: str, *, limit: int = 50) -> list[dict[str, Any]]:
        """Search the connector and return structured results."""

    @abstractmethod
    async def download(self, file_id: str) -> bytes:
        """Download one object by connector-native identifier."""

    async def upload(self, path: str, destination: str) -> dict[str, Any]:
        raise UnsupportedOperationError(f"{self.source.value} does not implement upload")

    async def list_folder(self, folder_id: str) -> list[dict[str, Any]]:
        raise UnsupportedOperationError(f"{self.source.value} does not implement list_folder")

    async def metadata(self, file_id: str) -> dict[str, Any]:
        raise UnsupportedOperationError(f"{self.source.value} does not implement metadata")

    async def send_message(self, to: str, body: str) -> dict[str, Any]:
        raise UnsupportedOperationError(f"{self.source.value} does not implement send_message")

    async def list_threads(self, *, limit: int = 50) -> list[dict[str, Any]]:
        raise UnsupportedOperationError(f"{self.source.value} does not implement list_threads")

    async def close(self) -> None:
        self.connected = False


AdapterFactory = Callable[[], ConnectorAdapter]


class LazyConnectorLoader:
    """Register, connect, reuse, and retire connector adapters deterministically."""

    def __init__(self, *, idle_timeout_s: float = 300.0, metrics: MetricsCollector | None = None) -> None:
        if idle_timeout_s <= 0:
            raise ValueError("idle_timeout_s must be positive")
        self.idle_timeout_s = float(idle_timeout_s)
        self.metrics = metrics or MetricsCollector()
        self._factories: dict[ConnectorSource, AdapterFactory] = {}
        self._loaded: dict[ConnectorSource, ConnectorAdapter] = {}
        self._last_used: dict[ConnectorSource, float] = {}
        self._lock = asyncio.Lock()

    @property
    def registered_sources(self) -> tuple[ConnectorSource, ...]:
        return tuple(sorted(self._factories, key=lambda item: item.value))

    def register(self, source: ConnectorSource | str, factory: AdapterFactory) -> None:
        resolved = self._source(source)
        if resolved is ConnectorSource.ALL:
            raise ValueError("cannot register ALL selector")
        self._factories[resolved] = factory

    def unregister(self, source: ConnectorSource | str) -> None:
        resolved = self._source(source)
        self._factories.pop(resolved, None)

    @staticmethod
    def _source(source: ConnectorSource | str) -> ConnectorSource:
        if isinstance(source, ConnectorSource):
            return source
        try:
            return ConnectorSource(source)
        except ValueError as exc:
            raise ValueError(f"unknown connector source: {source}") from exc

    async def _load(self, source: ConnectorSource) -> ConnectorAdapter:
        async with self._lock:
            adapter = self._loaded.get(source)
            if adapter is not None:
                self._last_used[source] = time.monotonic()
                return adapter
            factory = self._factories.get(source)
            if factory is None:
                raise ConnectorUnavailableError(
                    f"connector {source.value!r} is not registered; external access is unavailable"
                )
            adapter = factory()
            if adapter.source is not source:
                raise ValueError(
                    f"adapter factory registered for {source.value} returned {adapter.source.value}"
                )
            await adapter.connect()
            adapter.connected = True
            self._loaded[source] = adapter
            self._last_used[source] = time.monotonic()
            return adapter

    @asynccontextmanager
    async def get_adapter(self, source: ConnectorSource | str):
        resolved = self._source(source)
        if resolved is ConnectorSource.ALL:
            raise ValueError("ALL cannot be opened as one adapter")
        adapter = await self._load(resolved)
        try:
            yield adapter
        finally:
            self._last_used[resolved] = time.monotonic()

    async def close_idle(self, *, now: float | None = None) -> tuple[str, ...]:
        timestamp = time.monotonic() if now is None else now
        closed: list[str] = []
        for source, adapter in list(self._loaded.items()):
            if timestamp - self._last_used.get(source, timestamp) >= self.idle_timeout_s:
                await adapter.close()
                self._loaded.pop(source, None)
                self._last_used.pop(source, None)
                closed.append(source.value)
        return tuple(sorted(closed))

    async def close_all(self) -> None:
        for adapter in list(self._loaded.values()):
            await adapter.close()
        self._loaded.clear()
        self._last_used.clear()


class UniversalTools:
    """Small operational surface over explicitly registered connector adapters."""

    FILE_SOURCES = (
        ConnectorSource.ONEDRIVE,
        ConnectorSource.GDRIVE,
        ConnectorSource.DROPBOX,
        ConnectorSource.GITHUB,
    )
    EMAIL_SOURCES = (ConnectorSource.GMAIL_CASEY, ConnectorSource.GMAIL_GLACIER)

    def __init__(self, loader: LazyConnectorLoader | None = None) -> None:
        self.loader = loader or LazyConnectorLoader()
        self.metrics = self.loader.metrics

    async def _call(
        self,
        source: ConnectorSource,
        operation_name: str,
        operation: Callable[[ConnectorAdapter], Awaitable[Any]],
    ) -> Any:
        metric = self.metrics.get_or_create(operation_name, source.value)
        started = time.perf_counter()
        try:
            async with self.loader.get_adapter(source) as adapter:
                result = await operation(adapter)
        except BaseException as exc:
            metric.record_error(exc, (time.perf_counter() - started) * 1000.0)
            raise
        metric.record_success((time.perf_counter() - started) * 1000.0)
        return result

    def _selected_sources(
        self,
        selector: ConnectorSource | str,
        allowed: Sequence[ConnectorSource],
    ) -> tuple[ConnectorSource, ...]:
        resolved = self.loader._source(selector)
        if resolved is ConnectorSource.ALL:
            registered = set(self.loader.registered_sources)
            selected = tuple(source for source in allowed if source in registered)
            if not selected:
                raise ConnectorUnavailableError("no compatible connectors are registered")
            return selected
        if resolved not in allowed:
            raise ValueError(f"connector {resolved.value} is not valid for this operation")
        return (resolved,)

    async def search_files(
        self,
        query: str,
        source: ConnectorSource | str = ConnectorSource.ALL,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query must be non-empty")
        if limit < 1:
            raise ValueError("limit must be positive")
        sources = self._selected_sources(source, self.FILE_SOURCES)
        batches = await asyncio.gather(*(
            self._call(
                item,
                "search_files",
                lambda adapter, item=item: adapter.search(query, limit=limit),
            )
            for item in sources
        ))
        enriched: list[dict[str, Any]] = []
        for src, batch in zip(sources, batches, strict=True):
            for row in batch:
                enriched.append({"source": src.value, **dict(row)})
        return self.merge_results(enriched)[:limit]

    async def download_file(self, file_id: str, source: ConnectorSource | str) -> bytes:
        if not file_id.strip():
            raise ValueError("file_id must be non-empty")
        resolved = self.loader._source(source)
        if resolved not in self.FILE_SOURCES:
            raise ValueError(f"connector {resolved.value} is not a file source")
        data = await self._call(resolved, "download_file", lambda adapter: adapter.download(file_id))
        if not isinstance(data, bytes):
            raise TypeError("connector download() must return bytes")
        return data

    async def search_emails(
        self,
        query: str,
        account: ConnectorSource | str = ConnectorSource.ALL,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query must be non-empty")
        sources = self._selected_sources(account, self.EMAIL_SOURCES)
        batches = await asyncio.gather(*(
            self._call(
                item,
                "search_emails",
                lambda adapter, item=item: adapter.search(query, limit=limit),
            )
            for item in sources
        ))
        enriched = [
            {"source": src.value, **dict(row)}
            for src, batch in zip(sources, batches, strict=True)
            for row in batch
        ]
        return self.merge_results(enriched)[:limit]

    async def upload_file(
        self,
        path: str,
        destination: str,
        source: ConnectorSource | str,
    ) -> dict[str, Any]:
        resolved = self.loader._source(source)
        return await self._call(
            resolved,
            "upload_file",
            lambda adapter: adapter.upload(path, destination),
        )

    async def list_folder(
        self,
        folder_id: str,
        source: ConnectorSource | str,
    ) -> list[dict[str, Any]]:
        resolved = self.loader._source(source)
        return await self._call(resolved, "list_folder", lambda adapter: adapter.list_folder(folder_id))

    async def get_file_metadata(
        self,
        file_id: str,
        source: ConnectorSource | str,
    ) -> dict[str, Any]:
        resolved = self.loader._source(source)
        return await self._call(resolved, "metadata", lambda adapter: adapter.metadata(file_id))

    async def send_message(
        self,
        to: str,
        body: str,
        account: ConnectorSource | str,
    ) -> dict[str, Any]:
        resolved = self.loader._source(account)
        if resolved not in self.EMAIL_SOURCES:
            raise ValueError(f"connector {resolved.value} is not an email account")
        return await self._call(resolved, "send_message", lambda adapter: adapter.send_message(to, body))

    async def list_threads(
        self,
        account: ConnectorSource | str = ConnectorSource.ALL,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        sources = self._selected_sources(account, self.EMAIL_SOURCES)
        batches = await asyncio.gather(*(
            self._call(item, "list_threads", lambda adapter, item=item: adapter.list_threads(limit=limit))
            for item in sources
        ))
        return self.merge_results(
            {"source": src.value, **dict(row)}
            for src, batch in zip(sources, batches, strict=True)
            for row in batch
        )[:limit]

    @staticmethod
    def parse_data(data: str | bytes, format: str = "json") -> Any:
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        kind = format.lower()
        if kind == "json":
            return json.loads(text)
        if kind == "csv":
            return list(csv.DictReader(io.StringIO(text)))
        if kind == "xml":
            root = ET.fromstring(text)
            return {
                "tag": root.tag,
                "attributes": dict(root.attrib),
                "children": [
                    {"tag": child.tag, "attributes": dict(child.attrib), "text": child.text or ""}
                    for child in root
                ],
            }
        raise ValueError(f"unsupported data format: {format}")

    @staticmethod
    def merge_results(results: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate structured results without losing distinct source identities."""
        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in results:
            item = dict(row)
            stable_identity = item.get("id") or item.get("file_id") or item.get("url")
            if stable_identity is None:
                stable_identity = hashlib.sha256(
                    json.dumps(item, sort_keys=True, default=str, separators=(",", ":")).encode()
                ).hexdigest()
            key = f"{item.get('source', '')}:{stable_identity}"
            if key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    async def get_health_report(self) -> dict[str, Any]:
        return self.metrics.health_report()


__all__ = [
    "ConnectorAdapter",
    "ConnectorSource",
    "ConnectorUnavailableError",
    "LazyConnectorLoader",
    "MetricsCollector",
    "ToolMetrics",
    "UniversalTools",
    "UnsupportedOperationError",
]
