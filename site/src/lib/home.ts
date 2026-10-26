import { createTooltip } from './tooltip';
import type { FilterValues } from './presentation';
const tooltip = createTooltip();
const behavior = () => matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' as const : 'smooth' as const;
const form = document.querySelector<HTMLFormElement>('#filters')!;
const fields = ['impact', 'category', 'org', 'q'] as const;
const control = (name: string) => form.elements.namedItem(name) as HTMLInputElement | HTMLSelectElement;
function filter(sync = true) {
  const values = Object.fromEntries(fields.map(name => [name, control(name).value]));
  let count = 0;
  document.querySelectorAll<HTMLElement>('.event-list .event').forEach(item => {
    const { impact, category, orgs, search } = item.dataset;
    const match = (!values.impact || (values.impact === 'SA' ? impact === 'S' || impact === 'A' : values.impact === impact))
      && (!values.category || values.category === category)
      && (!values.org || (JSON.parse(orgs ?? '[]') as string[]).includes(values.org))
      && (search ?? '').includes(values.q.trim().toLowerCase());
    item.hidden = !match;
    if (match) count++;
  });
  document.querySelector('#results')!.textContent = count ? `显示 ${count} 条事件` : '没有符合条件的事件，请调整筛选。';
  document.querySelector('#empty-results')?.remove();
  if (!count) {
    const empty = document.createElement('div'); empty.id = 'empty-results'; empty.className = 'empty-state';
    const button = document.createElement('button'); button.type = 'button'; button.textContent = '清除筛选';
    button.addEventListener('click', () => { form.reset(); control('q').focus(); });
    empty.append(button); document.querySelector('#results')!.after(empty);
  }
  if (sync) {
    const url = new URL(location.href);
    fields.forEach(name => values[name] ? url.searchParams.set(name, values[name]) : url.searchParams.delete(name));
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  }
}
function applyFilter(partial: FilterValues) {
  fields.forEach(name => { control(name).value = partial[name] ?? ''; });
  filter();
  document.querySelector('#events-heading')!.scrollIntoView({behavior:behavior(),block:'start'});
}
let flashTimer: ReturnType<typeof setTimeout>;
function jump(id: string) {
  const card = document.getElementById(`e-${id}`);
  if (!card) return;
  tooltip.close();
  if (card.hidden) form.reset();
  card.querySelector('details')!.open = true;
  document.querySelectorAll('.event.flash').forEach(el => el.classList.remove('flash'));
  clearTimeout(flashTimer); card.classList.add('flash');
  flashTimer = setTimeout(() => card.classList.remove('flash'), 2000);
  card.querySelector<HTMLAnchorElement>('h3 a')!.focus({preventScroll:true});
  card.scrollIntoView({behavior:behavior(),block:'start'});
  history.replaceState(null, '', `${location.pathname}${location.search}#e-${id}`);
}
function jumpHash() {
  if (location.hash.startsWith('#e-')) {
    try { jump(decodeURIComponent(location.hash.slice(3))); } catch { /* Ignore malformed hashes. */ }
  }
}
function restore() {
  const query = new URLSearchParams(location.search);
  fields.forEach(name => { control(name).value = query.get(name) ?? ''; });
  filter(false);
}
restore(); form.hidden = false;
form.addEventListener('submit', e => e.preventDefault());
form.addEventListener('input', () => filter());
form.addEventListener('reset', () => { fields.forEach(name => { control(name).value = ''; }); filter(); });
window.addEventListener('popstate', restore);
const toggle = document.querySelector<HTMLInputElement>('#show-all')!;
document.querySelector<HTMLElement>('#timeline-control')!.hidden = false;
const points = [...document.querySelectorAll<SVGAElement>('.timeline-point')];
document.querySelector('.lane-chart')!.classList.add('js-filterable');
document.querySelector('#timeline-count')!.textContent = `当前显示 ${points.filter(p => ['S','A'].includes(p.dataset.impact!)).length} 条`;
const panel = document.querySelector<HTMLElement>('#timeline-detail')!;
const templates = new Map([...document.querySelectorAll<HTMLTemplateElement>('template[data-detail]')].map(t => [t.dataset.detail, t]));
function show(point: SVGAElement) {
  const template = templates.get(point.dataset.id);
  if (!template) return;
  points.forEach(p => p.classList.toggle('selected', p === point));
  panel.replaceChildren(template.content.cloneNode(true));
}
function preview(point: SVGAElement) {
  show(point);
  const source = templates.get(point.dataset.id)?.content;
  if (!source) return;
  const content = document.createDocumentFragment();
  ['.event-meta', 'h3', 'p.muted'].forEach(selector => {
    const node = source.querySelector(selector); if (node) content.append(node.cloneNode(true));
  });
  const summary = document.createElement('p');
  const text = source.querySelector('p:not(.muted)')?.textContent ?? '';
  summary.textContent = Array.from(text).slice(0,60).join('') + (Array.from(text).length > 60 ? '…' : '');
  const button = document.createElement('button'); button.type = 'button'; button.textContent = '查看卡片 ↓';
  button.addEventListener('click', () => jump(point.dataset.id!));
  content.append(summary, button); tooltip.show(point, content);
}
points.forEach(point => {
  let touch = false;
  point.addEventListener('pointerdown', e => { touch = e.pointerType === 'touch' || matchMedia('(pointer: coarse)').matches; });
  point.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch' && !matchMedia('(pointer: coarse)').matches) preview(point); });
  point.addEventListener('focus', () => {
    if (!touch) requestAnimationFrame(() => { if (document.activeElement === point) preview(point); });
  });
  point.addEventListener('click', e => {
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); show(point);
    if (touch && !tooltip.isOpen(point)) preview(point);
    else jump(point.dataset.id!);
    touch = false;
  });
  point.addEventListener('keydown', e => {
    if (e.key === ' ') { e.preventDefault(); preview(point); }
    if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey) {
      e.preventDefault(); show(point); jump(point.dataset.id!);
    }
  });
});
window.addEventListener('hashchange', jumpHash);
requestAnimationFrame(jumpHash);
const scroller = document.querySelector<HTMLElement>('.timeline-scroll')!;
function scrollHint() {
  scroller.parentElement!.classList.toggle('has-overflow', scroller.scrollWidth > scroller.clientWidth);
}
requestAnimationFrame(() => { scrollHint(); if (scroller.scrollWidth > scroller.clientWidth) scroller.scrollLeft = scroller.scrollWidth; });
new ResizeObserver(scrollHint).observe(scroller);
toggle.addEventListener('change', () => {
  tooltip.close();
  document.querySelector('.lane-chart')!.classList.toggle('show-all', toggle.checked);
  const shown = points.filter(p => toggle.checked || ['S','A'].includes(p.dataset.impact!));
  document.querySelector('#timeline-count')!.textContent = `当前显示 ${shown.length} 条`;
  if (points.some(p => p.classList.contains('selected') && !shown.includes(p))) {
    panel.textContent = '悬停、聚焦或点击圆点查看事件详情。';
    points.forEach(p => p.classList.remove('selected'));
  }
});
async function loadCharts() {
  document.querySelectorAll('.chart').forEach(el => { el.textContent = '图表加载中…'; el.classList.add('loading'); el.setAttribute('aria-busy', 'true'); });
  try {
    const { renderCharts } = await import('./charts');
    renderCharts(JSON.parse(document.querySelector('#chart-data')!.textContent!), {onFilter:applyFilter});
  } catch {
    document.querySelectorAll('.chart').forEach(el => { el.textContent = '图表加载失败，请查看下方数据表。'; });
  } finally {
    document.querySelectorAll('.chart').forEach(el => { el.classList.remove('loading'); el.removeAttribute('aria-busy'); });
  }
}
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(e => e.isIntersecting)) return;
    observer.disconnect(); void loadCharts();
  }, { rootMargin: '150px' });
  document.querySelectorAll('.chart').forEach(el => observer.observe(el));
} else { void loadCharts(); }
