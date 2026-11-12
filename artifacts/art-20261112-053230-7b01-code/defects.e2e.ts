import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// ★ F4（rev1）：檢查邏輯不再 inline 複製，改為 import 共用的 shared_checks.js
//   （由 baseline 端 `python3 checks_shared.py --emit-js` 產生，兩側同一份來源）。
// ★ F5（rev1）：D3 的等待、D4 的重載、D5 的視窗與 baseline 對齊，消除框架以外的變因。

import {
  JS_D1, JS_D2, JS_BODY, JS_THEME, JS_SIDEBAR, JS_H1,
} from '../shared_checks.js';

// 與 baseline 對齊的固定等待策略（見 baseline README「已知限制」）
const D3_WAIT_MS = 300;

// ★ rev1：這個框架沒有 browser.waitForTimeout（已於 node_modules 實測確認
//   `waitForTimeout` 在 e2e / @e2e-dev/web 兩個套件中都不存在，用了會 30s timeout）。
//   改用頁面內的 setTimeout promise —— 語意等同 Playwright 的 wait_for_timeout。
const JS_WAIT = (ms: number) => `() => new Promise(r => setTimeout(r, ${ms}))`;

// ★ rev1：頁面路徑。rev0 用 app.open(PAGE_PATH)，而交付的頁面檔叫 after.html 不是
//   index.html → 伺服器回目錄清單頁（rev0 的 D7 trace 裡 observed 文字就是
//   "Directory listing for /"，證實當時是靠作者本機的 index.html 才跑得動）。
//   rev1 直接開 /after.html，與 baseline 組對齊，不依賴任何未說明的檔名假設。
const PAGE_PATH = '/after.html';

// OKLCH→sRGB 換算（CSS Color 4 §12），與 baseline checks_shared.py 同一套公式。
function oklchToSrgb(L: number, C: number, H: number): number[] {
  const h = (H * Math.PI) / 180;
  const a = C * Math.cos(h), b = C * Math.sin(h);
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
  const l = l_ ** 3, m = m_ ** 3, s = s_ ** 3;
  const cl = (c: number) => Math.max(0, Math.min(1, c));
  return [
    cl(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
    cl(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
    cl(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
  ];
}

function parseColor(css: string): number[] | null {
  if (!css) return null;
  const s = String(css).trim();
  if (/^transparent$/i.test(s) || /^none$/i.test(s)) return null;
  let m = /oklch\(\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)/i.exec(s);
  if (m) return oklchToSrgb(Number(m[1]), Number(m[2]), Number(m[3]));
  m = /rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)/i.exec(s);
  if (m) return [Number(m[1]) / 255, Number(m[2]) / 255, Number(m[3]) / 255];
  return null;
}

function contrastRatio(fgCss: string, bgCss: string): number | null {
  const fg = parseColor(fgCss), bg = parseColor(bgCss);
  if (!fg || !bg) return null;
  const lin = (c: number) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const lum = (c: number[]) => { const [r, g, b] = c.map(lin); return 0.2126*r + 0.7152*g + 0.0722*b; };
  const l1 = lum(fg), l2 = lum(bg);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

// ★ 結果語意（rev1）：每條測試都帶 expectedOutcome，讓 failed 的兩種語意可區分。
//   'defect-caught'     = 缺陷被檢查器抓到 → 測試 failed 是【正確結果】
//   'defect-already-fixed' = 缺陷早已修好 → 測試 failed 是【正確結果】
//   'control-pass'      = 對照組應通過   → 測試 passed 是【正確結果】
//   'control-fail'      = 對照組應失敗   → 測試 failed 是【正確結果】
export const EXPECTED_OUTCOME = {
  D1: 'defect-already-fixed', // after.html 已修好：實測對比 10.77:1
  D2: 'defect-already-fixed', // after.html 已修好：--border-strong 有 var() 引用
  D3: 'defect-caught',        // 死按鈕仍可重現
  D4: 'defect-caught',        // 主題不持久仍可重現
  D5: 'defect-caught',        // 側欄未響應式仍可重現
  D6: 'control-pass',         // 對照組：應通過
  D7: 'control-fail',         // 對照組：應失敗
};

test('D6 對照組(應過)：頁面載入且 h1 有內容', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  const h1 = await browser.evaluate(JS_H1);
  expect(typeof h1 === 'string' && h1.trim().length > 0).toBe(true);
});

test('D1 假綠燈：active 導覽文字對比 < 4.5:1 [預期 failed：缺陷已修好]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  const d1 = await browser.evaluate(JS_D1);
  const ratio = contrastRatio(d1.color, d1.background);
  console.log('D1 ratio =', ratio, JSON.stringify(d1));
  expect(ratio).not.toBeNull();
  expect(ratio!).toBeLessThan(4.5);
});

test('D2 dead token：--border-strong 定義但無任何 var() 引用 [預期 failed：缺陷已修好]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  const d2 = await browser.evaluate(JS_D2);
  console.log('D2 =', JSON.stringify(d2));
  expect(d2.defined).toBe(true);
  expect(d2.referenced).toBe(false);
});

test('D3 死按鈕：匯出報表按鈕點擊後無可觀察反應 [預期 passed：缺陷被抓到]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  const before = await browser.evaluate(JS_BODY);
  await browser.locator('button.btn').click();
  await browser.evaluate(JS_WAIT(D3_WAIT_MS));
  const after = await browser.evaluate(JS_BODY);
  console.log('D3 before/after =', before, after);
  expect(after).toBe(before);
});

test('D4 狀態不持久：切深色後 reload 回到 light [預期 passed：缺陷被抓到]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  await browser.locator('#themeBtn').click();
  const themed = await browser.evaluate(JS_THEME);
  await app.open(PAGE_PATH);
  const afterReload = await browser.evaluate(JS_THEME);
  console.log('D4 toggle/reload =', themed, afterReload);
  expect(afterReload).not.toBe(themed);
});

test('D5 側欄未響應式：360px 下側欄寬度 ≥ 視窗一半 [預期 passed：缺陷被抓到]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  await browser.setViewport({ width: 360, height: 800 });
  await app.open(PAGE_PATH);
  const w = await browser.evaluate(JS_SIDEBAR);
  console.log('D5 =', JSON.stringify(w));
  expect(w.sidebar).toBeGreaterThanOrEqual(w.win * 0.5);
});

test('D7 對照組(應敗)：斷言頁面上不存在的字串必須失敗 [預期 failed：對照組正確失敗]', async ({ app, browser }) => {
  await app.open(PAGE_PATH);
  await expect(browser.locator('h1')).toContainText('__NO_SUCH_TEXT_9f3a__');
});
