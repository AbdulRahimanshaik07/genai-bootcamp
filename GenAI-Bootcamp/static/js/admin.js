const modal = document.getElementById('eventModal');
const addBtn = document.getElementById('addEventBtn');
const cancelBtn = document.getElementById('cancelModal');
const saveBtn = document.getElementById('saveEvent');
const list = document.getElementById('eventsList');

let editingId = null;

function openModal(ev){
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  if (ev){
    document.getElementById('evTitle').value = ev.title || '';
    document.getElementById('evType').value = ev.type || 'Gen AI';
    document.getElementById('evStart').value = ev.startDate || '';
    document.getElementById('evEnd').value = ev.endDate || '';
    document.getElementById('evLocation').value = ev.location || '';
  } else {
    document.getElementById('evTitle').value = '';
    document.getElementById('evType').value = 'Gen AI';
    document.getElementById('evStart').value = '';
    document.getElementById('evEnd').value = '';
    document.getElementById('evLocation').value = '';
  }
}
function closeModal(){
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

addBtn && addBtn.addEventListener('click',()=>{ editingId=null; openModal(null); });
cancelBtn && cancelBtn.addEventListener('click', closeModal);

list && list.addEventListener('click', (e)=>{
  const row = e.target.closest('[data-id]');
  if (!row) return;
  const id = row.getAttribute('data-id');
  if (e.target.classList.contains('edit-ev')){
    editingId = id;
    const info = row.querySelector('div');
    const title = info.querySelector('.font-semibold')?.textContent?.trim().split(' (')[0];
    const meta = info.querySelector('.text-slate-600')?.textContent || '';
    const [datePart, , location] = meta.split('•').map(s=>s.trim());
    const [start, end] = (datePart || '').split('–').map(s=>s.trim());
    openModal({ title, startDate:start, endDate:end, location });
  }
  if (e.target.classList.contains('delete-ev')){
    if (!confirm('Delete this event?')) return;
    fetch(`/api/admin/events/${id}`, { method:'DELETE' })
      .then(r=>r.json())
      .then(()=> location.reload())
      .catch(()=> alert('Delete failed'));
  }
});

saveBtn && saveBtn.addEventListener('click', async ()=>{
  const payload = {
    title: document.getElementById('evTitle').value.trim(),
    type: document.getElementById('evType').value.trim() || 'Gen AI',
    startDate: document.getElementById('evStart').value.trim(),
    endDate: document.getElementById('evEnd').value.trim(),
    location: document.getElementById('evLocation').value.trim(),
  };
  try{
    const res = await fetch(editingId? `/api/admin/events/${editingId}`: '/api/admin/events',{
      method: editingId? 'PUT':'POST',
      headers:{ 'Content-Type':'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    });
    let data;
    const ctype = res.headers.get('content-type') || '';
    if (ctype.includes('application/json')) {
      data = await res.json();
    } else {
      const text = await res.text();
      throw new Error(text.slice(0, 200) || res.statusText || 'Unexpected response');
    }
    if (!res.ok) throw new Error(data.error || 'Save failed');
    closeModal();
    location.reload();
  }catch(err){
    alert(err.message || 'Failed');
  }
});


