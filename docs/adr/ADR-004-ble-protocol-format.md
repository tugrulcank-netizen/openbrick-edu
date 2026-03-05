# ADR-004: BLE Framed Binary Protocol Format

| Field  | Value |
|--------|-------|
| **ID** | ADR-004 |
| **Date** | 2026-03 |
| **Status** | Accepted |
| **Origin** | AI-Suggested & Human-Approved |

## Context

The BLE GATT characteristics defined in ADR-003 carry payloads between the
Web IDE and the hub firmware. A wire format must be specified for:

- **Program upload** (IDE → hub): MicroPython bytecode, potentially up to
  10KB, must be chunked (BLE MTU is typically 20–512 bytes).
- **Run/Stop commands** (IDE → hub): Short control messages.
- **Sensor telemetry** (hub → IDE): Continuous stream of sensor readings.
- **Hub status** (hub → IDE): Battery level, error codes, connection state.

Requirements:
- Must fit within BLE MTU (minimum 20 bytes; negotiated up to 512 bytes with
  Data Length Extension).
- Must be detectable as corrupt (a classroom environment with BLE interference
  means data integrity matters).
- Must be parseable by both MicroPython (firmware) and TypeScript (IDE) without
  external libraries.
- Must be compact — sensor telemetry runs at up to 50Hz across 6 ports.

## Decision

Use a **lightweight framed binary protocol** with the following frame structure:

```
┌────────┬────────┬──────────┬─────────────────┬─────────┐
│ START  │  TYPE  │  LENGTH  │    PAYLOAD       │  CRC16  │
│ 1 byte │ 1 byte │ 2 bytes  │  0–500 bytes     │ 2 bytes │
└────────┴────────┴──────────┴─────────────────┴─────────┘
```

| Field | Value | Notes |
|-------|-------|-------|
| START | `0xAA` | Frame delimiter |
| TYPE | See table below | Message type byte |
| LENGTH | uint16 little-endian | Payload length in bytes |
| PAYLOAD | Varies by TYPE | See payload definitions |
| CRC16 | CRC-16/CCITT-FALSE | Covers TYPE + LENGTH + PAYLOAD |

### Message Types

| Type Byte | Name | Direction | Payload |
|-----------|------|-----------|---------|
| `0x01` | PROGRAM_CHUNK | IDE → Hub | `chunk_index (2B) + total_chunks (2B) + data (N bytes)` |
| `0x02` | PROGRAM_DONE | IDE → Hub | `total_size (4B)` — signals upload complete |
| `0x03` | CMD_RUN | IDE → Hub | `program_slot (1B)` |
| `0x04` | CMD_STOP | IDE → Hub | Empty payload |
| `0x05` | CMD_RESET | IDE → Hub | Empty payload |
| `0x10` | TELEMETRY | Hub → IDE | `port (1B) + sensor_type (1B) + values (N×4B floats)` |
| `0x11` | HUB_STATUS | Hub → IDE | `battery_pct (1B) + state (1B) + error_code (2B)` |
| `0x12` | ACK | Hub → IDE | `ack_type (1B) + status (1B)` |

Full payload field definitions: `@docs/ble-spec.md`.

### Chunked Upload Flow

```
IDE: PROGRAM_CHUNK [0 of N]  →  Hub: ACK (ok)
IDE: PROGRAM_CHUNK [1 of N]  →  Hub: ACK (ok)
...
IDE: PROGRAM_DONE            →  Hub: ACK (ok / checksum_fail)
```

On checksum failure, the IDE retransmits from the failed chunk index.

## Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| JSON over BLE | Human-readable but 3–5× larger than binary; 50Hz telemetry at 6 ports would saturate BLE bandwidth |
| Protocol Buffers | Requires protobuf library on MicroPython — adds ~40KB flash; no pre-built MicroPython package available |
| MessagePack | Better than JSON but still requires a library on both ends; binary framing adds same complexity without the simplicity of a custom protocol |
| Nordic UART Service (raw) | No framing, no integrity check — any BLE interference causes silent data corruption |
| ASCII line protocol (`SENSOR:ax=0.5\n`) | Easy to read but 10× larger than binary for telemetry; fails BLE bandwidth constraints at 50Hz |

## Consequences

- **Positive:** CRC-16 catches single-burst corruption events common in classroom BLE environments.
- **Positive:** Fixed frame header (`0xAA`) allows resync after a dropped packet.
- **Positive:** Implementable in pure MicroPython and TypeScript without external libraries.
- **Positive:** Chunk index in PROGRAM_CHUNK allows selective retransmission rather than full re-upload.
- **Negative:** Binary protocol is harder to debug than text — use nRF Connect's hex view or a custom BLE sniffer script during development.
- **Neutral:** CRC-16/CCITT-FALSE was chosen (not CRC-32) to keep the checksum field at 2 bytes. At max payload size (500 bytes) the collision probability is acceptable for this use case.

## Implementation Notes

- Firmware: `firmware/ble/protocol.py` — encoder/decoder + CRC implementation.
- IDE: `ide/src/ble/protocol.ts` — encoder/decoder + CRC implementation.
- Both implementations must share the same CRC polynomial (`0x1021`, init `0xFFFF`).
- Unit tests must verify encode→decode round-trip for each message type.
- See ADR-003 for the GATT characteristic assignments that carry these frames.
