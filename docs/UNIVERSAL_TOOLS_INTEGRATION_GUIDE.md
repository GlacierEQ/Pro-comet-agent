# Universal Tools Framework

## Current status

The framework is an **executable connector abstraction**, not a bundle of pre-authenticated external integrations.

It provides:

- explicit connector registration;
- lazy connection creation and reuse;
- parallel search across registered sources;
- structured downloads and optional adapter operations;
- deterministic source-aware deduplication;
- JSON, CSV, and XML parsing;
- per-operation latency/success/error metrics;
- idle connector cleanup;
- fail-closed behavior when a connector or operation is unavailable.

It does **not** claim live OneDrive, Google Drive, Dropbox, Gmail, or GitHub credentials merely because those connector names exist in the enum. Concrete external adapters must be registered by the runtime that actually owns those credentials and APIs.

## Why this changed

The historical module advertised “production-ready” integrations while its concrete adapter methods returned placeholder empty lists or byte strings. That was not an integration. The current implementation removes those fake-success paths.

## Architecture

```text
Caller
  ↓
UniversalTools
  ↓
LazyConnectorLoader
  ↓
explicitly registered ConnectorAdapter factory
  ↓
real external implementation supplied by the consuming runtime
```

If no compatible adapter is registered, the call raises `ConnectorUnavailableError`. Unsupported adapter operations raise `UnsupportedOperationError`. Empty output is therefore an actual connector result, not the framework pretending a missing integration succeeded.

## Core operations

```python
from modules.universal_tools_framework import (
    ConnectorAdapter,
    ConnectorSource,
    LazyConnectorLoader,
    UniversalTools,
)

loader = LazyConnectorLoader()
loader.register(ConnectorSource.GDRIVE, make_real_drive_adapter)
tools = UniversalTools(loader)

rows = await tools.search_files("case evidence", source="gdrive")
data = await tools.download_file("native-file-id", source="gdrive")
health = await tools.get_health_report()
```

The adapter factory is intentionally external to this module. That keeps authentication, SDK choice, account identity, and secret handling in the system that genuinely owns them.

## Local utilities

These execute without external credentials:

```python
UniversalTools.parse_data('{"status":"ok"}', "json")
UniversalTools.parse_data("a,b\n1,2\n", "csv")
UniversalTools.parse_data("<root><item>x</item></root>", "xml")
UniversalTools.merge_results([...])
```

## Verification

`tests/test_universal_tools_framework.py` proves:

- absent connectors fail closed;
- registered adapters are lazily connected and reused;
- `source="all"` searches only registered compatible connectors;
- source identities are preserved during merge/deduplication;
- unsupported operations are explicit failures;
- downloaded bytes come from the adapter rather than a framework placeholder;
- idle adapters close;
- local parse utilities execute;
- metrics reflect real calls.

The repository CI also builds and tests the TypeScript Comet browser runtime. The browser server remains the primary product surface of this repository; the Python universal layer is a reusable compatibility/orchestration module.
