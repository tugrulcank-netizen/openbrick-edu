/**
 * BLE framed binary protocol for OpenBrick EDU.
 *
 * Mirrors firmware/ble/protocol.py exactly — CRC polynomial and init value
 * MUST stay in sync with the firmware implementation.
 *
 * Wire frame layout (ADR-004):
 *   [0]     SOF     0xAA
 *   [1]     CMD     command byte
 *   [2–3]   LEN     payload length (uint16 little-endian)
 *   [4…N-3] PAYLOAD raw bytes (0 or more)
 *   [N-2]   CRC_HI  CRC-16 high byte  ┐ over bytes [1…N-3]
 *   [N-1]   CRC_LO  CRC-16 low byte   ┘ (CMD + LEN + PAYLOAD)
 */

import { FRAME_SOF, FRAME_OVERHEAD } from './types';
import type { BleFrame } from './types';

// ── CRC-16/CCITT-FALSE ────────────────────────────────────────────────────────
// Polynomial: 0x1021 | Init: 0xFFFF | No input/output reflection | No final XOR
// This is "CRC-16/CCITT-FALSE" — the same variant used in firmware/ble/protocol.py

/**
 * Compute CRC-16 (CCITT-FALSE) over `data`.
 * @param data - Bytes to checksum.
 * @returns 16-bit CRC value.
 */
export function crc16(data: Uint8Array): number {
  let crc = 0xFFFF;
  for (const byte of data) {
    crc ^= byte << 8;
    for (let i = 0; i < 8; i++) {
      if (crc & 0x8000) {
        crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
      } else {
        crc = (crc << 1) & 0xFFFF;
      }
    }
  }
  return crc;
}

// ── Frame encoding ────────────────────────────────────────────────────────────

/**
 * Encode a BleFrame into a wire-format Uint8Array.
 *
 * The CRC covers bytes [1…N-3]: CMD + LEN_HI + LEN_LO + PAYLOAD.
 * @param frame - Command and payload to encode.
 * @returns Framed bytes ready to send via BLE writeValueWithResponse.
 */
export function encodeFrame(frame: BleFrame): Uint8Array {
  const payloadLen = frame.payload.byteLength;
  const totalLen = FRAME_OVERHEAD + payloadLen;
  const buf = new Uint8Array(totalLen);

  // SOF
  buf[0] = FRAME_SOF;
  // CMD
  buf[1] = frame.command;
  // LEN (uint16 LE)
  buf[2] = payloadLen & 0xFF;
  buf[3] = (payloadLen >> 8) & 0xFF;
  // PAYLOAD
  buf.set(frame.payload, 4);

  // CRC over [CMD, LEN_LO, LEN_HI, ...PAYLOAD] = buf[1 .. N-3]
  const crcInput = buf.slice(1, totalLen - 2);
  const crc = crc16(crcInput);
  buf[totalLen - 2] = (crc >> 8) & 0xFF; // CRC_HI
  buf[totalLen - 1] =  crc       & 0xFF; // CRC_LO

  return buf;
}

// ── Frame decoding ────────────────────────────────────────────────────────────

/**
 * Decode a wire-format buffer into a BleFrame.
 *
 * Returns `null` if the buffer is malformed or the CRC does not match.
 * Callers should silently drop null results (corrupted / partial packets).
 *
 * @param buf - Raw bytes received via BLE notification.
 * @returns Decoded BleFrame, or null on error.
 */
export function decodeFrame(buf: Uint8Array): BleFrame | null {
  // Minimum frame size check
  if (buf.byteLength < FRAME_OVERHEAD) return null;

  // SOF check
  if (buf[0] !== FRAME_SOF) return null;

  // Parse LEN (uint16 LE)
  const payloadLen = buf[2] | (buf[3] << 8);
  const expectedTotal = FRAME_OVERHEAD + payloadLen;
  if (buf.byteLength < expectedTotal) return null;

  // CRC verification
  const crcInput = buf.slice(1, expectedTotal - 2);
  const expectedCrc = crc16(crcInput);
  const receivedCrc = (buf[expectedTotal - 2] << 8) | buf[expectedTotal - 1];
  if (expectedCrc !== receivedCrc) return null;

  // Extract payload
  const payload = buf.slice(4, 4 + payloadLen);

  return {
    command: buf[1] as BleFrame['command'],
    payload,
  };
}
