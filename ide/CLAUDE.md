# OpenBrick EDU — IDE Instructions

Web-based visual programming environment: Blockly + MicroPython + Web Bluetooth.

## Tech Stack

- **Framework:** React 18+ with TypeScript strict mode
- **Block Editor:** Google Blockly (generates MicroPython)
- **Text Editor:** Monaco Editor (MicroPython syntax highlighting + autocomplete)
- **Charts:** Recharts (live sensor dashboard)
- **BLE:** Web Bluetooth API (Chrome 90+, Edge 90+)
- **Testing:** Jest (unit) + Playwright (E2E)
- **Lint:** ESLint strict + Prettier
- **Build:** Vite
- **i18n:** react-i18next with JSON translation files

## Module Structure

```
ide/
├── src/
│   ├── blockly/
│   │   ├── blocks/            # Custom block JSON definitions by category
│   │   │   ├── hub/           # Hub blocks (LED matrix, speaker, battery, IMU)
│   │   │   ├── motors/        # Motor control blocks
│   │   │   ├── sensors/       # Sensor read blocks (color, distance, force)
│   │   │   └── logic/         # Enhanced logic/loop blocks
│   │   ├── generators/
│   │   │   └── python/        # MicroPython code generators (mirrors blocks/ structure)
│   │   └── toolbox.ts         # Toolbox category definitions and block registration
│   ├── editor/
│   │   ├── MonacoEditor.tsx   # MicroPython text editor component
│   │   └── autocomplete.ts   # Hub API autocomplete definitions
│   ├── ble/
│   │   ├── BleManager.ts      # Web Bluetooth connection state machine
│   │   ├── protocol.ts        # Binary frame encoder/decoder (CRC-16)
│   │   └── types.ts           # BLE message types and constants
│   ├── dashboard/
│   │   ├── SensorPanel.tsx    # Real-time sensor value display
│   │   └── ChartPanel.tsx     # Recharts time-series graphs
│   ├── i18n/
│   │   ├── en.json            # English translations
│   │   └── tr.json            # Turkish translations
│   ├── projects/
│   │   ├── ProjectManager.ts  # Save/load to localStorage + JSON export/import
│   │   └── templates/         # Starter project templates
│   ├── tutorials/             # Guided tutorial engine with step highlighting (post-Phase 2)
│   ├── simulator/             # Virtual hub emulation (post-MVP)
│   └── App.tsx                # Root component, layout, routing
├── public/
├── tests/
│   ├── unit/                  # Jest unit tests
│   └── e2e/                   # Playwright E2E tests
└── vite.config.ts
```

## Component Patterns

- **Functional components only** — no class components.
- **Hooks for state** — useState, useReducer, useContext. No external state library unless complexity demands it.
- **Custom hooks** for shared logic: `useBle()`, `useSensorStream()`, `useProject()`.
- **Props:** All components have explicit TypeScript interfaces. No `any` without `// JUSTIFIED:` comment.
- **Error boundaries** around Blockly workspace and BLE manager — these are the most crash-prone areas.

## Blockly Block Convention

Each block consists of two files:

1. **Block definition:** `src/blockly/blocks/{category}/{block_name}.json`
   - JSON format per Blockly spec
   - Includes `message0`, `args0`, `colour`, `tooltip`, `helpUrl`

2. **Python generator:** `src/blockly/generators/python/{category}/{block_name}.ts`
   - Exports a generator function registered on `pythonGenerator.forBlock`
   - Must produce valid MicroPython targeting the hub HAL API

**Reference implementation:** `blocks/sensors/color_read.json` + `generators/python/sensors/color_read.ts`

When creating new blocks, load skill `@.claude/skills/blockly-block-creation.md` for the full template and worked example.

## Web Bluetooth State Machine

```
DISCONNECTED → SCANNING → CONNECTING → CONNECTED → UPLOADING → RUNNING
     ↑              ↑          ↑            ↑           ↑          |
     └──────────────┴──────────┴────────────┴───────────┴──────────┘
                            (any error or disconnect)
```

- **BleManager** is a singleton — one connection at a time.
- **Auto-reconnect:** 3 attempts with exponential backoff (1s, 2s, 4s), then give up.
- **Timeout:** Connection attempt times out after 10 seconds.
- **Error handling:** All BLE errors surface as user-friendly messages (NFR-U03) — never expose raw DOMException text.
- Full protocol details: load skill `@.claude/skills/ble-protocol.md`

## i18n Key Naming

```
{namespace}.{area}.{element}
```

Examples:
- `blocks.sensors.colorRead.tooltip` — "Read the color sensor value"
- `dashboard.sensors.title` — "Sensor Dashboard"
- `ble.status.connected` — "Connected to hub"
- `errors.ble.timeout` — "Connection timed out. Make sure the hub is powered on."

**Rules:**
- camelCase for multi-word segments
- Every user-visible string MUST use i18n — no hardcoded strings in components
- Add keys to both `en.json` and `tr.json` simultaneously — never leave one behind

## Performance Budget

| Metric                  | Target           | Enforced By          |
|------------------------|------------------|----------------------|
| Initial bundle (gzip)  | < 500 KB         | size-limit in CI     |
| Page load (10 Mbps)    | < 3 seconds      | Lighthouse CI        |
| Blockly workspace init | < 500 ms         | Performance mark     |
| Sensor dashboard FPS   | ≥ 30 fps         | Manual check         |

- **Lazy-load:** Monaco editor, simulator (post-MVP), tutorial engine, advanced Blockly categories.
- **Tree-shake:** Import only needed Recharts components, not the entire library.
- **Image assets:** SVG for icons, WebP for any raster images. No PNGs > 50 KB.

## Testing

**Unit tests (Jest):**
- All Blockly Python generators must have tests verifying output code
- All BLE protocol encode/decode functions must have round-trip tests
- All custom hooks must have tests using `@testing-library/react-hooks`
- Test names describe behavior: `should generate valid MicroPython for color read block`

**E2E tests (Playwright):**
- Critical flows: connect to hub, create block program, upload, run, view dashboard
- Mock Web Bluetooth with Playwright's service worker injection for CI
- Cross-browser: Chrome + Edge minimum (Firefox with BLE adapter where supported)

**Commands:**
```bash
npm test                    # Jest unit tests
npm run test:e2e            # Playwright E2E
npm run lint                # ESLint strict
npm run type-check          # TypeScript strict
npm run build               # Vite production build
npm run size                # Bundle size check
```

## Accessibility (NFR-A01 equivalent)

- All interactive elements must be keyboard navigable
- Blockly workspace: rely on Blockly's built-in keyboard nav
- All images/icons have `alt` text or `aria-label`
- Color contrast: WCAG 2.1 AA minimum (4.5:1 for text)
- Screen reader labels on BLE status, sensor values, and error messages

## Critical Rules

- NEVER use `any` type without a `// JUSTIFIED:` comment explaining why
- NEVER hardcode user-visible strings — always use i18n keys
- NEVER import entire libraries — use named imports for tree-shaking
- NEVER store sensitive data in localStorage (no API keys, tokens, etc.)
- ALWAYS match the component pattern in `App.tsx` and existing components
- ALWAYS add both `en.json` and `tr.json` keys when creating new UI text
- When creating new Blockly blocks, load `@.claude/skills/blockly-block-creation.md`
