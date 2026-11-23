const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const illustration = document.querySelector('.articleart');
const layers = illustration?.querySelectorAll('.layer');
if (layers?.length) {
  illustration.addEventListener('pointermove', event => {
    if (reducedMotion.matches || event.pointerType === 'touch') return;
    const rect = illustration.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - .5;
    const y = (event.clientY - rect.top) / rect.height - .5;
    layers.forEach((layer, index) => {
      layer.style.setProperty('--dx', `${x * (index + 1) * 11}px`);
      layer.style.setProperty('--dy', `${y * (index + 1) * 8}px`);
    });
  });
  illustration.addEventListener('pointerleave', () => layers.forEach(layer => {
    layer.style.removeProperty('--dx');
    layer.style.removeProperty('--dy');
  }));
}
const contents = [...document.querySelectorAll('.reading aside a')];
if (contents.length) {
  const observer = new IntersectionObserver(entries => {
    const visible = entries.find(entry => entry.isIntersecting);
    if (!visible) return;
    contents.forEach(link => {
      if (link.hash === '#' + visible.target.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-12% 0px -65% 0px' });
  contents.forEach(link => observer.observe(document.querySelector(link.hash)));
}
