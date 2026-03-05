"""
BLE framed binary protocol for OpenBrick EDU.

Spec: ADR-004 — BLE Framed Binary Protocol Format.

Frame structure:
  [0xAA][TYPE 1B][LENGTH 2B LE][PAYLOAD N bytes][CRC16 2B LE]

CRC-16/CCITT-FALSE covers TYPE + LENGTH + PAYLOAD.
Polynomial: 0x1021, Init: 0xFFFF.

This module is the firmware side of the protocol.
The IDE equivalent lives in ide/src/ble/protocol.ts.
Both must use identical CRC parameters and frame layout.
"""

import struct
from ble.service import (
    MSG_PROGRAM_CHUNK, MSG_PROGRAM_DONE,
    MSG_CMD_RUN, MSG_CMD_STOP, MSG_CMD_RESET,
    MSG_TELEMETRY, MSG_HUB_STATUS, MSG_ACK,
)

FRAME_START = 0xAA
MIN_FRAME_LEN = 6   # START(1) + TYPE(1) + LENGTH(2) + CRC(2)


class FrameError(Exception):
    """Raised when a received frame is malformed or has a bad CRC."""


# ---------------------------------------------------------------------------
# CRC-16/CCITT-FALSE
# ---------------------------------------------------------------------------

def crc16(data: bytes) -> int:
    """Compute CRC-16/CCITT-FALSE over data.

    Polynomial: 0x1021, Init: 0xFFFF.
    Matches the TypeScript implementation in ide/src/ble/protocol.ts.
    """
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


# ---------------------------------------------------------------------------
# Core encoder / decoder
# ---------------------------------------------------------------------------

def encode_frame(msg_type: int, payload: bytes) -> bytes:
    """Encode a message into a framed binary packet.

    Args:
        msg_type: One of the MSG_* constants from ble.service.
        payload:  Raw payload bytes (0–500 bytes).

    Returns:
        Complete frame as bytes ready to write to a BLE characteristic.
    """
    length = len(payload)
    header = bytes([msg_type]) + struct.pack("<H", length)
    crc_input = header + payload
    crc = crc16(crc_input)
    return bytes([FRAME_START]) + crc_input + struct.pack("<H", crc)


def decode_frame(data: bytes) -> tuple:
    """Decode a framed binary packet.

    Args:
        data: Raw bytes received from a BLE characteristic.

    Returns:
        (msg_type: int, payload: bytes)

    Raises:
        FrameError: If the frame is too short, has a bad start byte,
                    or fails CRC validation.
    """
    if len(data) < MIN_FRAME_LEN:
        raise FrameError(
            f"Frame too short: {len(data)} bytes (minimum {MIN_FRAME_LEN})"
        )

    if data[0] != FRAME_START:
        raise FrameError(
            f"Invalid start byte: 0x{data[0]:02X} (expected 0x{FRAME_START:02X})"
        )

    msg_type = data[1]
    length = struct.unpack("<H", data[2:4])[0]
    payload = data[4 : 4 + length]
    received_crc = struct.unpack("<H", data[4 + length : 4 + length + 2])[0]

    crc_input = bytes([msg_type]) + struct.pack("<H", length) + payload
    expected_crc = crc16(crc_input)

    if received_crc != expected_crc:
        raise FrameError(
            f"CRC mismatch: received 0x{received_crc:04X}, "
            f"expected 0x{expected_crc:04X}"
        )

    return msg_type, payload


# ---------------------------------------------------------------------------
# Message builders (convenience API)
# ---------------------------------------------------------------------------

def build_cmd_run(slot: int) -> bytes:
    """Build a CMD_RUN frame. Payload: program_slot (1 byte)."""
    return encode_frame(MSG_CMD_RUN, bytes([slot]))


def build_cmd_stop() -> bytes:
    """Build a CMD_STOP frame. Empty payload."""
    return encode_frame(MSG_CMD_STOP, b"")


def build_cmd_reset() -> bytes:
    """Build a CMD_RESET frame. Empty payload."""
    return encode_frame(MSG_CMD_RESET, b"")


def build_program_chunk(chunk_index: int, total_chunks: int, data: bytes) -> bytes:
    """Build a PROGRAM_CHUNK frame.

    Payload: chunk_index(2B LE) + total_chunks(2B LE) + data
    """
    header = struct.pack("<HH", chunk_index, total_chunks)
    return encode_frame(MSG_PROGRAM_CHUNK, header + data)


def build_program_done(total_size: int) -> bytes:
    """Build a PROGRAM_DONE frame. Payload: total_size (4B LE)."""
    return encode_frame(MSG_PROGRAM_DONE, struct.pack("<I", total_size))


def build_hub_status(battery_pct: int, state: int, error_code: int) -> bytes:
    """Build a HUB_STATUS frame.

    Payload: battery_pct(1B) + state(1B) + error_code(2B LE)
    """
    return encode_frame(MSG_HUB_STATUS, struct.pack("<BBH", battery_pct, state, error_code))


def build_ack(ack_type: int, status: int) -> bytes:
    """Build an ACK frame. Payload: ack_type(1B) + status(1B)."""
    return encode_frame(MSG_ACK, bytes([ack_type, status]))
