# Skill: BLE Protocol

Load this skill when working on the firmware BLE stack or the IDE BLE manager.

---

## BLE GATT Service Definitions

### Service UUIDs

All custom services use the OpenBrick EDU base UUID: `0000XXXX-0000-1000-8000-00805F9B34FB` where `XXXX` is the short UUID listed below. Standard services use Bluetooth SIG-assigned UUIDs.

| Service             | Short UUID | Type     | Purpose                                |
|--------------------|-----------|----------|----------------------------------------|
| Device Information | 0x180A    | Standard | Firmware version, HW rev, serial number|
| Program Transfer   | 0xFE01   | Custom   | Upload/download user programs          |
| Program Control    | 0xFE02   | Custom   | Run, stop, list, select program slot   |
| Sensor Telemetry   | 0xFE03   | Custom   | Stream sensor readings to IDE          |
| Motor Command      | 0xFE04   | Custom   | Send motor control commands            |
| Hub Status         | 0xFE05   | Custom   | Battery, temperature, error state      |

### Characteristics

#### Device Information Service (0x180A)

| Characteristic        | UUID   | Properties | Format       |
|----------------------|--------|-----------|--------------|
| Firmware Revision    | 0x2A26 | Read      | UTF-8 string |
| Hardware Revision    | 0x2A27 | Read      | UTF-8 string |
| Serial Number        | 0x2A25 | Read      | UTF-8 string |
| Manufacturer Name    | 0x2A29 | Read      | "OpenBrick"  |

#### Program Transfer Service (0xFE01)

| Characteristic   | UUID   | Properties     | Description                     |
|-----------------|--------|---------------|---------------------------------|
| Program Data    | 0x0101 | Write No Resp  | Chunked binary upload frames    |
| Transfer Status | 0x0102 | Notify         | ACK/NACK per frame; completion  |
| Program Read    | 0x0103 | Read + Notify  | Download program from slot      |

#### Program Control Service (0xFE02)

| Characteristic   | UUID   | Properties     | Description                     |
|-----------------|--------|---------------|---------------------------------|
| Command         | 0x0201 | Write          | Run, stop, list, select slot    |
| Status          | 0x0202 | Notify         | Running/stopped/error + output  |
| Console Output  | 0x0203 | Notify         | Print() output from user program|

#### Sensor Telemetry Service (0xFE03)

| Characteristic   | UUID   | Properties     | Description                     |
|-----------------|--------|---------------|---------------------------------|
| Port Config     | 0x0301 | Write          | Set active ports and sample rate|
| Telemetry Stream| 0x0302 | Notify         | Packed sensor readings          |
| Sensor Info     | 0x0303 | Read           | Detected sensor types per port  |

#### Motor Command Service (0xFE04)

| Characteristic   | UUID   | Properties     | Description                     |
|-----------------|--------|---------------|---------------------------------|
| Motor Command   | 0x0401 | Write          | Speed, position, stop per port  |
| Motor Status    | 0x0402 | Notify         | Current angle, speed, stall flag|

#### Hub Status Service (0xFE05)

| Characteristic   | UUID   | Properties     | Description                     |
|-----------------|--------|---------------|---------------------------------|
| Battery Level   | 0x2A19 | Read + Notify  | 0–100% (standard BLE battery)  |
| Hub Info        | 0x0501 | Read + Notify  | Temperature, uptime, error codes|

---

## Framed Binary Protocol

All data transfer over BLE uses a framed binary protocol. Frames have a maximum size of 256 bytes to fit within BLE MTU constraints.

### Frame Format

```
┌──────┬──────┬────────┬──────────┬──────────┬─────────┐
│ SOF  │ Type │ Seq #  │ Length   │ Payload  │ CRC-16  │
│ 1B   │ 1B   │ 1B     │ 2B (LE)  │ 0–249B   │ 2B (LE) │
└──────┴──────┴────────┴──────────┴──────────┴─────────┘
```

| Field    | Size    | Description                                              |
|---------|---------|----------------------------------------------------------|
| SOF     | 1 byte  | Start of frame marker: `0xAA`                            |
| Type    | 1 byte  | Frame type (see table below)                             |
| Seq #   | 1 byte  | Sequence number (0–255, wrapping); for ACK matching      |
| Length  | 2 bytes | Payload length, little-endian; 0–249                     |
| Payload | 0–249 B | Type-specific data                                       |
| CRC-16  | 2 bytes | CRC-16/CCITT over [Type + Seq + Length + Payload], LE    |

### Frame Types

| Type  | Name              | Direction     | Description                           |
|------|-------------------|---------------|---------------------------------------|
| 0x01 | PROGRAM_CHUNK     | IDE → Hub     | One chunk of a program upload         |
| 0x02 | PROGRAM_COMPLETE  | IDE → Hub     | Upload complete; include total CRC    |
| 0x03 | ACK               | Hub → IDE     | Acknowledge received frame (by Seq #) |
| 0x04 | NACK              | Hub → IDE     | Request retransmission (by Seq #)     |
| 0x05 | CMD_RUN           | IDE → Hub     | Run program in slot N                 |
| 0x06 | CMD_STOP          | IDE → Hub     | Stop running program                  |
| 0x07 | CMD_LIST          | IDE → Hub     | Request list of stored programs       |
| 0x08 | STATUS            | Hub → IDE     | Hub status update                     |
| 0x09 | SENSOR_DATA       | Hub → IDE     | Packed sensor telemetry               |
| 0x0A | MOTOR_CMD         | IDE → Hub     | Motor control command                 |
| 0x0B | CONSOLE           | Hub → IDE     | Print output from user program        |
| 0x0C | ERROR             | Hub → IDE     | Error report                          |

### CRC-16 Calculation

CRC-16/CCITT (polynomial 0x1021, initial value 0xFFFF). Calculate over bytes [Type, Seq, Length_LO, Length_HI, Payload...].

**Python (firmware):**
```python
def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc
```

**TypeScript (IDE):**
```typescript
function crc16Ccitt(data: Uint8Array): number {
  let crc = 0xFFFF;
  for (const byte of data) {
    crc ^= byte << 8;
    for (let i = 0; i < 8; i++) {
      crc = crc & 0x8000 ? (crc << 1) ^ 0x1021 : crc << 1;
      crc &= 0xFFFF;
    }
  }
  return crc;
}
```

---

## Program Upload Protocol

### Chunked Upload Flow

```
IDE                                    Hub
 │                                      │
 │── PROGRAM_CHUNK (seq=0, chunk 0) ──>│
 │<── ACK (seq=0) ─────────────────────│
 │                                      │
 │── PROGRAM_CHUNK (seq=1, chunk 1) ──>│
 │<── ACK (seq=1) ─────────────────────│
 │                                      │
 │── ... (repeat for all chunks) ──────│
 │                                      │
 │── PROGRAM_COMPLETE (total CRC) ────>│
 │<── ACK (with status: OK/FAIL) ──────│
```

### PROGRAM_CHUNK Payload

```
┌──────────┬──────────┬──────────────┐
│ Slot #   │ Offset   │ Data         │
│ 1 byte   │ 4B (LE)  │ up to 244B   │
└──────────┴──────────┴──────────────┘
```

- **Slot #:** Target program slot (0–19)
- **Offset:** Byte offset within the program (for reassembly)
- **Data:** Up to 244 bytes of program data per chunk (249 - 5 header bytes)

### PROGRAM_COMPLETE Payload

```
┌──────────┬────────────┬──────────────┐
│ Slot #   │ Total Size │ Total CRC-16 │
│ 1 byte   │ 4B (LE)    │ 2B (LE)      │
└──────────┴────────────┴──────────────┘
```

Hub verifies total CRC matches reassembled program. If mismatch, responds with NACK and error code.

### Retry Logic

- IDE waits up to 500ms for ACK after each chunk
- On timeout or NACK: retransmit the same frame (same Seq #), up to 3 retries
- After 3 failed retries: abort upload, surface error to user
- Hub discards duplicate frames (same Seq # as already ACK'd)

### Upload Speed Budget

- BLE MTU: 247 bytes (negotiated, may be lower)
- Effective payload per frame: ~244 bytes
- Typical 10KB program: ~41 frames
- At 20ms BLE interval + 10ms processing: ~1.2 seconds theoretical minimum
- Target: < 5 seconds including retries and overhead (NFR-P05)

---

## Sensor Telemetry Protocol

### Telemetry Stream Format (SENSOR_DATA frame payload)

```
┌──────────┬───────────────────────────────────────────┐
│ Port Mask│ Per-Port Sensor Data (variable length)     │
│ 1 byte   │ [Port0Data][Port1Data]...[Port5Data]       │
└──────────┴───────────────────────────────────────────┘
```

**Port Mask:** Bitmask of active ports (bit 0 = port 0, bit 5 = port 5). Only active ports include data.

**Per-Port Sensor Data:**
```
┌───────────┬──────────┬──────────────┐
│ Sensor Type│ Data Len │ Sensor Values│
│ 1 byte     │ 1 byte   │ N bytes      │
└───────────┴──────────┴──────────────┘
```

### Sensor Type Codes and Data Formats

| Type Code | Sensor   | Data Format                          | Size   |
|----------|----------|--------------------------------------|--------|
| 0x01     | IMU      | gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z (int16 LE each) | 12B |
| 0x02     | Color    | r, g, b, c (uint16 LE each)          | 8B     |
| 0x03     | Distance | distance_mm (uint16 LE)              | 2B     |
| 0x04     | Force    | force_grams (int32 LE)               | 4B     |
| 0x05     | Motor    | angle_degrees (int32 LE), speed_dps (int16 LE) | 6B |
| 0x00     | None     | (empty — port has no sensor)         | 0B     |

### Telemetry Rate

- Default: 20 Hz (50ms interval) for all active ports
- Configurable via Port Config characteristic: 10, 20, 50, or 100 Hz
- At 100 Hz with 6 ports: frame size ≈ 1 + (6 × ~10) ≈ 61 bytes — fits in one BLE frame

---

## Connection State Machine (IDE Side)

```
                    ┌─────────────┐
         ┌────────>│ DISCONNECTED │<──────────────────┐
         │         └──────┬──────┘                    │
         │                │ user clicks "Connect"     │
         │                v                           │
         │         ┌─────────────┐                    │
         │    ┌───>│  SCANNING   │───timeout(10s)─────┤
         │    │    └──────┬──────┘                    │
         │    │           │ device found              │
         │    │           v                           │
         │    │    ┌─────────────┐                    │
         │    │    │ CONNECTING  │───timeout(10s)─────┤
         │    │    └──────┬──────┘                    │
         │    │           │ GATT connected            │
         │    │           v                           │
         │    │    ┌─────────────┐                    │
         │    │    │  CONNECTED  │◄──────┐            │
         │    │    └──┬─────┬───┘       │            │
         │    │       │     │           │            │
         │    │  upload│    │ run       │ done/error │
         │    │       v     v           │            │
         │    │  ┌─────┐ ┌─────────┐   │            │
         │    │  │UPLOD│ │ RUNNING │───┘            │
         │    │  └──┬──┘ └─────────┘                │
         │    │     │ complete                       │
         │    │     └──> back to CONNECTED           │
         │    │                                      │
         │    └──── auto-reconnect (3 attempts)──────┘
         │
         └───── user clicks "Disconnect" OR max retries
```

### Auto-Reconnect Strategy

1. On unexpected disconnect: wait 1 second, attempt reconnect
2. If fail: wait 2 seconds, attempt reconnect
3. If fail: wait 4 seconds, attempt reconnect
4. If fail: transition to DISCONNECTED, show user message
5. Never auto-reconnect if user explicitly disconnected

### Known Browser Quirks

| Browser       | Issue                                           | Workaround                              |
|--------------|------------------------------------------------|-----------------------------------------|
| Chrome (all) | `requestDevice()` requires user gesture         | Always call from a click handler         |
| Chrome Android| BLE MTU negotiation may fail silently          | Default to 20-byte frames; negotiate up  |
| Edge          | Same Chromium BLE stack — same behavior as Chrome | No special handling needed             |
| Firefox       | No Web Bluetooth support natively              | Show "use Chrome/Edge" message; document adapter option |
| Safari (macOS)| Web Bluetooth behind flag, unstable            | Not officially supported; document status |
| Chrome (Linux)| May need `chrome://flags/#enable-web-bluetooth`| Document in setup guide                  |

---

## Error Codes

| Code  | Name                | Description                                  | IDE Display Message                    |
|------|---------------------|----------------------------------------------|----------------------------------------|
| 0x01 | CRC_MISMATCH       | Frame CRC check failed                       | "Communication error. Please retry."   |
| 0x02 | SLOT_FULL          | Target program slot has no space              | "Program slot is full. Choose another."|
| 0x03 | UPLOAD_TIMEOUT     | Hub didn't receive next chunk in time         | "Upload timed out. Check connection."  |
| 0x04 | PROGRAM_TOO_LARGE  | Program exceeds 100KB slot limit              | "Program is too large (max 100KB)."    |
| 0x05 | INVALID_SLOT       | Slot number out of range (0–19)               | "Invalid program slot."                |
| 0x06 | EXECUTION_ERROR    | Runtime error in user MicroPython program     | Show error text from CONSOLE frames    |
| 0x07 | WATCHDOG_TIMEOUT   | User program exceeded execution time limit    | "Program took too long and was stopped."|
| 0x08 | SENSOR_INIT_FAIL   | Sensor failed to initialize on port           | "Sensor on port N not responding."     |
| 0x09 | MOTOR_STALL        | Motor stall detected (overcurrent)            | "Motor on port N is stalled."          |
| 0x0A | LOW_BATTERY        | Battery below 10%                             | "Low battery. Please charge the hub."  |

**Rule:** ALL error messages shown to users must be human-readable (NFR-U03). Never display raw error codes, hex values, or stack traces in the IDE UI.
