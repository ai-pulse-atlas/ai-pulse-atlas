export function createTooltip() {
  const tip = document.createElement('div');
  tip.id = 'pulse-tip'; tip.className = 'pulse-tip'; tip.role = 'tooltip'; tip.hidden = true;
  document.body.append(tip);
  let target: Element | undefined;
  let previousDescription: string | null = null;
  function close() {
    if (target) {
      if (previousDescription === null) target.removeAttribute('aria-describedby');
      else target.setAttribute('aria-describedby', previousDescription);
    }
    target = undefined; tip.hidden = true;
  }
  function position() {
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const width = document.documentElement.clientWidth;
    const height = window.innerHeight;
    const box = tip.getBoundingClientRect();
    tip.style.left = `${Math.max(8, Math.min(width - box.width - 8, rect.left + rect.width / 2 - box.width / 2))}px`;
    const below = rect.bottom + 10;
    tip.style.top = `${Math.max(8, Math.min(height - box.height - 8, below + box.height <= height - 8 ? below : rect.top - box.height - 10))}px`;
  }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  document.addEventListener('pointerdown', e => {
    if (e.target instanceof Node && !tip.contains(e.target) && !target?.contains(e.target)) close();
  });
  document.addEventListener('scroll', e => { if (e.target !== tip) close(); }, true);
  window.addEventListener('resize', close);
  return {
    close,
    isOpen: (element: Element) => !tip.hidden && target === element,
    show(element: Element, content: DocumentFragment) {
      close(); target = element;
      previousDescription = target.getAttribute('aria-describedby');
      target.setAttribute('aria-describedby', [previousDescription, tip.id].filter(Boolean).join(' '));
      tip.replaceChildren(content); tip.hidden = false; position();
    },
  };
}
