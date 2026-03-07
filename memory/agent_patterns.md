# Architectural Patterns & Technical Decisions

## 1. Async Firestore Integration (Python)

- **Pattern**: `run_in_executor`
- **Context**: The `firebase-admin` Python SDK only offers a synchronous Firestore client. Running synchronous I/O operations directly in FastAPI endpoints blocks the ASGI event loop, causing severe latency degradation under concurrency.
- **Implementation**:
  ```python
  loop = asyncio.get_event_loop()
  await loop.run_in_executor(None, sync_write_fn)
  ```
- **Executor Type**: Passing `None` to `run_in_executor` defaults to `concurrent.futures.ThreadPoolExecutor`, which is the correct choice for I/O bound tasks like network calls to Firestore (unlike `ProcessPoolExecutor` which is for CPU bound tasks).

## 2. Two-Tier Pytest Suite

- **Pattern**: Segmented Mock vs. Emulator Testing
- **Context**: Relying exclusively on mocks for database integration hides serialization bugs. Relying exclusively on an emulator makes CI/CD slow and brittle.
- **Implementation**:
  - `test_api.py`: Mocks the `services.log_writer` layer entirely. Tests API routing, payload validation (via Pydantic), and HTTP response structuring. Extremely fast.
  - `test_writer.py`: Executes against the local Firestore emulator (configured via `FIRESTORE_EMULATOR_HOST=localhost:8081`). Verifies that Pydantic models serialize correctly, batched atomic writes succeed, and role-based security filters don't interfere with Admin SDK writes.

## 3. Pydantic Event Registry Validation

- **Pattern**: Centralized Event Registry Enforcement
- **Context**: Logs quickly become chaotic if event types aren't strictly validated.
- **Implementation**:
  - `VALID_EVENT_TYPES` defined as the union of technical, methodological, and AI decision event sets.
  - `@field_validator("event_type")` enforces that any incoming REST payload matches the registered taxonomy, preventing drift.

## 4. Role-Based Firestore Rules (RBAC)

- **Pattern**: Role lookup via document references
- **Context**: We mapped the application's actual Firestore security pattern via `get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ["admin", "researcher"]` rather than relying on custom auth claims (`accessLevel`), which didn't exist in the project scope.

## 5. Security Isolation

- **Pattern**: Admin SDK Writer / Client Reader
- **Context**: The logging infrastructure prevents tampering by restricting direct client writes entirely via rules (`allow write: if false`), relying solely on the Cloud Run logging API (using the Admin SDK) to ingest data asynchronously.
