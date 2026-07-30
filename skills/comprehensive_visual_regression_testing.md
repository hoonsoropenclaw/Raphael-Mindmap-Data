# Comprehensive Visual Regression Testing

## Overview
The **comprehensive_visual_regression_testing** skill focuses on establishing a robust cross-browser visual regression testing infrastructure. This includes setting up fault injection verification, managing baselines, ensuring the integrity of test artifacts, and isolating fault evidence to maintain accurate and reliable test results.

## Key Components

### 1. Cross Browser Visual Regression Setup

#### Purpose
Establish a visual regression testing framework using Playwright that supports multiple browsers (Chromium, Firefox, WebKit, and mobile Chromium). This involves configuring the test environment, setting up the test matrix, and managing baselines.

#### Key Code Snippet
```javascript
// playwright.config.mjs
import { defineConfig, devices } from '@playwright/test';
import { normalizeBaseURL } from './scripts/vrt-utils.mjs';

const baseURL = normalizeBaseURL(process.env.VRT_BASE_URL || 'http://127.0.0.1:4317');

export default defineConfig({
  testDir: './tests',
  /* ... */
});
```

#### Common Errors and Prevention
- **Error**: Rendering differences between browsers lead to false positives.
  - **Solution**: Set up independent baselines for each browser to prevent normal rendering differences between Blink, Gecko, and WebKit from being misinterpreted as errors.
- **Error**: Port conflicts in CI environments cause test failures.
  - **Solution**: Use the `reuseExistingServer: false` option to ensure tests fail and provide clear error messages when ports are in use.

### 2. Fault Injection Verification

#### Purpose
Verify the interception mechanism of visual regression tests by injecting faults (e.g., modifying CSS styles) to ensure the tests can correctly detect expected regressions.

#### Key Code Snippet
```javascript
// scripts/verify-fault.mjs
const child = spawn(
  process.execPath,
  [
    'node_modules/@playwright/test/cli.js',
    'test',
    '--reporter=json',
    '--workers=4',
    '--output=test-results/fault-artifacts'
  ],
  {
    cwd: process.cwd(),
    env: { ...process.env, VRT_FAULT: '1' },
  }
);
```

#### Common Errors and Prevention
- **Error**: Fault injection artifacts are confused with the final report, leading to inaccuracies.
  - **Solution**: Store fault injection artifacts in a separate directory (e.g., `test-results/fault-artifacts`) and ensure the final report remains unaffected.
- **Error**: Baseline is not properly restored after fault injection, causing subsequent tests to fail.
  - **Solution**: After fault injection tests, run a clean test to verify that the baseline has not been corrupted.

### 3. Baseline Management

#### Purpose
Manage visual regression test baselines, including updating, reviewing changes, and handling baseline migrations.

#### Key Code Snippet
```bash
# Update baseline
npm run test:visual:update
```

#### Common Errors and Prevention
- **Error**: Unreviewed baseline updates lead to inaccurate test results.
  - **Solution**: Set `npm run test:visual:update` as a manually triggered action and review snapshot diffs after updating to ensure changes are expected.
- **Error**: OS or dependency upgrades cause baseline mismatches.
  - **Solution**: Treat baseline migration as a deliberate change and re-review all baselines after updating.

### 4. Artifact SHA256 Management

#### Purpose
Ensure the integrity of test artifacts by using SHA256 checks to verify that files have not been tampered with or corrupted during the test process.

#### Key Code Snippet
```javascript
// scripts/create-manifest.mjs
const files = (await Promise.all(include.map(collect))).flat().filter((file) => file !== output).sort();
const lines = [];
for (const relative of files) {
  const data = await import('node:fs/promises').then(({ readFile }) => readFile(path.join(root, relative)));
  lines.push(`${createHash('sha256').update(data).digest('hex')}  ${relative}`);
}
await writeFile(output, `${lines.join('
')}
`);
```

#### Common Errors and Prevention
- **Error**: SHA256 checksum failures cause test interruptions.
  - **Solution**: Ensure all test artifacts remain unmodified during the test process and perform integrity checks after testing.
- **Error**: Missing or corrupted files during SHA256 verification.
  - **Solution**: Conduct file integrity checks before testing begins and provide clear error messages when issues are detected.

### 5. Fault Evidence Isolation

#### Purpose
Isolate evidence (e.g., actual/diff/trace) generated during fault injection from the final report to prevent contamination of clean test results.

#### Key Code Snippet
```javascript
// scripts/verify-fault.mjs
await rm('test-results/fault-artifacts', { recursive: true, force: true });
```

#### Common Errors and Prevention
- **Error**: Fault evidence and final report are stored in the same directory, leading to inaccuracies.
  - **Solution**: Store fault evidence in a separate directory and perform isolation processing after testing.
- **Error**: Fault evidence is not properly deleted, affecting subsequent tests.
  - **Solution**: Clean the fault evidence directory before each test to ensure a clean testing environment.

## Conclusion
By integrating these components, the **comprehensive_visual_regression_testing** skill ensures a robust, reliable, and accurate visual regression testing process across multiple browsers. This approach minimizes false positives, maintains baseline integrity, and isolates fault evidence, resulting in more dependable test outcomes.