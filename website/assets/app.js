(() => {
  const buttons = Array.from(document.querySelectorAll('[data-section]'));
  const content = document.getElementById('content');
  const loader = document.querySelector('.content-pane__loader');
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const body = document.body;
  const cache = new Map();
  const storageKey = 'sapl-theme';
  let toast;
  let toastTimer;

  function ensureToast() {
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      toast.setAttribute('role', 'status');
      document.body.appendChild(toast);
    }
    return toast;
  }

  function showToast(message) {
    const node = ensureToast();
    node.textContent = message;
    node.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
      node.classList.remove('is-visible');
    }, 2400);
  }

  function showLoader() {
    if (!loader || !content) return;
    loader.hidden = false;
    content.setAttribute('aria-busy', 'true');
  }

  function hideLoader() {
    if (!loader || !content) return;
    loader.hidden = true;
    content.setAttribute('aria-busy', 'false');
  }

  function setActiveButton(activeButton) {
    buttons.forEach((button) => {
      const isActive = button === activeButton;
      button.classList.toggle('active', isActive);
      button.setAttribute('aria-selected', String(isActive));
      button.setAttribute('aria-pressed', String(isActive));
      if (isActive && content) {
        content.setAttribute('aria-labelledby', button.id);
      }
    });
  }

  async function fetchSection(path) {
    if (cache.has(path)) {
      return cache.get(path);
    }

    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`Failed to load ${path}`);
    }
    const markup = await response.text();
    cache.set(path, markup);
    return markup;
  }

  function enhanceCodeBlocks(scope) {
    if (!scope) return;
    const blocks = scope.querySelectorAll('pre[data-interactive]');
    blocks.forEach((pre) => {
      if (pre.dataset.enhanced === 'true' || !pre.parentElement) {
        return;
      }
      const parent = pre.parentElement;
      const wrapper = document.createElement('div');
      wrapper.className = 'code-suite';
      if (pre.dataset.wrap === 'true') {
        wrapper.classList.add('is-wrapped');
      }

      const toolbar = document.createElement('div');
      toolbar.className = 'code-suite__toolbar';

      const meta = document.createElement('span');
      meta.className = 'code-suite__meta';
      const language = pre.dataset.language ? pre.dataset.language.toUpperCase() : 'CODE';
      meta.textContent = `${language} SANDBOX`;

      const actions = document.createElement('div');
      actions.className = 'code-suite__actions';

      const copyButton = document.createElement('button');
      copyButton.type = 'button';
      copyButton.textContent = 'Copy';
      copyButton.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(pre.textContent.trim());
          showToast('Snippet copied');
        } catch (error) {
          console.error('Clipboard error', error);
          showToast('Copy failed');
        }
      });

      const wrapButton = document.createElement('button');
      wrapButton.type = 'button';
      wrapButton.textContent = 'Unwrap';
      wrapButton.addEventListener('click', () => {
        const isWrapped = wrapper.classList.toggle('is-wrapped');
        wrapButton.textContent = isWrapped ? 'Unwrap' : 'Wrap';
      });
      wrapButton.textContent = wrapper.classList.contains('is-wrapped') ? 'Unwrap' : 'Wrap';

      const runButton = document.createElement('button');
      runButton.type = 'button';
      runButton.textContent = 'Run';
      runButton.addEventListener('click', () => {
        runSandbox(pre, wrapper);
      });

      actions.append(copyButton, wrapButton, runButton);
      toolbar.append(meta, actions);

      parent.insertBefore(wrapper, pre);
      wrapper.append(toolbar, pre);
      pre.dataset.enhanced = 'true';
    });
  }

  function runSandbox(pre, wrapper) {
    const command = pre.dataset.command || 'sapl run demo.playbook';
    const output = pre.dataset.output || '⚠️ No simulated output provided.';
    let consoleEl = wrapper.querySelector('.code-suite__console');
    if (!consoleEl) {
      consoleEl = document.createElement('div');
      consoleEl.className = 'code-suite__console';
      wrapper.appendChild(consoleEl);
    }

    consoleEl.innerHTML = '';
    consoleEl.classList.add('is-running');

    const heading = document.createElement('strong');
    heading.textContent = 'Sandbox terminal';
    const commandLine = document.createElement('code');
    commandLine.textContent = `$ ${command}`;
    const outputNode = document.createElement('pre');
    outputNode.textContent = '';

    consoleEl.append(heading, commandLine, outputNode);

    window.setTimeout(() => {
      consoleEl.classList.remove('is-running');
      outputNode.textContent = output;
      showToast('Sandbox executed');
    }, 500);
  }

  async function renderSection(button, pushHash = true) {
    if (!button || !content) return;
    const path = button.dataset.section;
    const slug = button.dataset.slug;

    showLoader();
    try {
      const markup = await fetchSection(path);
      content.innerHTML = markup;
      enhanceCodeBlocks(content);
      setActiveButton(button);
      if (pushHash && slug) {
        history.replaceState(null, '', `#${slug}`);
      }
      requestAnimationFrame(() => {
        const firstHeading = content.querySelector('h2');
        if (firstHeading) {
          firstHeading.setAttribute('tabindex', '-1');
          try {
            firstHeading.focus({ preventScroll: false });
          } catch (err) {
            firstHeading.focus();
          }
          firstHeading.addEventListener(
            'blur',
            () => firstHeading.removeAttribute('tabindex'),
            { once: true }
          );
        } else {
          try {
            content.focus({ preventScroll: false });
          } catch (err) {
            content.focus();
          }
        }
      });
    } catch (error) {
      content.innerHTML = `<article class="prose"><h2>Unable to load content</h2><p>${error.message}</p></article>`;
      console.error(error);
    } finally {
      hideLoader();
    }
  }

  function prefetch(button) {
    const path = button.dataset.section;
    if (!path || cache.has(path) || button.dataset.prefetched === 'true') {
      return;
    }
    fetchSection(path).catch(() => {
      /* Ignore prefetch errors */
    });
    button.dataset.prefetched = 'true';
  }

  function getButtonBySlug(slug) {
    return buttons.find((button) => button.dataset.slug === slug);
  }

  function activateFromHash(initial = false) {
    if (buttons.length === 0) return;
    const slug = window.location.hash.replace('#', '') || 'overview';
    const button = getButtonBySlug(slug) || buttons[0];
    renderSection(button, false);
    if (!window.location.hash && initial && button.dataset.slug) {
      history.replaceState(null, '', `#${button.dataset.slug}`);
    }
  }

  buttons.forEach((button) => {
    button.setAttribute('aria-selected', 'false');
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => renderSection(button));
    button.addEventListener('mouseenter', () => prefetch(button));
    button.addEventListener('focus', () => prefetch(button));
  });

  const nav = document.querySelector('.site-nav');
  if (nav) {
    nav.addEventListener('keydown', (event) => {
      const currentIndex = buttons.indexOf(document.activeElement);
      if (currentIndex === -1) {
        return;
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        const next = buttons[(currentIndex + 1) % buttons.length];
        next.focus();
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        const prev = buttons[(currentIndex - 1 + buttons.length) % buttons.length];
        prev.focus();
      } else if (event.key === 'Home') {
        event.preventDefault();
        buttons[0].focus();
      } else if (event.key === 'End') {
        event.preventDefault();
        buttons[buttons.length - 1].focus();
      }
    });
  }

  window.addEventListener('hashchange', () => activateFromHash());

  function applyTheme(theme) {
    if (!theme) return;
    body.dataset.theme = theme;
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(theme === 'light'));
      const icon = themeToggle.querySelector('.theme-toggle__icon');
      if (icon) {
        icon.textContent = theme === 'light' ? '☀️' : '🌙';
      }
    }
  }

  function resolveInitialTheme() {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      return stored;
    }
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function toggleTheme() {
    const nextTheme = body.dataset.theme === 'light' ? 'dark' : 'light';
    applyTheme(nextTheme);
    localStorage.setItem(storageKey, nextTheme);
  }

  if (themeToggle) {
    applyTheme(resolveInitialTheme());
    themeToggle.addEventListener('click', toggleTheme);
    const media = window.matchMedia('(prefers-color-scheme: light)');
    media.addEventListener('change', (event) => {
      if (!localStorage.getItem(storageKey)) {
        applyTheme(event.matches ? 'light' : 'dark');
      }
    });
  }

  const currentYear = new Date().getFullYear();
  const yearTarget = document.getElementById('copyright-year');
  if (yearTarget) {
    yearTarget.textContent = String(currentYear);
  }

  enhanceCodeBlocks(content);
  activateFromHash(true);
})();
