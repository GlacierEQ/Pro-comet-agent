# Hire surface

The historical hire exclusion applied to an older connector module that returned placeholder values while implying live external integrations.

That specific blocker is resolved by the current explicit adapter runtime: concrete connectors must be registered by a caller, unavailable connectors fail closed, unsupported operations fail explicitly, and deterministic tests exercise the orchestration boundary without pretending external access exists.

## Recruiter-visible capability boundary

The repository may demonstrate:

- fail-closed asynchronous connector-adapter orchestration;
- source-preserving result merging and lifecycle/health metrics;
- JSON, CSV, and XML local parsing;
- a TypeScript browser-provider/server architecture that compiles under repository CI;
- structured Prisma models as source artifacts.

It must not be represented as proof of live Google Drive, Dropbox, Gmail, GitHub, OneDrive, MCP, APEX, Mastermind, Browserbase, Comet/CDP, or production database connectivity unless a separate exact-head receipt proves that integration.

## Admission state

The prior implementation head `355db6c60a4f0f7a5a3a329003cc939d9cbc293c` has successful CI receipt `31643253384`. The public-truth repair changes the repository head, so recruiter admission remains `FUNCTIONAL_CANDIDATE` until the resulting canonical head receives fresh successful proof.
