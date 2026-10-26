const form = document.querySelector<HTMLFormElement>('#filters')!;
form.hidden = false;
form.addEventListener('submit', e => e.preventDefault());
form.addEventListener('input', () => {
  const values = new FormData(form);
  let count = 0;
  document.querySelectorAll<HTMLElement>('.timeline .event').forEach(item => {
    const { impact, category, orgs, search } = item.dataset;
    const match = (!values.get('impact') || values.get('impact') === impact)
      && (!values.get('category') || values.get('category') === category)
      && (!values.get('org') || JSON.parse(orgs!).includes(values.get('org')))
      && search!.includes(String(values.get('keyword') ?? '').trim().toLowerCase());
    item.hidden = !match;
    if (match) count++;
  });
  document.querySelector('#results')!.textContent = count ? `显示 ${count} 条事件` : '没有符合条件的事件，请调整筛选。';
});
const observer = new IntersectionObserver(async entries => {
  if (!entries.some(e => e.isIntersecting)) return;
  observer.disconnect();
  try {
    const { renderCharts } = await import('./charts');
    renderCharts(JSON.parse(document.querySelector('#chart-data')!.textContent!));
  } catch {
    document.querySelector('#heatmap')!.textContent = '图表加载失败，请查看下方数据表。';
  }
}, { rootMargin: '150px' });
observer.observe(document.querySelector('#heatmap')!);
