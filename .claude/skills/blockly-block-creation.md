# Skill: Blockly Block Creation

Load this skill when creating new Blockly blocks for the OpenBrick EDU IDE.

---

## Block Creation Checklist

Every new block requires ALL of the following:

1. [ ] Block JSON definition in `ide/src/blockly/blocks/{category}/`
2. [ ] Python code generator in `ide/src/blockly/generators/python/{category}/`
3. [ ] Registration in toolbox config: `ide/src/blockly/toolbox.ts`
4. [ ] i18n keys in both `ide/src/i18n/en.json` AND `ide/src/i18n/tr.json`
5. [ ] Jest test for the Python generator
6. [ ] All checks pass: `npm test && npm run lint && npm run type-check`
7. [ ] `docs/changelog.md` updated

---

## Step 1: Block JSON Definition

File: `ide/src/blockly/blocks/{category}/{block_name}.json`

### Template

```json
{
  "type": "openbrick_{category}_{action}",
  "message0": "%{BKY_OPENBRICK_{CATEGORY}_{ACTION}}",
  "args0": [
    {
      "type": "field_dropdown",
      "name": "PORT",
      "options": [
        ["%{BKY_PORT_1}", "1"],
        ["%{BKY_PORT_2}", "2"],
        ["%{BKY_PORT_3}", "3"],
        ["%{BKY_PORT_4}", "4"],
        ["%{BKY_PORT_5}", "5"],
        ["%{BKY_PORT_6}", "6"]
      ]
    }
  ],
  "output": "Number",
  "colour": 210,
  "tooltip": "%{BKY_OPENBRICK_{CATEGORY}_{ACTION}_TOOLTIP}",
  "helpUrl": ""
}
```

### Block Type Naming Convention

```
openbrick_{category}_{action}
```

Examples:
- `openbrick_sensors_color_read` — read color sensor
- `openbrick_sensors_distance_read` — read distance sensor
- `openbrick_motors_run` — run motor at speed
- `openbrick_motors_run_to_position` — move motor to angle
- `openbrick_hub_led_set` — set LED matrix pixel
- `openbrick_hub_imu_angle` — read IMU angle

### Category Colors

| Category | Hue  | Description        |
|---------|------|--------------------|
| Hub     | 300  | Purple — hub functions (LED, speaker, IMU, battery) |
| Motors  | 40   | Orange — motor control |
| Sensors | 210  | Blue — sensor readings |
| Logic   | 210  | Blue — standard Blockly logic (keep default) |
| Loops   | 120  | Green — standard Blockly loops (keep default) |
| Math    | 230  | Blue — standard Blockly math (keep default) |
| Text    | 160  | Teal — standard Blockly text (keep default) |

### Block Shape Rules

| Shape          | When to Use                        | Blockly Property        |
|---------------|-------------------------------------|-------------------------|
| Value (output) | Block returns a value (sensor read) | `"output": "Number"` or `"output": "String"` |
| Statement      | Block performs an action (motor run) | `"previousStatement": null, "nextStatement": null` |
| Hat            | Event trigger (program start)       | `"hat": "cap"` (Blockly extension) |

### Input Types

| Blockly Type        | Use Case                  | Example                     |
|--------------------|---------------------------|-----------------------------|
| `field_dropdown`   | Fixed choices (port, mode)| Port selection, color mode  |
| `field_number`     | Numeric input with limits | Speed (-100 to 100)        |
| `input_value`      | Accepts another block     | Variable or expression      |
| `field_checkbox`   | Boolean toggle            | Brake on/off                |
| `field_colour`     | Color picker              | LED color selection         |

---

## Step 2: Python Code Generator

File: `ide/src/blockly/generators/python/{category}/{block_name}.ts`

### Template

```typescript
import { PythonGenerator, Order } from "blockly/python";
import type { Block } from "blockly/core";

export function openbrick_{category}_{action}(
  block: Block,
  generator: PythonGenerator
): [string, Order] | string {
  // 1. Extract field values
  const port = block.getFieldValue("PORT");

  // 2. Add import (once per program)
  generator.definitions_["import_openbrick"] =
    "from openbrick import hub";

  // 3. Generate MicroPython code
  // For VALUE blocks (return a value):
  const code = `hub.sensor(${port}).read()`;
  return [code, Order.FUNCTION_CALL];

  // For STATEMENT blocks (perform an action):
  // const code = `hub.motor(${port}).run(${speed})\n`;
  // return code;
}
```

### Code Generation Rules

1. **Import management:** Use `generator.definitions_["import_xxx"]` to ensure each import appears once at the top of the generated program. Key name must be unique per import.

2. **Operator precedence:** Return the correct `Order` for value blocks:
   - `Order.FUNCTION_CALL` — for function calls like `sensor.read()`
   - `Order.NONE` — for simple values (variables, literals)
   - `Order.ATOMIC` — for expressions in parentheses

3. **Statement blocks:** Return a string ending with `\n`. Never return an Order tuple.

4. **Value blocks:** Return `[code, Order]` tuple. Never return just a string.

5. **Child blocks:** Use `generator.valueToCode(block, "INPUT_NAME", Order.NONE)` to get code from connected value blocks.

6. **String safety:** Always validate/sanitize user inputs that end up in generated code.

### Hub API Reference (MicroPython)

Generated code targets these hub APIs:

```python
from openbrick import hub

# Sensors
hub.sensor(port).read()              # Returns dict: {"r": 255, "g": 0, ...} or int
hub.sensor(port).get_type()          # Returns: "color", "distance", "force"

# Motors
hub.motor(port).run(speed)           # speed: -100 to 100
hub.motor(port).stop(brake=True)     # brake: True = hold, False = coast
hub.motor(port).run_to_position(degrees, speed=50)
hub.motor(port).get_angle()          # Returns: int (cumulative degrees)
hub.motor(port).reset_angle()

# Hub
hub.led.set_pixel(x, y, color)      # x: 0-4, y: 0-4, color: (r,g,b) tuple
hub.led.clear()
hub.led.show_text(text, speed=50)
hub.speaker.beep(frequency, duration_ms)
hub.speaker.play_melody(notes)
hub.imu.get_angle(axis)             # axis: "pitch", "roll", "yaw"
hub.imu.get_acceleration(axis)      # axis: "x", "y", "z"
hub.battery.level()                 # Returns: 0-100
hub.wait(seconds)                   # Non-blocking delay
```

---

## Step 3: Register in Toolbox

File: `ide/src/blockly/toolbox.ts`

Add the block to the appropriate category:

```typescript
{
  kind: "category",
  name: "%{BKY_CATEGORY_SENSORS}",
  colour: 210,
  contents: [
    // Existing blocks...
    { kind: "block", type: "openbrick_sensors_color_read" },
    // Add new block here:
    { kind: "block", type: "openbrick_sensors_{new_block}" },
  ],
}
```

**Ordering rule:** Within a category, order blocks from simple/common to complex/rare.

---

## Step 4: Add i18n Keys

### English (`ide/src/i18n/en.json`)

```json
{
  "OPENBRICK_SENSORS_COLOR_READ": "read color on port %1",
  "OPENBRICK_SENSORS_COLOR_READ_TOOLTIP": "Read the RGB color value from the color sensor on the selected port.",
  "PORT_1": "1",
  "PORT_2": "2",
  "CATEGORY_SENSORS": "Sensors"
}
```

### Turkish (`ide/src/i18n/tr.json`)

```json
{
  "OPENBRICK_SENSORS_COLOR_READ": "port %1 renk oku",
  "OPENBRICK_SENSORS_COLOR_READ_TOOLTIP": "Seçilen porttaki renk sensöründen RGB renk değerini oku.",
  "PORT_1": "1",
  "PORT_2": "2",
  "CATEGORY_SENSORS": "Sensörler"
}
```

### i18n Key Naming

```
OPENBRICK_{CATEGORY}_{ACTION}           — block message text
OPENBRICK_{CATEGORY}_{ACTION}_TOOLTIP   — block tooltip
CATEGORY_{NAME}                          — toolbox category name
PORT_{N}                                 — port labels (shared)
```

**Rule:** ALWAYS add keys to BOTH en.json and tr.json simultaneously. Never commit with a missing translation.

---

## Step 5: Write Tests

File: `ide/tests/unit/blockly/generators/{category}/{block_name}.test.ts`

### Test Template

```typescript
import Blockly from "blockly";
import { pythonGenerator } from "blockly/python";
import { openbrick_sensors_color_read } from "@/blockly/generators/python/sensors/color_read";

// Register the generator
pythonGenerator.forBlock["openbrick_sensors_color_read"] =
  openbrick_sensors_color_read;

describe("openbrick_sensors_color_read", () => {
  let workspace: Blockly.Workspace;

  beforeEach(() => {
    workspace = new Blockly.Workspace();
  });

  afterEach(() => {
    workspace.dispose();
  });

  it("should generate valid MicroPython for port 1", () => {
    const block = workspace.newBlock("openbrick_sensors_color_read");
    block.setFieldValue("1", "PORT");

    const code = pythonGenerator.blockToCode(block);

    expect(code).toContain("hub.sensor(1).read()");
  });

  it("should include the openbrick import", () => {
    const block = workspace.newBlock("openbrick_sensors_color_read");
    block.setFieldValue("1", "PORT");

    pythonGenerator.blockToCode(block);

    expect(pythonGenerator.definitions_["import_openbrick"]).toBe(
      "from openbrick import hub"
    );
  });

  it("should generate correct code for all ports", () => {
    for (const port of ["1", "2", "3", "4", "5", "6"]) {
      const block = workspace.newBlock("openbrick_sensors_color_read");
      block.setFieldValue(port, "PORT");

      const [code] = pythonGenerator.blockToCode(block) as [string, number];

      expect(code).toBe(`hub.sensor(${port}).read()`);
    }
  });
});
```

### What to Test

- [ ] Correct MicroPython output for each field combination
- [ ] Import statement is generated exactly once
- [ ] All port values produce valid code
- [ ] Value blocks return correct Order
- [ ] Statement blocks end with `\n`
- [ ] Connected child blocks are incorporated correctly

---

## Worked Example: Color Sensor Read Block

### 1. Block Definition

`ide/src/blockly/blocks/sensors/color_read.json`:
```json
{
  "type": "openbrick_sensors_color_read",
  "message0": "%{BKY_OPENBRICK_SENSORS_COLOR_READ}",
  "args0": [
    {
      "type": "field_dropdown",
      "name": "PORT",
      "options": [
        ["%{BKY_PORT_1}", "1"],
        ["%{BKY_PORT_2}", "2"],
        ["%{BKY_PORT_3}", "3"],
        ["%{BKY_PORT_4}", "4"],
        ["%{BKY_PORT_5}", "5"],
        ["%{BKY_PORT_6}", "6"]
      ]
    },
    {
      "type": "field_dropdown",
      "name": "MODE",
      "options": [
        ["%{BKY_COLOR_MODE_COLOR}", "color"],
        ["%{BKY_COLOR_MODE_RED}", "red"],
        ["%{BKY_COLOR_MODE_GREEN}", "green"],
        ["%{BKY_COLOR_MODE_BLUE}", "blue"],
        ["%{BKY_COLOR_MODE_CLEAR}", "clear"]
      ]
    }
  ],
  "output": "Number",
  "colour": 210,
  "tooltip": "%{BKY_OPENBRICK_SENSORS_COLOR_READ_TOOLTIP}",
  "helpUrl": ""
}
```

### 2. Python Generator

`ide/src/blockly/generators/python/sensors/color_read.ts`:
```typescript
import { PythonGenerator, Order } from "blockly/python";
import type { Block } from "blockly/core";

export function openbrick_sensors_color_read(
  block: Block,
  generator: PythonGenerator
): [string, Order] {
  const port = block.getFieldValue("PORT");
  const mode = block.getFieldValue("MODE");

  generator.definitions_["import_openbrick"] =
    "from openbrick import hub";

  let code: string;
  if (mode === "color") {
    code = `hub.sensor(${port}).read()["color"]`;
  } else {
    code = `hub.sensor(${port}).read()["${mode}"]`;
  }

  return [code, Order.MEMBER];
}
```

### 3. i18n Keys

```json
// en.json
{
  "OPENBRICK_SENSORS_COLOR_READ": "read %2 from color sensor on port %1",
  "OPENBRICK_SENSORS_COLOR_READ_TOOLTIP": "Read a color value from the TCS34725 color sensor.",
  "COLOR_MODE_COLOR": "detected color",
  "COLOR_MODE_RED": "red intensity",
  "COLOR_MODE_GREEN": "green intensity",
  "COLOR_MODE_BLUE": "blue intensity",
  "COLOR_MODE_CLEAR": "light level"
}

// tr.json
{
  "OPENBRICK_SENSORS_COLOR_READ": "port %1 renk sensöründen %2 oku",
  "OPENBRICK_SENSORS_COLOR_READ_TOOLTIP": "TCS34725 renk sensöründen renk değeri oku.",
  "COLOR_MODE_COLOR": "algılanan renk",
  "COLOR_MODE_RED": "kırmızı yoğunluğu",
  "COLOR_MODE_GREEN": "yeşil yoğunluğu",
  "COLOR_MODE_BLUE": "mavi yoğunluğu",
  "COLOR_MODE_CLEAR": "ışık seviyesi"
}
```

### 4. Toolbox Registration

```typescript
// In toolbox.ts, sensors category:
{ kind: "block", type: "openbrick_sensors_color_read" },
```

### 5. Tests — see test template above, adapted for the MODE field.

---

## Common Mistakes

| Mistake                                    | Fix                                              |
|-------------------------------------------|--------------------------------------------------|
| Returning string from value block          | Return `[code, Order]` tuple                     |
| Returning `[code, Order]` from statement   | Return string ending with `\n`                   |
| Hardcoded UI text in block JSON            | Use `%{BKY_...}` references                      |
| Missing Turkish translation                | Always add both en.json and tr.json keys          |
| Import added inside generated code         | Use `generator.definitions_` for top-level imports|
| Not registering in toolbox                 | Add to `toolbox.ts` in correct category           |
| Test doesn't dispose workspace             | Always call `workspace.dispose()` in afterEach    |
