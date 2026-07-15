(() => {
  const body = document.body;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const setTheme = (theme) => {
    body.dataset.theme = theme;
    localStorage.setItem('unitAdminTheme', theme);
    $$('.theme-swatch').forEach((button) => button.classList.toggle('active', button.dataset.theme === theme));
    const picker = $('#themePicker');
    if (picker) picker.value = theme;
  };

  setTheme(localStorage.getItem('unitAdminTheme') || 'command');

  $('#themePicker')?.addEventListener('change', (event) => setTheme(event.target.value));
  $$('.theme-swatch').forEach((button) => button.addEventListener('click', () => setTheme(button.dataset.theme)));

  const shell = $('.app-shell');
  const sidebarToggle = $('#sidebarToggle');
  const savedCollapsed = localStorage.getItem('unitAdminSidebarCollapsed') === 'true';
  shell?.classList.toggle('sidebar-collapsed', savedCollapsed);
  sidebarToggle?.addEventListener('click', () => {
    shell.classList.toggle('sidebar-collapsed');
    localStorage.setItem('unitAdminSidebarCollapsed', shell.classList.contains('sidebar-collapsed'));
  });

  const closePanels = (except) => {
    $$('.floating-panel.open').forEach((panel) => {
      if (panel !== except) panel.classList.remove('open');
    });
  };

  $$('[data-panel-target]').forEach((button) => {
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      const panel = document.getElementById(button.dataset.panelTarget);
      const shouldOpen = !panel.classList.contains('open');
      closePanels(panel);
      panel.classList.toggle('open', shouldOpen);
    });
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.floating-panel') && !event.target.closest('[data-panel-target]')) closePanels();
  });

  $$('.count-up').forEach((element) => {
    const target = Number(element.dataset.value || element.textContent || 0);
    const duration = 700;
    const start = performance.now();
    const animate = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      element.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  });

  $$('.progress-fill').forEach((bar) => requestAnimationFrame(() => { bar.style.width = `${bar.dataset.percent || 0}%`; }));

  const slides = $$('.hero-slide');
  const dots = $$('.hero-dot');
  let slideIndex = 0;
  const showSlide = (index) => {
    if (!slides.length) return;
    slideIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle('active', i === slideIndex));
    dots.forEach((dot, i) => dot.classList.toggle('active', i === slideIndex));
  };
  dots.forEach((dot, index) => dot.addEventListener('click', () => showSlide(index)));
  if (slides.length > 1) setInterval(() => showSlide(slideIndex + 1), 6000);

  $$('.interactive-card[data-href]').forEach((card) => {
    card.tabIndex = 0;
    const open = () => { window.location.href = card.dataset.href; };
    card.addEventListener('click', open);
    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') open();
    });
  });

  $$('.tab-button').forEach((button) => {
    button.addEventListener('click', () => {
      const parent = button.closest('.dashboard-widget');
      $$('.tab-button', parent).forEach((item) => item.classList.remove('active'));
      $$('.tab-pane', parent).forEach((pane) => pane.classList.remove('active'));
      button.classList.add('active');
      $(`#${button.dataset.tab}`, parent)?.classList.add('active');
    });
  });

  const clock = $('#liveClock');
  if (clock) {
    const updateClock = () => {
      const now = new Date();
      clock.textContent = now.toLocaleString([], { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };
    updateClock();
    setInterval(updateClock, 1000);
  }
})();