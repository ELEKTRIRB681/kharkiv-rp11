document.addEventListener('DOMContentLoaded', () => {
  const statusEl = document.getElementById('status');
  const joinBtns = [document.getElementById('joinBtn'), document.getElementById('heroJoin')].filter(Boolean);

  // Static status for public hosting
  function setStaticStatus(){
    if(!statusEl) return;
    statusEl.textContent = 'Статус: Онлайн (Kharkiv RP активний)';
    statusEl.classList.add('status-online');
  }

  async function fetchRules(){
    try{
      const API_BASE = window.location.origin + '/api';
      const res = await fetch(`${API_BASE}/rules`);
      const rules = await res.json();
      renderRules(rules);
    }catch(e){
      document.getElementById('rulesList').textContent = 'Помилка завантаження правил.';
    }
  }

  function renderRules(rules){
    const container = document.getElementById('rulesList');
    container.innerHTML = '';
    rules.forEach(rule => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="card-head">
          <h4>${rule.title}</h4>
          <div class="chev">▸</div>
        </div>
        <div class="card-body">
          ${rule.items.map(i=>`<div class="item"><strong>${i.id}</strong> — ${i.text}</div>`).join('')}
        </div>
      `;
      card.querySelector('.card-head').addEventListener('click', () => {
        card.classList.toggle('open');
      });
      container.appendChild(card);
    });
  }

  // Search filter
  const search = document.getElementById('rulesSearch');
  let rulesCache = null;
  async function loadAndCacheRules(){
    if(!rulesCache){
      const res = await fetch('/api/rules');
      rulesCache = await res.json();
    }
    return rulesCache;
  }

  search.addEventListener('input', async (e) => {
    const q = e.target.value.trim().toLowerCase();
    const rules = await loadAndCacheRules();
    if(!q){
      renderRules(rules);return;
    }
    const filtered = rules.map(r=>{
      const items = r.items.filter(i=> (i.text + ' ' + i.id).toLowerCase().includes(q));
      return {...r, items};
    }).filter(r=>r.items.length>0);
    renderRules(filtered);
    // auto-open matches
    document.querySelectorAll('.card').forEach(c=>c.classList.add('open'));
  });

  // Join buttons: ensure they open the Roblox share URL in a new tab
  const ROBLOX_SHARE = 'https://roblox.com/share?code=5ihdm3h6w8n7dq&v=v2';
  joinBtns.forEach(b=>{
    if(!b) return;
    if(b.tagName === 'A'){
      b.setAttribute('href', ROBLOX_SHARE);
      b.setAttribute('target', '_blank');
      b.setAttribute('rel', 'noopener noreferrer');
    } else {
      b.addEventListener('click', ()=>{
        window.open(ROBLOX_SHARE, '_blank', 'noopener');
      });
    }
  });

  // Init constitution accordion (for static public/index.html)
  function initConstitutionAccordion(){
    document.querySelectorAll('.constit-card .card-head').forEach(head=>{
      const card = head.closest('.constit-card');
      head.addEventListener('click', ()=>{
        // close others
        document.querySelectorAll('.constit-card.open').forEach(c=>{ if(c!==card) c.classList.remove('open'); });
        card.classList.toggle('open');
      });
    });
  }
  initConstitutionAccordion();

  setStaticStatus();
  fetchRules();
});
