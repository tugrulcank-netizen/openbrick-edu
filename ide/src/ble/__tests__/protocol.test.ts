/**
 * Tests for BLE framed binary protocol.
 *
 * CRC-16 polynomial: 0x1021, init: 0xFFFF (CCITT variant).
 * Must produce identical results to firmware/ble/protocol.py.
 *
 * Wire frame layout (ADR-004):
 *   [0]     SOF     0xAA
 *   [1]     CMD     command byte
 *   [2–3]   LEN     payload length (uint16 LE)
 *   [4…N-3] PAYLOAD raw bytes
 *   [N-2]   CRC_HI  over bytes [1…N-3]  (CMD + LEN + PAYLOAD)
 *   [N-1]   CRC_LO
 */

import { encodeFrame, decodeFrame, crc16 } from '../protocol';
import { CMD, FRAME_SOF } from '../types';

// ── CRC-16 (CCITT) ────────────────────────────────────────────────────────────

describe('crc16', () => {
  it('returns 0xFFFF for empty input', () => {
    expect(crc16(new Uint8Array([]))).toBe(0xFFFF);
  });

  it('produces known value for single zero byte', () => {
    // CRC-16/CCITT: 0x00 → 0xE1F0
    expect(crc16(new Uint8Array([0x00]))).toBe(0xE1F0);
  });

  it('produces known value for [0x01, 0x02]', () => {
    // Pre-computed reference value (matches firmware/ble/protocol.py)
    expect(crc16(new Uint8Array([0x01, 0x02]))).toBe(0x0E7C);
  });

  it('produces known value for ASCII "123456789"', () => {
    // Standard CRC-16/CCITT-FALSE check vector = 0x29B1
    const data = new TextEncoder().encode('123456789');
    expect(crc16(data)).toBe(0x29B1);
  });

  it('is deterministic — same input always gives same output', () => {
    const data = new Uint8Array([0xAA, 0xBB, 0xCC]);
    expect(crc16(data)).toBe(crc16(data));
  });
});

// ── encodeFrame ───────────────────────────────────────────────────────────────

describe('encodeFrame', () => {
  it('produces correct SOF byte', () => {
    const frame = encodeFrame({ command: CMD.PROGRAM_RUN, payload: new Uint8Array() });
    expect(frame[0]).toBe(FRAME_SOF);
  });

  it('embeds the command byte at index 1', () => {
    const frame = encodeFrame({ command: CMD.PROGRAM_STOP, payload: new Uint8Array() });
    expect(frame[1]).toBe(CMD.PROGRAM_STOP);
  });

  it('encodes empty payload with LEN=0', () => {
    const frame = encodeFrame({ command: CMD.PROGRAM_RUN, payload: new Uint8Array() });
    // LEN is uint16 LE at bytes [2,3]
    const len = frame[2] | (frame[3] << 8);
    expect(len).toBe(0);
    expect(frame.byteLength).toBe(6); // FRAME_OVERHEAD only
  });

  it('encodes 3-byte payload with correct LEN', () => {
    const payload = new Uint8Array([0x01, 0x02, 0x03]);
    const frame = encodeFrame({ command: CMD.SENSOR_READ, payload });
    const len = frame[2] | (frame[3] << 8);
    expect(len).toBe(3);
    expect(frame.byteLength).toBe(9); // 6 overhead + 3 payload
  });

  it('copies payload bytes correctly into the frame', () => {
    const payload = new Uint8Array([0xDE, 0xAD, 0xBE, 0xEF]);
    const frame = encodeFrame({ command: CMD.MOTOR_SET, payload });
    expect(Array.from(frame.slice(4, 8))).toEqual([0xDE, 0xAD, 0xBE, 0xEF]);
  });

  it('appends CRC-16 over CMD+LEN+PAYLOAD as the last 2 bytes', () => {
    const payload = new Uint8Array([0xAB]);
    const frame = encodeFrame({ command: CMD.HUB_STATUS, payload });
    // CRC covers frame[1..N-3]: CMD(1) + LEN(2) + PAYLOAD(1) = bytes [1,2,3,4]
    const crcInput = frame.slice(1, frame.byteLength - 2);
    const expectedCrc = crc16(crcInput);
    const actualCrcHi = frame[frame.byteLength - 2];
    const actualCrcLo = frame[frame.byteLength - 1];
    expect((actualCrcHi << 8) | actualCrcLo).toBe(expectedCrc);
  });
});

// ── decodeFrame ───────────────────────────────────────────────────────────────

describe('decodeFrame', () => {
  it('round-trips an empty-payload frame', () => {
    const original = { command: CMD.PROGRAM_RUN as typeof CMD.PROGRAM_RUN, payload: new Uint8Array() };
    const wire = encodeFrame(original);
    const decoded = decodeFrame(wire);
    expect(decoded).not.toBeNull();
    expect(decoded!.command).toBe(CMD.PROGRAM_RUN);
    expect(decoded!.payload.byteLength).toBe(0);
  });

  it('round-trips a frame with payload', () => {
    const payload = new Uint8Array([0x01, 0x02, 0x03, 0x04]);
    const original = { command: CMD.MOTOR_SET as typeof CMD.MOTOR_SET, payload };
    const wire = encodeFrame(original);
    const decoded = decodeFrame(wire);
    expect(decoded).not.toBeNull();
    expect(decoded!.command).toBe(CMD.MOTOR_SET);
    expect(Array.from(decoded!.payload)).toEqual([0x01, 0x02, 0x03, 0x04]);
  });

  it('returns null if SOF byte is wrong', () => {
    const payload = new Uint8Array([0xAB]);
    const wire = encodeFrame({ command: CMD.SENSOR_READ, payload });
    wire[0] = 0xFF; // corrupt SOF
    expect(decodeFrame(wire)).toBeNull();
  });

  it('returns null if frame is too short (< 6 bytes)', () => {
    expect(decodeFrame(new Uint8Array([0xAA, 0x01, 0x00]))).toBeNull();
  });

  it('returns null if CRC does not match', () => {
    const payload = new Uint8Array([0xAB]);
    const wire = encodeFrame({ command: CMD.SENSOR_READ, payload });
    wire[wire.byteLength - 1] ^= 0xFF; // flip last CRC byte
    expect(decodeFrame(wire)).toBeNull();
  });

  it('returns null if declared LEN exceeds actual frame bytes', () => {
    const payload = new Uint8Array([0x01, 0x02]);
    const wire = encodeFrame({ command: CMD.MOTOR_SET, payload });
    // Lie about length: set LEN = 100
    wire[2] = 100;
    wire[3] = 0;
    expect(decodeFrame(wire)).toBeNull();
  });
});

// ── Cross-compatibility anchor ────────────────────────────────────────────────

describe('firmware compatibility', () => {
  it('CRC-16 of "OpenBrick" matches pre-computed firmware reference', () => {
    // Computed with firmware/ble/protocol.py crc16() on b"OpenBrick"
    // Run: python -c "from firmware.ble.protocol import crc16; print(hex(crc16(b'OpenBrick')))"
    // Expected: 0x064D
    const data = new TextEncoder().encode('OpenBrick');
    expect(crc16(data)).toBe(0x064D);
  });
});
