export default {
  preset: 'ts-jest/presets/default-esm',
  testEnvironment: 'node',
  testMatch: ['**/src/**/__tests__/**/*.test.ts'],
  transform: {
    '^.+\\.ts$': ['ts-jest', { useESM: true, diagnostics: false, tsconfig: 'tsconfig.jest.json' }],
  },
  extensionsToTreatAsEsm: ['.ts'],
};
