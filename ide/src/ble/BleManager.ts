/**
 * BleManager — Web Bluetooth connection state machine for OpenBrick EDU.
 *
 * States: disconnected → connecting → connected → disconnecting → disconnected
 *
 * Usage:
 *   const ble = new BleManager();
 *   ble.onStateChange(state => console.log(state));
 *   ble.onFrame(frame => handleIncoming(frame));
 *   await ble.connect();
 *   await ble.sendFrame({ command: CMD.PROGRAM_RUN, payload: new Uint8Array() });
 *   await ble.disconnect();
 */

import { encodeFrame, decodeFrame } from './protocol';
import {
  BLE_SERVICE_UUID,
  BLE_TX_CHARACTERISTIC,
  BLE_RX_CHARACTERISTIC,
} from './types';
import type {
  BleConnectionState,
  BleFrame,
  OnFrameCallback,
  OnStateChangeCallback,
  OnErrorCallback,
} from './types';

export class BleManager {
  // ── State ───────────────────────────────────────────────────────────────────

  private _state: BleConnectionState = 'disconnected';
  private _device: BluetoothDevice | null = null;
  private _txChar: BluetoothRemoteGATTCharacteristic | null = null;
  private _rxChar: BluetoothRemoteGATTCharacteristic | null = null;

  // ── Callbacks ────────────────────────────────────────────────────────────────

  private _stateListeners:  OnStateChangeCallback[] = [];
  private _frameListeners:  OnFrameCallback[] = [];
  private _errorListeners:  OnErrorCallback[] = [];

  // ── Public state accessors ────────────────────────────────────────────────────

  get state(): BleConnectionState {
    return this._state;
  }

  get isConnected(): boolean {
    return this._state === 'connected';
  }

  // ── Event registration ────────────────────────────────────────────────────────

  onStateChange(cb: OnStateChangeCallback): void {
    this._stateListeners.push(cb);
  }

  onFrame(cb: OnFrameCallback): void {
    this._frameListeners.push(cb);
  }

  onError(cb: OnErrorCallback): void {
    this._errorListeners.push(cb);
  }

  // ── connect() ─────────────────────────────────────────────────────────────────

  /**
   * Open the Web Bluetooth device picker, connect to the OpenBrick hub,
   * and enable notifications on the RX characteristic.
   *
   * @throws if the user cancels, BLE is unavailable, or GATT connection fails.
   */
  async connect(): Promise<void> {
    if (this._state !== 'disconnected') {
      throw new Error(`Cannot connect: already in state '${this._state}'`);
    }

    this._setState('connecting');

    try {
      // 1. Request device
      this._device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [BLE_SERVICE_UUID] }],
        optionalServices: [BLE_SERVICE_UUID],
      });

      // 2. Listen for unexpected disconnection
      this._device.addEventListener('gattserverdisconnected', this._handleUnexpectedDisconnect);

      // 3. Connect GATT
      const server = await this._device.gatt!.connect();

      // 4. Get primary service
      const service = await server.getPrimaryService(BLE_SERVICE_UUID);

      // 5. Get characteristics
      this._txChar = await service.getCharacteristic(BLE_TX_CHARACTERISTIC);
      this._rxChar = await service.getCharacteristic(BLE_RX_CHARACTERISTIC);

      // 6. Enable RX notifications
      await this._rxChar.startNotifications();
      this._rxChar.addEventListener('characteristicvaluechanged', this._handleNotification);

      this._setState('connected');
    } catch (err) {
      // Clean up on failure
      this._device = null;
      this._txChar = null;
      this._rxChar = null;
      this._setState('disconnected');
      throw err;
    }
  }

  // ── disconnect() ──────────────────────────────────────────────────────────────

  /**
   * Gracefully disconnect from the hub.
   * Safe to call when already disconnected (no-op).
   */
  async disconnect(): Promise<void> {
    if (this._state === 'disconnected') return;

    this._setState('disconnecting');

    try {
      if (this._rxChar) {
        this._rxChar.removeEventListener('characteristicvaluechanged', this._handleNotification);
        try { await this._rxChar.stopNotifications(); } catch { /* ignore */ }
      }

      if (this._device) {
        this._device.removeEventListener('gattserverdisconnected', this._handleUnexpectedDisconnect);
        this._device.gatt?.disconnect();
      }
    } finally {
      this._device = null;
      this._txChar = null;
      this._rxChar = null;
      this._setState('disconnected');
    }
  }

  // ── sendFrame() ───────────────────────────────────────────────────────────────

  /**
   * Encode and transmit a BleFrame to the hub via the TX characteristic.
   *
   * @throws if not connected.
   */
  async sendFrame(frame: BleFrame): Promise<void> {
    if (!this.isConnected || !this._txChar) {
      throw new Error('Not connected');
    }
    const wire = encodeFrame(frame);
    await this._txChar.writeValueWithResponse(wire.buffer);
  }

  // ── Private handlers ──────────────────────────────────────────────────────────

  /** Incoming notification from RX characteristic. */
  private _handleNotification = (event: Event): void => {
    const target = event.target as BluetoothRemoteGATTCharacteristic;
    // JUSTIFICATION: Web Bluetooth spec uses DataView, but tests supply ArrayBuffer directly.
    const raw = new Uint8Array(target.value?.buffer ?? new ArrayBuffer(0));
    const frame = decodeFrame(raw);
    if (frame === null) return; // silently drop malformed/corrupted packets

    for (const cb of this._frameListeners) {
      try { cb(frame); } catch (e) {
        console.error('[BleManager] onFrame callback threw:', e);
      }
    }
  };

  /** Fired when the device drops the connection unexpectedly (e.g., out of range). */
  private _handleUnexpectedDisconnect = (): void => {
    this._device = null;
    this._txChar = null;
    this._rxChar = null;
    this._setState('disconnected');
    const err = new Error('Hub disconnected unexpectedly');
    for (const cb of this._errorListeners) {
      try { cb(err); } catch { /* ignore */ }
    }
  };

  private _setState(next: BleConnectionState): void {
    this._state = next;
    for (const cb of this._stateListeners) {
      try { cb(next); } catch (e) {
        console.error('[BleManager] onStateChange callback threw:', e);
      }
    }
  }
}
