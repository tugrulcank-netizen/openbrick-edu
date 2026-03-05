"""
BLE GATT service UUID constants for OpenBrick EDU.

Spec: ADR-003 — BLE GATT Service UUID Scheme.

Base UUID: 4f70656e-4272-6963-6b00-000000000000
("OpenBrick" encoded in ASCII at bytes 0–8)

All UUIDs use the same base with a unique suffix per characteristic.
The IDE (ide/src/ble/uuids.ts) must mirror these constants exactly.
docs/ble-spec.md is the single source of truth for both.
"""

# ---------------------------------------------------------------------------
# Service and Characteristic UUIDs (ADR-003)
# ---------------------------------------------------------------------------

HUB_SERVICE_UUID     = "4f70656e-4272-6963-6b00-000000000001"
PROGRAM_UPLOAD_UUID  = "4f70656e-4272-6963-6b00-000000000002"
RUN_STOP_UUID        = "4f70656e-4272-6963-6b00-000000000003"
TELEMETRY_UUID       = "4f70656e-4272-6963-6b00-000000000004"
HUB_STATUS_UUID      = "4f70656e-4272-6963-6b00-000000000005"

# ---------------------------------------------------------------------------
# Message type bytes (ADR-004)
# ---------------------------------------------------------------------------

# IDE → Hub
MSG_PROGRAM_CHUNK = 0x01   # chunked binary upload
MSG_PROGRAM_DONE  = 0x02   # signals upload complete
MSG_CMD_RUN       = 0x03   # run program in slot
MSG_CMD_STOP      = 0x04   # stop running program
MSG_CMD_RESET     = 0x05   # reset hub state

# Hub → IDE
MSG_TELEMETRY     = 0x10   # streaming sensor values
MSG_HUB_STATUS    = 0x11   # battery, state, error code
MSG_ACK           = 0x12   # acknowledgement
