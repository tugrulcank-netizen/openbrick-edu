"""
Tests for BLE GATT service definitions and framed binary protocol.

Two modules under test:
  firmware/ble/service.py   — UUID constants and service descriptor
  firmware/ble/protocol.py  — frame encoder/decoder + CRC-16

Spec source: ADR-003 (UUID scheme) and ADR-004 (protocol format).

Frame structure (ADR-004):
  [0xAA] [TYPE 1B] [LENGTH 2B LE] [PAYLOAD N bytes] [CRC16 2B]

CRC-16/CCITT-FALSE: polynomial 0x1021, init 0xFFFF.
CRC covers TYPE + LENGTH + PAYLOAD (not the START byte).

Message types:
  0x01  PROGRAM_CHUNK   chunk_index(2) + total_chunks(2) + data(N)
  0x02  PROGRAM_DONE    total_size(4)
  0x03  CMD_RUN         program_slot(1)
  0x04  CMD_STOP        empty
  0x05  CMD_RESET       empty
  0x10  TELEMETRY       port(1) + sensor_type(1) + values(N×4 floats)
  0x11  HUB_STATUS      battery_pct(1) + state(1) + error_code(2)
  0x12  ACK             ack_type(1) + status(1)
"""

import sys
import os
import struct
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _crc16(data: bytes) -> int:
    """CRC-16/CCITT-FALSE: poly=0x1021, init=0xFFFF."""
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


def _build_raw_frame(msg_type: int, payload: bytes) -> bytes:
    """Build a valid frame manually for decoder tests."""
    length = len(payload)
    crc_data = bytes([msg_type]) + struct.pack("<H", length) + payload
    crc = _crc16(crc_data)
    return bytes([0xAA, msg_type]) + struct.pack("<H", length) + payload + struct.pack("<H", crc)


# ---------------------------------------------------------------------------
# 1. Service UUIDs (ADR-003)
# ---------------------------------------------------------------------------

class TestBLEServiceUUIDs:
    def test_hub_service_uuid_defined(self):
        from ble.service import HUB_SERVICE_UUID
        assert HUB_SERVICE_UUID is not None

    def test_program_upload_uuid_defined(self):
        from ble.service import PROGRAM_UPLOAD_UUID
        assert PROGRAM_UPLOAD_UUID is not None

    def test_run_stop_uuid_defined(self):
        from ble.service import RUN_STOP_UUID
        assert RUN_STOP_UUID is not None

    def test_telemetry_uuid_defined(self):
        from ble.service import TELEMETRY_UUID
        assert TELEMETRY_UUID is not None

    def test_hub_status_uuid_defined(self):
        from ble.service import HUB_STATUS_UUID
        assert HUB_STATUS_UUID is not None

    def test_uuids_are_unique(self):
        from ble.service import (
            HUB_SERVICE_UUID, PROGRAM_UPLOAD_UUID,
            RUN_STOP_UUID, TELEMETRY_UUID, HUB_STATUS_UUID,
        )
        uuids = [HUB_SERVICE_UUID, PROGRAM_UPLOAD_UUID,
                 RUN_STOP_UUID, TELEMETRY_UUID, HUB_STATUS_UUID]
        assert len(set(uuids)) == 5

    def test_uuids_contain_openbrick_prefix(self):
        """All UUIDs must start with the OpenBrick base: 4f70656e-4272-6963-6b00."""
        from ble.service import (
            HUB_SERVICE_UUID, PROGRAM_UPLOAD_UUID,
            RUN_STOP_UUID, TELEMETRY_UUID, HUB_STATUS_UUID,
        )
        prefix = "4f70656e-4272-6963-6b00"
        for uuid in [HUB_SERVICE_UUID, PROGRAM_UPLOAD_UUID,
                     RUN_STOP_UUID, TELEMETRY_UUID, HUB_STATUS_UUID]:
            assert uuid.startswith(prefix), f"{uuid} missing OpenBrick prefix"

    def test_message_type_constants_defined(self):
        from ble.service import (
            MSG_PROGRAM_CHUNK, MSG_PROGRAM_DONE,
            MSG_CMD_RUN, MSG_CMD_STOP, MSG_CMD_RESET,
            MSG_TELEMETRY, MSG_HUB_STATUS, MSG_ACK,
        )
        assert MSG_PROGRAM_CHUNK == 0x01
        assert MSG_PROGRAM_DONE  == 0x02
        assert MSG_CMD_RUN       == 0x03
        assert MSG_CMD_STOP      == 0x04
        assert MSG_CMD_RESET     == 0x05
        assert MSG_TELEMETRY     == 0x10
        assert MSG_HUB_STATUS    == 0x11
        assert MSG_ACK           == 0x12


# ---------------------------------------------------------------------------
# 2. CRC-16 implementation
# ---------------------------------------------------------------------------

class TestCRC16:
    def test_empty_payload_known_value(self):
        """CRC-16/CCITT-FALSE of empty bytes = 0xFFFF (init value)."""
        from ble.protocol import crc16
        assert crc16(b"") == 0xFFFF

    def test_known_value_123456789(self):
        """Standard CRC-16/CCITT-FALSE test vector: '123456789' → 0x29B1."""
        from ble.protocol import crc16
        assert crc16(b"123456789") == 0x29B1

    def test_matches_reference_implementation(self):
        """Protocol crc16 must match our reference _crc16 for arbitrary data."""
        from ble.protocol import crc16
        data = bytes(range(64))
        assert crc16(data) == _crc16(data)


# ---------------------------------------------------------------------------
# 3. Frame encoder
# ---------------------------------------------------------------------------

class TestFrameEncoder:
    def test_encode_starts_with_0xAA(self):
        from ble.protocol import encode_frame
        frame = encode_frame(msg_type=0x04, payload=b"")
        assert frame[0] == 0xAA

    def test_encode_type_byte(self):
        from ble.protocol import encode_frame
        frame = encode_frame(msg_type=0x03, payload=b"\x00")
        assert frame[1] == 0x03

    def test_encode_length_little_endian(self):
        from ble.protocol import encode_frame
        payload = b"\x01\x02\x03"
        frame = encode_frame(msg_type=0x04, payload=payload)
        length = struct.unpack("<H", frame[2:4])[0]
        assert length == 3

    def test_encode_payload_present(self):
        from ble.protocol import encode_frame
        payload = b"\xDE\xAD\xBE\xEF"
        frame = encode_frame(msg_type=0x04, payload=payload)
        assert frame[4:8] == payload

    def test_encode_crc_appended(self):
        from ble.protocol import encode_frame
        payload = b"\x01"
        frame = encode_frame(msg_type=0x03, payload=payload)
        crc_data = bytes([0x03]) + struct.pack("<H", 1) + payload
        expected_crc = _crc16(crc_data)
        actual_crc = struct.unpack("<H", frame[-2:])[0]
        assert actual_crc == expected_crc

    def test_encode_total_length(self):
        """Frame = 1(START) + 1(TYPE) + 2(LEN) + N(PAYLOAD) + 2(CRC)."""
        from ble.protocol import encode_frame
        payload = b"\x00" * 10
        frame = encode_frame(msg_type=0x04, payload=payload)
        assert len(frame) == 1 + 1 + 2 + 10 + 2

    def test_encode_empty_payload(self):
        from ble.protocol import encode_frame
        frame = encode_frame(msg_type=0x04, payload=b"")
        assert len(frame) == 6   # 1+1+2+0+2


# ---------------------------------------------------------------------------
# 4. Frame decoder
# ---------------------------------------------------------------------------

class TestFrameDecoder:
    def test_decode_valid_frame_returns_type_and_payload(self):
        from ble.protocol import decode_frame
        raw = _build_raw_frame(0x04, b"")
        msg_type, payload = decode_frame(raw)
        assert msg_type == 0x04
        assert payload == b""

    def test_decode_returns_correct_payload(self):
        from ble.protocol import decode_frame
        raw = _build_raw_frame(0x03, b"\x01")
        msg_type, payload = decode_frame(raw)
        assert msg_type == 0x03
        assert payload == b"\x01"

    def test_decode_wrong_start_byte_raises(self):
        from ble.protocol import decode_frame, FrameError
        raw = _build_raw_frame(0x04, b"")
        bad = bytes([0xBB]) + raw[1:]
        with pytest.raises(FrameError):
            decode_frame(bad)

    def test_decode_bad_crc_raises(self):
        from ble.protocol import decode_frame, FrameError
        raw = bytearray(_build_raw_frame(0x04, b"\x01\x02"))
        raw[-1] ^= 0xFF   # corrupt last CRC byte
        with pytest.raises(FrameError):
            decode_frame(bytes(raw))

    def test_decode_truncated_frame_raises(self):
        from ble.protocol import decode_frame, FrameError
        with pytest.raises(FrameError):
            decode_frame(b"\xAA\x04")   # too short

    def test_encode_decode_roundtrip(self):
        from ble.protocol import encode_frame, decode_frame
        payload = bytes(range(20))
        frame = encode_frame(0x10, payload)
        msg_type, decoded = decode_frame(frame)
        assert msg_type == 0x10
        assert decoded == payload


# ---------------------------------------------------------------------------
# 5. Message builders (convenience API)
# ---------------------------------------------------------------------------

class TestMessageBuilders:
    def test_build_cmd_run(self):
        """CMD_RUN payload = program_slot (1 byte)."""
        from ble.protocol import build_cmd_run, decode_frame
        from ble.service import MSG_CMD_RUN
        frame = build_cmd_run(slot=2)
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_CMD_RUN
        assert payload == bytes([2])

    def test_build_cmd_stop(self):
        from ble.protocol import build_cmd_stop, decode_frame
        from ble.service import MSG_CMD_STOP
        frame = build_cmd_stop()
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_CMD_STOP
        assert payload == b""

    def test_build_cmd_reset(self):
        from ble.protocol import build_cmd_reset, decode_frame
        from ble.service import MSG_CMD_RESET
        frame = build_cmd_reset()
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_CMD_RESET
        assert payload == b""

    def test_build_program_chunk(self):
        """PROGRAM_CHUNK payload = chunk_index(2LE) + total_chunks(2LE) + data."""
        from ble.protocol import build_program_chunk, decode_frame
        from ble.service import MSG_PROGRAM_CHUNK
        data = b"\xCA\xFE\xBA\xBE"
        frame = build_program_chunk(chunk_index=0, total_chunks=3, data=data)
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_PROGRAM_CHUNK
        idx, total = struct.unpack("<HH", payload[:4])
        assert idx == 0
        assert total == 3
        assert payload[4:] == data

    def test_build_hub_status(self):
        """HUB_STATUS payload = battery_pct(1) + state(1) + error_code(2LE)."""
        from ble.protocol import build_hub_status, decode_frame
        from ble.service import MSG_HUB_STATUS
        frame = build_hub_status(battery_pct=85, state=1, error_code=0)
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_HUB_STATUS
        batt, state, err = struct.unpack("<BBH", payload)
        assert batt == 85
        assert state == 1
        assert err == 0

    def test_build_ack(self):
        """ACK payload = ack_type(1) + status(1)."""
        from ble.protocol import build_ack, decode_frame
        from ble.service import MSG_ACK
        frame = build_ack(ack_type=0x01, status=0x00)
        msg_type, payload = decode_frame(frame)
        assert msg_type == MSG_ACK
        assert payload == bytes([0x01, 0x00])
