# ADR-003: BLE GATT Service UUID Scheme

| Field  | Value |
|--------|-------|
| **ID** | ADR-003 |
| **Date** | 2026-03 |
| **Status** | Accepted |
| **Origin** | AI-Suggested & Human-Approved |

## Context

The OpenBrick EDU hub communicates with the Web IDE over BLE using GATT
services and characteristics. A UUID scheme must be chosen before implementing
the BLE stack (Phase 1, Day 4). The scheme must:

- Be stable (UUIDs must not change between firmware versions — they are
  hardcoded in the Web IDE's BLE manager)
- Be distinguishable from other BLE devices (avoid collisions in classroom)
- Work with the Web Bluetooth API (Chrome/Edge require full 128-bit UUIDs
  for custom services)
- Be human-readable enough for debugging with nRF Connect or similar tools

## Decision

Use a **custom 128-bit UUID base** derived from a fixed namespace, with
16-bit service/characteristic codes embedded at bytes 12–13.

**Base UUID:** `4f70656e-4272-6963-6b00-000000000000`
(encodes "OpenBrick" in ASCII at the first 9 bytes)

| Name | UUID | Description |
|------|------|-------------|
| Hub Service | `4f70656e-4272-6963-6b00-000000000001` | Root GATT service |
| Program Upload | `4f70656e-4272-6963-6b00-000000000002` | Write: chunked binary upload |
| Run/Stop Control | `4f70656e-4272-6963-6b00-000000000003` | Write: run / stop / reset commands |
| Sensor Telemetry | `4f70656e-4272-6963-6b00-000000000004` | Notify: streaming sensor values |
| Hub Status | `4f70656e-4272-6963-6b00-000000000005` | Notify: battery, errors, state |

Full UUID table: `@docs/ble-spec.md` (to be created in Phase 1, Day 4).

## Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Bluetooth SIG 16-bit UUIDs | Reserved for official profiles; using them for custom services is non-compliant |
| Random UUID (UUID v4) | Not human-readable; harder to debug; same stability benefit without the readability |
| Nordic UART Service (NUS) | Generic; no service discovery semantics; would need all multiplexing done at app layer |
| Single characteristic (all traffic) | Loses GATT semantic structure; harder to use Web Bluetooth `getCharacteristic` filtering |

## Consequences

- **Positive:** "OpenBrick" prefix is visible in Bluetooth scanners — makes debugging easier in classrooms with many BLE devices.
- **Positive:** Each characteristic has a clear semantic role — Web IDE can discover and bind by UUID without ambiguity.
- **Positive:** UUID space is extensible: bytes 14–15 are reserved for future service expansion.
- **Negative:** Full 128-bit UUIDs increase the BLE advertisement packet size slightly vs 16-bit UUIDs.
- **Neutral:** These UUIDs must be constants in both `firmware/ble/services.py` and `ide/src/ble/uuids.ts` — kept in sync manually. A shared spec doc (`docs/ble-spec.md`) is the source of truth.

## Implementation Notes

- Firmware: define as constants in `firmware/ble/services.py`.
- IDE: define as constants in `ide/src/ble/uuids.ts`.
- BLE advertisement should include the Hub Service UUID so the IDE can filter
  OpenBrick devices during scan.
- See ADR-004 for the binary protocol format carried over these characteristics.
