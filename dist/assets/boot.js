import { createScene } from './scene.js';
const ZH = document.documentElement.lang.startsWith('zh');
const STAGES = ZH ? [
  ['硅。', '提纯的沙，变得精确。'],
  ['芯片。', '算力，在等待通信。'],
  ['GPU。', '显存、互联与服务，一起调优。'],
  ['金。', '有用的 AI，交付到你手上。'],
] : [
  ['Silicon.', 'Sand, purified and made precise.'],
  ['Chip.', 'Compute, waiting on communication.'],
  ['GPU.', 'Memory, links and serving, tuned together.'],
  ['Gold.', 'Useful AI, delivered.'],
];
const hero = document.querySelector('.sand-hero');
const heroCanvas = document.querySelector('.hero-canvas');
const h = heroCanvas && createScene(heroCanvas, { mode: 'hero' });
if (h) {
  document.documentElement.classList.add('gl');
  const onScroll = () => { const r = hero.getBoundingClientRect(); h.setScroll(Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight)))); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
} else document.documentElement.classList.add('no-gl');

const storyCanvas = document.querySelector('.story-canvas');
const s = storyCanvas && createScene(storyCanvas, { mode: 'story' });
const metrics = [...document.querySelectorAll('.metric')];
const nameEl = document.querySelector('.stage-name'), lineEl = document.querySelector('.stage-line'), idxEl = document.querySelector('.stage-index');
let current = -1;
const setStep = i => {
  if (i === current) return; current = i; s && s.setStep(i);
  metrics.forEach((m, k) => m.classList.toggle('active', k === i));
  if (nameEl) { nameEl.textContent = STAGES[i][0]; lineEl.textContent = STAGES[i][1]; idxEl.textContent = `0${i + 1} / 04`; }
};
const pick = () => {
  const mid = innerHeight * .5; let best = 0, bd = Infinity;
  metrics.forEach((m, i) => { const r = m.getBoundingClientRect(), d = Math.abs((r.top + r.bottom) / 2 - mid); if (d < bd) { bd = d; best = i; } });
  setStep(best);
};
addEventListener('scroll', pick, { passive: true }); pick();
