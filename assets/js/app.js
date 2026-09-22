/* JKCORP frontend enhancements: language/theme persistence and API-ready contact form. */
(() => {
  'use strict';
  const API_URL = (window.JKCORP_CONFIG && window.JKCORP_CONFIG.apiUrl) || '';
  const body = document.body;
  const languageButtons = document.querySelectorAll('.lang-btn');
  const themeButtons = document.querySelectorAll('.theme-btn');
  const translations = window.JKCORP_TRANSLATIONS || {};
  const language = localStorage.getItem('jkcorp_lang') || 'gu';
  const theme = localStorage.getItem('jkcorp_theme') || 'ocean';

  function setTheme(value) {
    body.dataset.theme = value;
    themeButtons.forEach((button) => button.classList.toggle('active', button.dataset.theme === value));
    localStorage.setItem('jkcorp_theme', value);
  }

  function setLanguage(value) {
    const dictionary = translations[value] || {};
    document.documentElement.lang = value;
    document.querySelectorAll('[data-i18n]').forEach((element) => {
      const text = dictionary[element.dataset.i18n];
      if (text) element.textContent = text;
    });
    languageButtons.forEach((button) => button.classList.toggle('active', button.dataset.lang === value));
    localStorage.setItem('jkcorp_lang', value);
  }

  themeButtons.forEach((button) => button.addEventListener('click', () => setTheme(button.dataset.theme)));
  languageButtons.forEach((button) => button.addEventListener('click', () => setLanguage(button.dataset.lang)));
  setTheme(theme);
  setLanguage(language);

  const menuButton = document.getElementById('hamburger');
  const nav = document.getElementById('mainnav');
  menuButton?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => nav.classList.remove('open')));

  document.querySelectorAll('.faq-question').forEach((button) => button.addEventListener('click', () => {
    const item = button.closest('.faq-item');
    const expanded = item.classList.toggle('open');
    button.setAttribute('aria-expanded', String(expanded));
  }));

  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');
  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const phone = String(data.phone || '').replace(/\s/g, '');
    const dictionary = translations[document.documentElement.lang] || translations.gu || {};
    if (!/^\+?[0-9-]{7,15}$/.test(phone)) {
      status.textContent = dictionary.invalidPhone || 'Please enter a valid phone number.';
      status.className = 'form-status error';
      return;
    }
    status.textContent = dictionary.sending || 'Sending...';
    status.className = 'form-status';
    try {
      if (!API_URL) throw new Error('API URL is not configured');
      const response = await fetch(`${API_URL.replace(/\/$/, '')}/api/inquiries`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Request failed');
      form.reset();
      status.textContent = dictionary.formSuccess || 'Your inquiry was sent successfully.';
      status.className = 'form-status success';
    } catch (error) {
      const bodyText = [`Name: ${data.name}`, `Phone: ${data.phone}`, `Service: ${data.service}`, `Message: ${data.message || ''}`].join('\n');
      window.location.href = `mailto:jkcorpofficial@gmail.com?subject=${encodeURIComponent('New JKCORP service inquiry')}&body=${encodeURIComponent(bodyText)}`;
      status.textContent = dictionary.mailFallback || 'Your email app will open to send the inquiry.';
      status.className = 'form-status success';
    }
  });

  const back = document.getElementById('backToTop');
  window.addEventListener('scroll', () => back?.classList.toggle('show', window.scrollY > 240), { passive: true });
  back?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
})();
