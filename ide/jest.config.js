export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'jest-environment-jsdom',
  setupFiles: ['./jest.setup.ts'],
  testMatch: ['**/src/**/__tests__/**/*.test.ts'],
  transform: {
    '^.+\\.ts$': ['ts-jest', { useESM: true, diagnostics: false, tsconfig: 'tsconfig.jest.json' }],
  },
  extensionsToTreatAsEsm: ['.ts'],
  collectCoverageFrom: [
    'src/ble/**/*.ts',
    '!src/ble/**/__tests__/**',
  ],
};
