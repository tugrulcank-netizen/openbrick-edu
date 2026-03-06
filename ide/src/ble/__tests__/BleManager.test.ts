/**
 * Tests for BleManager — Web Bluetooth connection state machine.
 *
 * Web Bluetooth API (navigator.bluetooth) is fully mocked.
 * No real hardware or browser required.
 *
 * State machine: disconnected → connecting → connected → disconnecting → disconnected
 */

import { BleManager } from '../BleManager';
import { CMD } from '../types';
import type { BleConnectionState, BleFrame } from '../types';

// ── Web Bluetooth mock helpers ────────────────────────────────────────────────

/** Create a minimal mock GATT characteristic */
function makeMockCharacteristic(uuid: string) {
  return {
    uuid,
    writeValueWithResponse: jest.fn().mockResolvedValue(undefined),
    startNotifications: jest.fn().mockResolvedValue(undefined),
    stopNotifications: jest.fn().mockResolvedValue(undefined),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  };
}

/** Create a minimal mock GATT service */
function makeMockService(txChar: ReturnType<typeof makeMockCharacteristic>, rxChar: ReturnType<typeof makeMockCharacteristic>) {
  return {
    getCharacteristic: jest.fn().mockImplementation((uuid: string) => {
      if (uuid.includes('0002')) return Promise.resolve(txChar);
      if (uuid.includes('0003')) return Promise.resolve(rxChar);
      return Promise.reject(new Error(`Unknown UUID: ${uuid}`));
    }),
  };
}

/** Create a minimal mock BluetoothDevice */
function makeMockDevice(service: ReturnType<typeof makeMockService>) {
  const gatt = {
    connect: jest.fn().mockResolvedValue({
      getPrimaryService: jest.fn().mockResolvedValue(service),
    }),
    disconnect: jest.fn(),
    connected: true,
  };
  return {
    name: 'OpenBrick-EDU',
    gatt,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  };
}

/** Install a mock navigator.bluetooth before each test */
function installBluetoothMock(device: ReturnType<typeof makeMockDevice>) {
  Object.defineProperty(global.navigator, 'bluetooth', {
    value: {
      requestDevice: jest.fn().mockResolvedValue(device),
      getAvailability: jest.fn().mockResolvedValue(true),
    },
    writable: true,
    configurable: true,
  });
}

// ── Fixtures ──────────────────────────────────────────────────────────────────

function makeConnectedManager() {
  const txChar = makeMockCharacteristic('6e400002-b5a3-f393-e0a9-e50e24dcca9e');
  const rxChar = makeMockCharacteristic('6e400003-b5a3-f393-e0a9-e50e24dcca9e');
  const service = makeMockService(txChar, rxChar);
  const device = makeMockDevice(service);
  installBluetoothMock(device);
  return { txChar, rxChar, service, device };
}

// ── Initial state ─────────────────────────────────────────────────────────────

describe('BleManager initial state', () => {
  it('starts in disconnected state', () => {
    const mgr = new BleManager();
    expect(mgr.state).toBe('disconnected');
  });

  it('isConnected returns false initially', () => {
    const mgr = new BleManager();
    expect(mgr.isConnected).toBe(false);
  });
});

// ── connect() ─────────────────────────────────────────────────────────────────

describe('BleManager.connect()', () => {
  beforeEach(() => jest.clearAllMocks());

  it('transitions through connecting → connected', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    const states: BleConnectionState[] = [];
    mgr.onStateChange((s) => states.push(s));

    await mgr.connect();

    expect(states).toContain('connecting');
    expect(states[states.length - 1]).toBe('connected');
  });

  it('is in connected state after successful connect()', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    expect(mgr.state).toBe('connected');
    expect(mgr.isConnected).toBe(true);
  });

  it('calls navigator.bluetooth.requestDevice with the correct service UUID', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    expect(navigator.bluetooth.requestDevice).toHaveBeenCalledWith(
      expect.objectContaining({
        filters: expect.arrayContaining([
          expect.objectContaining({ services: expect.arrayContaining(['6e400001-b5a3-f393-e0a9-e50e24dcca9e']) }),
        ]),
      })
    );
  });

  it('calls startNotifications on the RX characteristic', async () => {
    const { rxChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    expect(rxChar.startNotifications).toHaveBeenCalled();
  });

  it('transitions to disconnected and throws if requestDevice rejects', async () => {
    Object.defineProperty(global.navigator, 'bluetooth', {
      value: { requestDevice: jest.fn().mockRejectedValue(new Error('User cancelled')) },
      writable: true, configurable: true,
    });
    const mgr = new BleManager();
    const states: BleConnectionState[] = [];
    mgr.onStateChange((s) => states.push(s));

    await expect(mgr.connect()).rejects.toThrow('User cancelled');
    expect(mgr.state).toBe('disconnected');
  });

  it('throws if already connected', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    await expect(mgr.connect()).rejects.toThrow();
  });
});

// ── disconnect() ──────────────────────────────────────────────────────────────

describe('BleManager.disconnect()', () => {
  beforeEach(() => jest.clearAllMocks());

  it('transitions to disconnected state', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    await mgr.disconnect();
    expect(mgr.state).toBe('disconnected');
  });

  it('calls gatt.disconnect() on the device', async () => {
    const { device } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();
    await mgr.disconnect();
    expect(device.gatt.disconnect).toHaveBeenCalled();
  });

  it('does nothing if already disconnected', async () => {
    const mgr = new BleManager();
    await expect(mgr.disconnect()).resolves.toBeUndefined();
    expect(mgr.state).toBe('disconnected');
  });
});

// ── sendFrame() ───────────────────────────────────────────────────────────────

describe('BleManager.sendFrame()', () => {
  beforeEach(() => jest.clearAllMocks());

  it('calls writeValueWithResponse on TX characteristic', async () => {
    const { txChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();

    await mgr.sendFrame({ command: CMD.PROGRAM_RUN, payload: new Uint8Array() });
    expect(txChar.writeValueWithResponse).toHaveBeenCalledTimes(1);
  });

  it('sends a correctly framed buffer (SOF = 0xAA)', async () => {
    const { txChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();

    await mgr.sendFrame({ command: CMD.PROGRAM_STOP, payload: new Uint8Array() });
    const sentBuf: ArrayBuffer = txChar.writeValueWithResponse.mock.calls[0][0];
    const view = new Uint8Array(sentBuf);
    expect(view[0]).toBe(0xAA); // SOF
    expect(view[1]).toBe(CMD.PROGRAM_STOP); // CMD
  });

  it('throws if not connected', async () => {
    const mgr = new BleManager();
    await expect(
      mgr.sendFrame({ command: CMD.PROGRAM_RUN, payload: new Uint8Array() })
    ).rejects.toThrow('Not connected');
  });
});

// ── onFrame() ─────────────────────────────────────────────────────────────────

describe('BleManager.onFrame()', () => {
  beforeEach(() => jest.clearAllMocks());

  it('fires the callback when a valid notification arrives', async () => {
    const { rxChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();

    const received: BleFrame[] = [];
    mgr.onFrame((f) => received.push(f));

    // Simulate a notification event carrying a valid CMD.HUB_STATUS frame
    // Build the raw wire bytes manually (encodeFrame logic replicated here for isolation)
    // SOF=0xAA, CMD=0x30, LEN=0x00 0x00, CRC over [0x30,0x00,0x00]
    const { encodeFrame } = await import('../protocol');
    const raw = encodeFrame({ command: CMD.HUB_STATUS, payload: new Uint8Array() });

    // Find the addEventListener call for 'characteristicvaluechanged'
    const addEventCall = rxChar.addEventListener.mock.calls.find(
      ([evt]: [string]) => evt === 'characteristicvaluechanged'
    );
    expect(addEventCall).toBeDefined();
    const handler = addEventCall![1];

    // Simulate the event
    handler({ target: { value: { buffer: raw.buffer } } });

    expect(received).toHaveLength(1);
    expect(received[0].command).toBe(CMD.HUB_STATUS);
  });

  it('silently drops malformed notifications (bad CRC)', async () => {
    const { rxChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();

    const received: BleFrame[] = [];
    mgr.onFrame((f) => received.push(f));

    // Corrupt frame: not a valid framed packet
    const corrupt = new Uint8Array([0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]);
    const addEventCall = rxChar.addEventListener.mock.calls.find(
      ([evt]: [string]) => evt === 'characteristicvaluechanged'
    );
    const handler = addEventCall![1];
    handler({ target: { value: { buffer: corrupt.buffer } } });

    expect(received).toHaveLength(0);
  });
});

// ── Event handler registration ────────────────────────────────────────────────

describe('BleManager event handlers', () => {
  it('supports multiple onStateChange listeners', async () => {
    makeConnectedManager();
    const mgr = new BleManager();
    const a: BleConnectionState[] = [];
    const b: BleConnectionState[] = [];
    mgr.onStateChange((s) => a.push(s));
    mgr.onStateChange((s) => b.push(s));
    await mgr.connect();
    expect(a.length).toBeGreaterThan(0);
    expect(b.length).toBeGreaterThan(0);
  });

  it('supports multiple onFrame listeners', async () => {
    const { rxChar } = makeConnectedManager();
    const mgr = new BleManager();
    await mgr.connect();

    const { encodeFrame } = await import('../protocol');
    const raw = encodeFrame({ command: CMD.HUB_STATUS, payload: new Uint8Array() });
    const addEventCall = rxChar.addEventListener.mock.calls.find(
      ([evt]: [string]) => evt === 'characteristicvaluechanged'
    );
    const handler = addEventCall![1];

    const a: BleFrame[] = [];
    const b: BleFrame[] = [];
    mgr.onFrame((f) => a.push(f));
    mgr.onFrame((f) => b.push(f));
    handler({ target: { value: { buffer: raw.buffer } } });

    expect(a).toHaveLength(1);
    expect(b).toHaveLength(1);
  });
});
