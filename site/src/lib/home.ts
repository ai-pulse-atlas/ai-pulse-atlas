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
  if (sync) {
    const url = new URL(location.href);
    fields.forEach(name => values[name] ? url.searchParams.set(name, values[name]) : url.searchParams.delete(name));
    history.replaceState(null, '', url.pathname + url.search + url.hash);
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
const panel = document.querySelector<HTMLElement>('#timeline-detail')!;
const templates = new Map([...document.querySelectorAll<HTMLTemplateElement>('template[data-detail]')].map(t => [t.dataset.detail, t]));
function show(point: SVGAElement) {
  const template = templates.get(point.dataset.id);
  if (!template) return;
  points.forEach(p => p.classList.toggle('selected', p === point));
  panel.replaceChildren(template.content.cloneNode(true));
}
points.forEach(point => {
  point.addEventListener('mouseenter', () => show(point));
  point.addEventListener('focus', () => show(point));
  point.addEventListener('click', e => { if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return; e.preventDefault(); show(point); });
  point.addEventListener('keydown', e => { if (e.key === ' ') { e.preventDefault(); show(point); } });
});
toggle.addEventListener('change', () => {
  document.querySelector('.lane-chart')!.classList.toggle('show-all', toggle.checked);
  const shown = points.filter(p => toggle.checked || ['S','A'].includes(p.dataset.impact!));
  document.querySelector('#timeline-count')!.textContent = `当前显示 ${shown.length} 条`;
  if (points.some(p => p.classList.contains('selected') && !shown.includes(p))) {
    panel.textContent = '悬停、聚焦或点击圆点查看事件详情。';
    points.forEach(p => p.classList.remove('selected'));
  }
});
async function loadCharts() {
  try {
    const { renderCharts } = await import('./charts');
    renderCharts(JSON.parse(document.querySelector('#chart-data')!.textContent!));
  } catch {
    document.querySelectorAll('.chart').forEach(el => { el.textContent = '图表加载失败，请查看下方数据表。'; });
  }
}
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    if (!entries.some(e => e.isIntersecting)) return;
    observer.disconnect(); void loadCharts();
  }, { rootMargin: '150px' });
  document.querySelectorAll('.chart').forEach(el => observer.observe(el));
} else { void loadCharts(); }
