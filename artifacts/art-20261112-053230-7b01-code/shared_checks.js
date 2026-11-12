export const JS_D1 = `() => {
  const el = document.querySelector('.nav-item.active');
  if (!el) return {error: 'no .nav-item.active'};
  const cs = getComputedStyle(el);
  return {color: cs.color, background: cs.backgroundColor};
}`;

export const JS_D2 = `() => {
  const styles = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
  return {
    defined: styles.includes('--border-strong:'),
    referenced: /var\\(--border-strong\\)/.test(styles),
  };
}`;

export const JS_BODY = `() => document.body.innerText.length`;

export const JS_THEME = `() => document.documentElement.dataset.theme`;

export const JS_SIDEBAR = `() => {
  const s = document.querySelector('.sidebar');
  if (!s) return null;
  return {sidebar: s.getBoundingClientRect().width, win: window.innerWidth};
}`;

export const JS_H1 = `() => { const h = document.querySelector('h1'); return h ? h.innerText : null; }`;
