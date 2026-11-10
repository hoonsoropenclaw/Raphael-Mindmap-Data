import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// 與 baseline（playwright 直接寫）使用「同一份」檢查邏輯：shared_checks.js
// 唯一變因 = 測試框架，不是檢查內容不同。

const JS_D1 = `() => {
  const el = document.querySelector('.nav-item.active');
  if (!el) return {error: 'no .nav-item.active'};
  const cs = getComputedStyle(el);
  return {color: cs.color, background: cs.backgroundColor};
}`;

const JS_D2 = `() => {
  const styles = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
  return {defined: styles.includes('--border-strong:'), referenced: /var\\(--border-strong\\)/.test(styles)};
}`;

const JS_BODY = `() => document.body.innerText.length`;
const JS_THEME = `() => document.documentElement.dataset.theme`;
const JS_SIDEBAR = `() => {
  const s = document.querySelector('.sidebar');
  if (!s) return null;
  return {sidebar: s.getBoundingClientRect().width, win: window.innerWidth};
}`;
const JS_H1 = `() => { const h = document.querySelector('h1'); return h ? h.innerText : null; }`;

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

test('D6 對照組(應過)：頁面載入且 h1 有內容', async ({ app, browser }) => {
  await app.open('/');
  const h1 = await browser.evaluate(JS_H1);
  expect(typeof h1 === 'string' && h1.trim().length > 0).toBe(true);
});

test('D1 假綠燈：active 導覽文字對比 < 4.5:1', async ({ app, browser }) => {
  await app.open('/');
  const d1 = await browser.evaluate(JS_D1);
  const ratio = contrastRatio(d1.color, d1.background);
  console.log('D1 ratio =', ratio, JSON.stringify(d1));
  expect(ratio).not.toBeNull();
  expect(ratio!).toBeLessThan(4.5);
});

test('D2 dead token：--border-strong 定義但無任何 var() 引用', async ({ app, browser }) => {
  await app.open('/');
  const d2 = await browser.evaluate(JS_D2);
  console.log('D2 =', JSON.stringify(d2));
  expect(d2.defined).toBe(true);
  expect(d2.referenced).toBe(false);
});

test('D3 死按鈕：匯出報表按鈕點擊後無可觀察反應', async ({ app, browser }) => {
  await app.open('/');
  const before = await browser.evaluate(JS_BODY);
  await browser.locator('button.btn').click();
  const after = await browser.evaluate(JS_BODY);
  console.log('D3 before/after =', before, after);
  expect(after).toBe(before);
});

test('D4 狀態不持久：切深色後 reload 回到 light', async ({ app, browser }) => {
  await app.open('/');
  await browser.locator('#themeBtn').click();
  const themed = await browser.evaluate(JS_THEME);
  await app.open('/');
  const afterReload = await browser.evaluate(JS_THEME);
  console.log('D4 toggle/reload =', themed, afterReload);
  expect(afterReload).not.toBe(themed);
});

test('D5 側欄未響應式：360px 下側欄寬度 ≥ 視窗一半', async ({ app, browser }) => {
  await app.open('/');
  await browser.setViewport({ width: 360, height: 800 });
  await app.open('/');
  const w = await browser.evaluate(JS_SIDEBAR);
  console.log('D5 =', JSON.stringify(w));
  expect(w.sidebar).toBeGreaterThanOrEqual(w.win * 0.5);
});

test('D7 對照組(應敗)：斷言頁面上不存在的字串必須失敗', async ({ app, browser }) => {
  await app.open('/');
  await expect(browser.locator('h1')).toContainText('__NO_SUCH_TEXT_9f3a__');
});
