(function () {
  // ---------- Theme toggle ----------
  const toggle = document.querySelector('[data-theme-toggle]');
  const root = document.documentElement;
  let theme = matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
  root.setAttribute('data-theme', theme);
  updateToggleIcon();

  toggle.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', theme);
    updateToggleIcon();
  });

  function updateToggleIcon() {
    toggle.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
    toggle.innerHTML = theme === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }

  // ---------- State ----------
  let qc = { verified: [], rejected_or_pending: [] };
  let diyData = { intro: '', steps: [] };
  let mode = 'pro';
  let query = '';

  const verifiedGrid = document.getElementById('verified-grid');
  const pendingGrid = document.getElementById('pending-grid');
  const verifiedCount = document.getElementById('verified-count');
  const pendingCount = document.getElementById('pending-count');
  const statRow = document.getElementById('stat-row');
  const searchInput = document.getElementById('search-input');
  const modeProBtn = document.getElementById('mode-pro');
  const modeDiyBtn = document.getElementById('mode-diy');

  Promise.all([
    fetch('qc_data.json').then(r => r.json()),
    fetch('diy_data.json').then(r => r.json())
  ]).then(([qcJson, diyJson]) => {
    qc = qcJson;
    diyData = diyJson;
    renderStats();
    render();
  }).catch(err => {
    verifiedGrid.innerHTML = '<div class="empty-state"><p>Could not load diagnostic data. ' + err + '</p></div>';
  });

  function renderStats() {
    statRow.innerHTML = `
      <div class="stat"><span class="stat-num verified">${qc.verified.length}</span><span class="stat-label">Verified claims</span></div>
      <div class="stat"><span class="stat-num pending">${qc.rejected_or_pending.length}</span><span class="stat-label">Pending sources</span></div>
      <div class="stat"><span class="stat-num">3+</span><span class="stat-label">Domains required</span></div>
    `;
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function matchesQuery(text) {
    if (!query) return true;
    return text.toLowerCase().includes(query.toLowerCase());
  }

  function domainOf(url) {
    try { return new URL(url).hostname.replace('www.', ''); } catch (e) { return url; }
  }

  function render() {
    if (mode === 'pro') { renderProVerified(); renderProPending(); }
    else { renderDiy(); }
  }

  // ---------- PRO MODE ----------
  function renderProVerified() {
    const items = qc.verified.filter(f => matchesQuery(f.statement + ' ' + f.fact_id + ' ' + f.category));
    verifiedCount.textContent = items.length + ' / ' + qc.verified.length;

    if (!items.length) {
      verifiedGrid.innerHTML = emptyState('No verified claims match your search.');
      return;
    }

    verifiedGrid.innerHTML = items.map(f => `
      <article class="fact-card verified-card">
        <div class="fact-top">
          <span class="fact-id">${escapeHtml(f.fact_id)}</span>
          <div class="badge-row">
            <span class="badge category">${escapeHtml(f.category)}</span>
            <span class="badge status-verified">Verified</span>
            <span class="badge confidence">${escapeHtml(f.confidence)} confidence</span>
          </div>
        </div>
        <p class="fact-statement">${escapeHtml(f.statement)}</p>
        ${f.numeric_range ? numericCallout(f.numeric_range) : ''}
        <div class="fact-meta">
          <span class="corroboration">${f.independent_domain_count} independent domain${f.independent_domain_count === 1 ? '' : 's'} · ${escapeHtml(f.notes || '')}</span>
        </div>
        <details class="citations">
          <summary>${f.citations.length} source${f.citations.length === 1 ? '' : 's'}</summary>
          <ul>
            ${f.citations.map(u => `<li><a href="${escapeHtml(u)}" target="_blank" rel="noopener">${escapeHtml(domainOf(u))} — ${escapeHtml(u)}</a></li>`).join('')}
          </ul>
        </details>
      </article>
    `).join('');
  }

  function renderProPending() {
    const items = qc.rejected_or_pending.filter(f => matchesQuery(f.statement + ' ' + f.fact_id + ' ' + f.category));
    pendingCount.textContent = items.length + ' / ' + qc.rejected_or_pending.length;

    if (!items.length) {
      const msg = qc.rejected_or_pending.length === 0
        ? 'Nothing pending right now \u2014 every gathered claim in this domain cleared the 3-domain corroboration bar.'
        : 'No pending claims match your search.';
      pendingGrid.innerHTML = emptyState(msg);
      return;
    }

    pendingGrid.innerHTML = items.map(f => `
      <article class="fact-card pending">
        <div class="fact-top">
          <span class="fact-id">${escapeHtml(f.fact_id)}</span>
          <div class="badge-row">
            <span class="badge category">${escapeHtml(f.category)}</span>
            <span class="badge status-pending">${escapeHtml(f.status.replace(/_/g, ' '))}</span>
          </div>
        </div>
        <p class="fact-statement">${escapeHtml(f.statement)}</p>
        <div class="pending-note">Only ${f.independent_domain_count} independent domain${f.independent_domain_count === 1 ? '' : 's'} found (needs 3+). Not used in any report until this clears.</div>
        <details class="citations">
          <summary>${f.citations.length} source${f.citations.length === 1 ? '' : 's'} so far</summary>
          <ul>
            ${f.citations.map(u => `<li><a href="${escapeHtml(u)}" target="_blank" rel="noopener">${escapeHtml(domainOf(u))} — ${escapeHtml(u)}</a></li>`).join('')}
          </ul>
        </details>
      </article>
    `).join('');
  }

  function numericCallout(range) {
    const parts = [];
    if (range.min != null && range.max != null) parts.push(`${range.min}–${range.max} ${range.unit || ''}`.trim());
    if (range.absolute_max_before_fault != null) parts.push(`fault above ${range.absolute_max_before_fault} ${range.unit || ''}`.trim());
    return `<div class="numeric-callout">⚡ ${escapeHtml(parts.join(' · '))}</div>`;
  }

  function emptyState(msg) {
    return `<div class="empty-state"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg><p>${escapeHtml(msg)}</p></div>`;
  }

  // ---------- DIY MODE ----------
  function renderDiy() {
    const steps = diyData.steps.filter(s => matchesQuery(s.title + ' ' + s.body));
    verifiedCount.textContent = steps.length + ' / ' + diyData.steps.length;
    pendingCount.textContent = qc.rejected_or_pending.length;

    document.querySelector('#verified-grid').previousElementSibling.querySelector('h2').textContent = 'Roadside quick guide';

    if (!steps.length) {
      verifiedGrid.innerHTML = emptyState('No steps match your search.');
    } else {
      verifiedGrid.innerHTML = `<p style="color:var(--color-text-muted);margin-bottom:var(--space-4);">${escapeHtml(diyData.intro)}</p>` +
        steps.map(s => `
        <article class="fact-card verified-card">
          <div class="fact-top">
            <span class="fact-id">STEP ${s.step}</span>
            <span class="badge status-verified">Verified</span>
          </div>
          <p class="fact-statement diy">${escapeHtml(s.title)}</p>
          <p style="color:var(--color-text-muted);">${escapeHtml(s.body)}</p>
        </article>
      `).join('');
    }

    const pendingItems = qc.rejected_or_pending.filter(f => matchesQuery(f.statement));
    pendingGrid.innerHTML = pendingItems.length
      ? pendingItems.map(f => `
        <article class="fact-card pending">
          <div class="fact-top">
            <span class="fact-id">${escapeHtml(f.category)}</span>
            <span class="badge status-pending">Not confirmed enough yet</span>
          </div>
          <p class="fact-statement">${escapeHtml(f.statement)}</p>
          <div class="pending-note">We're not teaching this one to the network yet — needs one more independent source to confirm it.</div>
        </article>
      `).join('')
      : emptyState('Nothing pending right now — every gathered claim in this domain is verified.');
  }

  // ---------- Controls ----------
  searchInput.addEventListener('input', e => { query = e.target.value; render(); });

  modeProBtn.addEventListener('click', () => {
    mode = 'pro'; modeProBtn.setAttribute('aria-pressed', 'true'); modeDiyBtn.setAttribute('aria-pressed', 'false');
    document.querySelector('#verified-grid').previousElementSibling.querySelector('h2').textContent = 'Verified claims';
    render();
  });
  modeDiyBtn.addEventListener('click', () => {
    mode = 'diy'; modeDiyBtn.setAttribute('aria-pressed', 'true'); modeProBtn.setAttribute('aria-pressed', 'false');
    render();
  });
})();
