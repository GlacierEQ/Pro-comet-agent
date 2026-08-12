from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.universal_tools_framework import (
    ConnectorAdapter,
    ConnectorSource,
    ConnectorUnavailableError,
    LazyConnectorLoader,
    UniversalTools,
    UnsupportedOperationError,
)


class FakeAdapter(ConnectorAdapter):
    def __init__(self, source: ConnectorSource, rows: list[dict] | None = None) -> None:
        super().__init__(source)
        self.rows = rows or []
        self.connect_count = 0
        self.close_count = 0

    async def connect(self) -> None:
        self.connect_count += 1

    async def search(self, query: str, *, limit: int = 50) -> list[dict]:
        return [dict(row, query=query) for row in self.rows[:limit]]

    async def download(self, file_id: str) -> bytes:
        return f"{self.source.value}:{file_id}".encode()

    async def close(self) -> None:
        self.close_count += 1
        await super().close()


class UniversalToolsTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_connector_fails_closed(self) -> None:
        tools = UniversalTools()
        with self.assertRaises(ConnectorUnavailableError):
            await tools.search_files("evidence", source=ConnectorSource.GDRIVE)

    async def test_search_all_uses_only_registered_sources_and_preserves_source(self) -> None:
        loader = LazyConnectorLoader()
        drive = FakeAdapter(ConnectorSource.GDRIVE, [{"id": "a", "name": "A"}])
        dropbox = FakeAdapter(ConnectorSource.DROPBOX, [{"id": "a", "name": "A-copy"}])
        loader.register(ConnectorSource.GDRIVE, lambda: drive)
        loader.register(ConnectorSource.DROPBOX, lambda: dropbox)
        tools = UniversalTools(loader)

        rows = await tools.search_files("case", source=ConnectorSource.ALL)

        self.assertEqual(len(rows), 2)
        self.assertEqual({row["source"] for row in rows}, {"gdrive", "dropbox"})
        self.assertTrue(all(row["query"] == "case" for row in rows))
        self.assertEqual(drive.connect_count, 1)
        self.assertEqual(dropbox.connect_count, 1)

    async def test_lazy_loader_reuses_connection(self) -> None:
        loader = LazyConnectorLoader()
        drive = FakeAdapter(ConnectorSource.GDRIVE, [{"id": "a"}])
        loader.register(ConnectorSource.GDRIVE, lambda: drive)
        tools = UniversalTools(loader)

        await tools.search_files("one", source=ConnectorSource.GDRIVE)
        await tools.search_files("two", source=ConnectorSource.GDRIVE)

        self.assertEqual(drive.connect_count, 1)
        report = await tools.get_health_report()
        metric = report["tools"]["search_files:gdrive"]
        self.assertEqual(metric["call_count"], 2)
        self.assertEqual(metric["success_count"], 2)
        self.assertEqual(report["error_count"], 0)

    async def test_unsupported_operations_are_explicit(self) -> None:
        loader = LazyConnectorLoader()
        drive = FakeAdapter(ConnectorSource.GDRIVE)
        loader.register(ConnectorSource.GDRIVE, lambda: drive)
        tools = UniversalTools(loader)

        with self.assertRaises(UnsupportedOperationError):
            await tools.upload_file("local.txt", "/remote", ConnectorSource.GDRIVE)

    async def test_download_returns_real_adapter_bytes(self) -> None:
        loader = LazyConnectorLoader()
        drive = FakeAdapter(ConnectorSource.GDRIVE)
        loader.register(ConnectorSource.GDRIVE, lambda: drive)
        tools = UniversalTools(loader)
        self.assertEqual(
            await tools.download_file("123", ConnectorSource.GDRIVE),
            b"gdrive:123",
        )

    async def test_idle_cleanup_closes_loaded_adapter(self) -> None:
        loader = LazyConnectorLoader(idle_timeout_s=1)
        drive = FakeAdapter(ConnectorSource.GDRIVE)
        loader.register(ConnectorSource.GDRIVE, lambda: drive)
        tools = UniversalTools(loader)
        await tools.search_files("x", source=ConnectorSource.GDRIVE)
        closed = await loader.close_idle(now=10**12)
        self.assertEqual(closed, ("gdrive",))
        self.assertEqual(drive.close_count, 1)

    def test_parse_data_executes_json_csv_and_xml(self) -> None:
        self.assertEqual(UniversalTools.parse_data('{"a":1}'), {"a": 1})
        self.assertEqual(
            UniversalTools.parse_data("a,b\n1,2\n", "csv"),
            [{"a": "1", "b": "2"}],
        )
        xml = UniversalTools.parse_data("<root><item id='1'>x</item></root>", "xml")
        self.assertEqual(xml["tag"], "root")
        self.assertEqual(xml["children"][0]["text"], "x")

    def test_merge_results_deduplicates_within_source_not_across_sources(self) -> None:
        rows = UniversalTools.merge_results(
            [
                {"source": "gdrive", "id": "1", "name": "A"},
                {"source": "gdrive", "id": "1", "name": "A duplicate"},
                {"source": "dropbox", "id": "1", "name": "A elsewhere"},
            ]
        )
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
