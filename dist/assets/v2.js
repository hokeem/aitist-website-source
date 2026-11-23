(() => {
  const nav = document.querySelector('.nav');
  if (nav) {
    const links = nav.querySelector('nav');
    const controls = nav.querySelector('.nav-right');
    if (links && controls) {
      const zh = document.documentElement.lang.startsWith('zh');
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'nav-toggle';
      links.id = 'primary-navigation';
      toggle.setAttribute('aria-controls', links.id);
      toggle.setAttribute('aria-expanded', 'false');
      const close = (restoreFocus = false) => {
        nav.classList.remove('menu-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = zh ? '菜单' : 'Menu';
        if (restoreFocus) toggle.focus();
      };
      toggle.addEventListener('click', () => {
        if (nav.classList.contains('menu-open')) close();
        else {
          nav.classList.add('menu-open');
          toggle.setAttribute('aria-expanded', 'true');
          toggle.textContent = zh ? '关闭' : 'Close';
          links.querySelector('a')?.focus();
        }
      });
      links.addEventListener('click', e => { if (e.target.closest('a')) close(); });
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && nav.classList.contains('menu-open')) close(true);
      });
      document.addEventListener('click', e => { if (!nav.contains(e.target)) close(); });
      nav.addEventListener('focusout', () => {
        requestAnimationFrame(() => { if (!nav.contains(document.activeElement)) close(); });
      });
      matchMedia('(max-width:1100px)').addEventListener('change', () => close());
      controls.append(toggle);
      nav.classList.add('nav-enhanced');
      close();
    }
  }
  document.querySelectorAll('.tbl-wrap, .code pre, .art-fig').forEach(el => {
    el.tabIndex = 0;
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', document.documentElement.lang.startsWith('zh') ? '可横向滚动的内容' : 'Horizontally scrollable content');
  });
  const onScroll = () => nav.classList.toggle('scrolled', scrollY > 24);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) { items.forEach(el => el.classList.add('in')); return; }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  items.forEach((el, i) => {
    const sib = [...el.parentElement.children].filter(c => c.classList.contains('reveal'));
    el.style.transitionDelay = `${Math.min(sib.indexOf(el), 4) * 90}ms`;
    io.observe(el);
  });
})();
