/**
 * Shared types for the OpenBrick EDU BLE manager.
 * Mirrors the command/message structure in firmware/ble/protocol.py.
 */

// ── Connection state machine ──────────────────────────────────────────────────

export type BleConnectionState =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'disconnecting';

// ── Command bytes (must match firmware/ble/service.py CMD_* constants) ────────

export const CMD = {
  PROGRAM_UPLOAD: 0x01,
  PROGRAM_RUN:    0x02,
  PROGRAM_STOP:   0x03,
  SENSOR_READ:    0x10,
  MOTOR_SET:      0x20,
  HUB_STATUS:     0x30,
} as const;

export type CommandByte = typeof CMD[keyof typeof CMD];

// ── Frame structure (matches ADR-004 framed binary protocol) ──────────────────

/**
 * Decoded frame from the wire.
 *
 * Wire layout (little-endian):
 *   [0]     SOF     0xAA
 *   [1]     CMD     command byte
 *   [2–3]   LEN     payload length (uint16 LE)
 *   [4…N-3] PAYLOAD raw bytes
 *   [N-2]   CRC_HI  CRC-16 high byte
 *   [N-1]   CRC_LO  CRC-16 low byte
 */
export interface BleFrame {
  command: CommandByte;
  payload: Uint8Array;
}

// ── Event callbacks ───────────────────────────────────────────────────────────

export type OnFrameCallback       = (frame: BleFrame) => void;
export type OnStateChangeCallback = (state: BleConnectionState) => void;
export type OnErrorCallback       = (error: Error) => void;

// ── BLE GATT UUIDs (must match firmware/ble/service.py) ─────────────────────

export const BLE_SERVICE_UUID         = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
export const BLE_TX_CHARACTERISTIC    = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'; // IDE → Hub
export const BLE_RX_CHARACTERISTIC    = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'; // Hub → IDE

export const FRAME_SOF = 0xAA;
export const FRAME_OVERHEAD = 6; // SOF(1) + CMD(1) + LEN(2) + CRC(2)
