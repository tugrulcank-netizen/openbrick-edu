# IDE CI Debugging — Lessons Learned & Best Practices

**Date:** 2026-03-07 | **Session:** Day 6 | **Author:** AI-assisted dev log

---

## What Went Wrong Today

Setting up Jest + TypeScript + CI for the first time took ~15 commits to get green.
Here is a precise record of every error, its root cause, and how to avoid it next time.

---

## Error Log

### Error 1 — `npm error Missing script: "test"`
**Root cause:** The Vite scaffold (`npm create vite`) does not include a `test` script.  
**Fix:** Add `"test": "jest"` to `package.json` scripts manually.  
**Prevention:** Always add the `test` script immediately after scaffolding. Do not assume it exists.

---

### Error 2 — `ts-jest` not installed
**Root cause:** `jest` was in `devDependencies` but `ts-jest` was not — Jest cannot process `.ts` files without it.  
**Fix:** `npm install --save-dev ts-jest`  
**Prevention:** When adding Jest to a TypeScript project, always install `jest`, `ts-jest`, `@types/jest` together in one command.

```bash
npm install --save-dev jest ts-jest @types/jest jest-environment-jsdom @types/web-bluetooth
```

---

### Error 3 — `@typescript-eslint/no-unused-vars` lint error on CI but not locally
**Root cause:** A `const { device }` destructuring was correct in the original file but a `sed` command accidentally replaced it with a bare `makeConnectedManager()` call, removing the variable. CI caught it; local tests did not because ESLint was not run locally before committing.  
**Fix:** Fix the destructuring, re-run `npm run lint` locally before committing.  
**Prevention:** Always run `npm run lint && npm test` together before every commit. Never commit after tests alone.

```bash
# Correct pre-commit sequence
npm run lint && npm run type-check && npm test
```

---

### Error 4 — `npm run type-check` missing script
**Root cause:** The CI workflow expected `npm run type-check` but it was not in `package.json`.  
**Fix:** Add `"type-check": "tsc --noEmit -p tsconfig.app.json"` to scripts.  
**Prevention:** When writing a CI workflow that calls `npm run X`, immediately add script `X` to `package.json` in the same commit. Never write a workflow step without the matching script.

---

### Error 5 — TypeScript does not know about `jest`, `describe`, `BluetoothDevice`
**Root cause:** `tsconfig.app.json` only had `"types": ["vite/client"]`. Jest globals and Web Bluetooth types were not included.  
**Fix:**
- Add `"jest"` and `"web-bluetooth"` to `"types"` in `tsconfig.app.json`
- Install `@types/web-bluetooth`
- Exclude `__tests__` from `tsconfig.app.json` (test files have their own type environment)
- Create `tsconfig.jest.json` with `esModuleInterop: true` for ts-jest

**Prevention:** When adding a new technology (Jest, Web Bluetooth), immediately update `tsconfig` types. Create a dedicated `tsconfig.jest.json` at the start of IDE setup.

---

### Error 6 — `SharedArrayBuffer not assignable to ArrayBuffer`
**Root cause:** `Uint8Array.buffer` returns `ArrayBufferLike` which includes `SharedArrayBuffer`. Web Bluetooth's `writeValueWithResponse` only accepts `ArrayBuffer`.  
**Fix:** Cast explicitly: `wire.buffer as ArrayBuffer`  
**Prevention:** When calling Web Bluetooth write methods with a `Uint8Array`, always cast `.buffer as ArrayBuffer`.

---

### Error 7 — Coverage at 52% on CI (passes locally at 91%)
**Root cause:** CI ran coverage over ALL files in `src/` including `App.tsx` and `main.tsx` (0% coverage). Locally, Jest only found the `ble/` files because the test match was narrow, but coverage collected from everything.  
**Fix:** Add `collectCoverageFrom` to `jest.config.js` scoped to `src/ble/**/*.ts`.  
**Prevention:** Always set `collectCoverageFrom` explicitly when coverage is required. Never rely on Jest's default collection scope.

```js
collectCoverageFrom: [
  'src/ble/**/*.ts',
  '!src/ble/**/__tests__/**',
],
```

---

### Error 8 — Tests pass locally but fail on CI (`TextEncoder is not defined`, `navigator.bluetooth` missing)
**Root cause:** Local Jest used `testEnvironment: 'node'` where `TextEncoder` works fine. CI used jsdom implicitly (or vice versa). The environments differ. `navigator.bluetooth` and `TextEncoder` behave differently or are absent depending on the environment.  
**Fix:**
- Set `testEnvironment: 'jest-environment-jsdom'` explicitly
- Create `jest.setup.ts` to polyfill `TextEncoder` and `TextDecoder` from Node's `util` module
- Add `setupFiles: ['./jest.setup.ts']` to `jest.config.js`

**Prevention:** Always set `testEnvironment` explicitly — never rely on the default. For any test that uses browser APIs (`navigator`, `TextEncoder`, `Blob`, `ArrayBuffer`), use jsdom + polyfills from day one.

```ts
// jest.setup.ts
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder as typeof global.TextEncoder;
global.TextDecoder = TextDecoder as typeof global.TextDecoder;
```

---

## Root Cause Summary

All 8 errors share one underlying pattern: **the Jest + TypeScript + jsdom + Web Bluetooth setup was not fully defined upfront.** Each error was a missing piece of the same configuration puzzle, discovered one at a time through CI failures.

---

## Best Practices for Next Time

### 1. Install the full test stack in one shot
When starting any new IDE module that uses Jest + TypeScript + browser APIs:

```bash
npm install --save-dev \
  jest ts-jest @types/jest \
  jest-environment-jsdom \
  @types/web-bluetooth
```

### 2. Create all config files before writing any test
Before writing the first test file, create:
- `jest.config.js` — with `testEnvironment`, `collectCoverageFrom`, `setupFiles`, `transform`, `tsconfig`
- `tsconfig.jest.json` — with `esModuleInterop: true`, correct `lib` and `module`
- `jest.setup.ts` — with `TextEncoder`/`TextDecoder` polyfills
- Add `test` and `type-check` scripts to `package.json`

### 3. Run CI locally before pushing
The CI command is:
```bash
npm test -- --coverage --coverageThreshold='{"global":{"lines":75}}'
```
Run this exact command locally and confirm it passes **before** pushing. Do not rely on `npm test` alone.

### 4. Always run lint + type-check + test together
```bash
npm run lint && npm run type-check && npm test -- --coverage
```
If any of these fail locally, do not push.

### 5. Separate type-check from test execution
`tsconfig.app.json` should exclude `__tests__/` — test files use Jest's own global types and should not be type-checked by the app tsconfig. Use `tsconfig.jest.json` for ts-jest only.

### 6. When using Web Bluetooth types
- Always cast `Uint8Array.buffer as ArrayBuffer` when passing to `writeValueWithResponse`
- Always add `"web-bluetooth"` to `tsconfig` types
- Always mock `navigator.bluetooth` with `Object.defineProperty` in tests

### 7. Scope `collectCoverageFrom` explicitly
In any project with scaffolded files (Vite, CRA etc.), always scope coverage to the modules under test. Otherwise App.tsx, main.tsx and other scaffold files drag coverage to 0%.

---

## Quick Reference — Complete jest.config.js Template

```js
export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'jest-environment-jsdom',
  setupFiles: ['./jest.setup.ts'],
  testMatch: ['**/src/**/__tests__/**/*.test.ts'],
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      useESM: true,
      diagnostics: false,
      tsconfig: 'tsconfig.jest.json'
    }],
  },
  extensionsToTreatAsEsm: ['.ts'],
  collectCoverageFrom: [
    'src/<module>/**/*.ts',
    '!src/<module>/**/__tests__/**',
  ],
};
```

## Quick Reference — Complete tsconfig.jest.json Template

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src"]
}
```

---

## Time Cost Today

| Phase | Commits | Time lost |
|-------|---------|-----------|
| Missing test script + ts-jest | 2 | ~10 min |
| Unused variable lint error | 3 | ~15 min |
| Missing type-check script | 2 | ~10 min |
| TypeScript unknown types | 2 | ~15 min |
| Coverage scope wrong | 2 | ~10 min |
| jsdom + TextEncoder | 2 | ~15 min |
| **Total** | **13 fix commits** | **~75 min** |

With the templates above, this entire setup should take **1 commit and < 10 minutes** next time.
