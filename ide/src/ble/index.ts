/**
 * Public API for the OpenBrick EDU BLE module.
 */

export { BleManager } from './BleManager';
export { encodeFrame, decodeFrame, crc16 } from './protocol';
export {
  CMD,
  BLE_SERVICE_UUID,
  BLE_TX_CHARACTERISTIC,
  BLE_RX_CHARACTERISTIC,
  FRAME_SOF,
  FRAME_OVERHEAD,
} from './types';
export type {
  BleConnectionState,
  BleFrame,
  CommandByte,
  OnFrameCallback,
  OnStateChangeCallback,
  OnErrorCallback,
} from './types';
