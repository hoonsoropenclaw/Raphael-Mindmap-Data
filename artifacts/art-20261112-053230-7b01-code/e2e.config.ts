import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';

export default {
  // ★ rev1：明確指定 tests 目錄，避免預設 glob 與交付佈局不一致造成 NO_TESTS
  tests: ['tests/**/*.e2e.ts'],
  targets: [{
    engine: web(),
    app: { url: 'http://127.0.0.1:8932/' },
  }],
} satisfies E2EConfig;
