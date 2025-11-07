// Mobile menu toggle
const mobileBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');
if (mobileBtn && mobileMenu) {
  mobileBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
  });
}

// Proposal download link setup
const proposalBtn = document.getElementById('proposalBtn');
if (proposalBtn) {
  const localPdf = '/static/Gen-AI-Bootcamp-brochure.pdf';
  proposalBtn.href = localPdf;
  // Ensure download behaviour with a friendly filename
  if (!proposalBtn.getAttribute('download')) {
    proposalBtn.setAttribute('download', 'Gen-AI-Bootcamp-Proposal.pdf');
  }
}

// Tabs for testimonials
const tabButtons = document.querySelectorAll('.tab-btn');
tabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    tabButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.getAttribute('data-tab');
    document.querySelectorAll('.tab-pane').forEach((pane) => pane.classList.add('hidden'));
    const activePane = document.getElementById(`tab-${tab}`);
    if (activePane) activePane.classList.remove('hidden');
  });
});

// Registration form submission
const form = document.getElementById('registerForm');
const formMsg = document.getElementById('formMsg');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    formMsg.textContent = '';
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    try {
      const res = await fetch('/api/register-college', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Submission failed');
      formMsg.className = 'text-sm text-green-600';
      formMsg.textContent = 'Thanks! We will contact you shortly.';
      form.reset();
    } catch (err) {
      formMsg.className = 'text-sm text-red-600';
      formMsg.textContent = err.message || 'Something went wrong.';
    }
  });
}

// Load events on homepage
async function loadEvents(){
  const container = document.getElementById('eventsContainer');
  if (!container) return;
  try{
    const res = await fetch('/api/events');
    const data = await res.json();
    const events = (data && data.events) || [];
    if (!events.length){
      document.getElementById('eventsEmpty')?.classList.remove('hidden');
      return;
    }
    const frag = document.createDocumentFragment();
    events.forEach(ev => {
      const card = document.createElement('div');
      card.className = 'up-card';
      card.innerHTML = `
        <div>
          <div class="font-semibold text-slate-900">${ev.startDate} – ${ev.endDate}</div>
          <div class="text-slate-600">${ev.location}</div>
        </div>
        <a href="#collab" class="btn-outline">Know More</a>
      `;
      frag.appendChild(card);
    });
    container.appendChild(frag);
  }catch(err){
    console.warn('Failed to load events', err);
  }
}
loadEvents();

// Student Feedback Form Submission
const studentFeedbackForm = document.getElementById('studentFeedbackForm');
const studentFeedbackMsg = document.getElementById('studentFeedbackMsg');
if (studentFeedbackForm) {
  studentFeedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    studentFeedbackMsg.textContent = '';
    const formData = new FormData(studentFeedbackForm);
    const payload = Object.fromEntries(formData.entries());
    try {
      const res = await fetch('/api/submit-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Submission failed');
      studentFeedbackMsg.className = 'text-sm text-green-600 font-semibold';
      studentFeedbackMsg.textContent = '✓ Thank you for your feedback!';
      studentFeedbackForm.reset();
      setTimeout(() => {
        studentFeedbackMsg.textContent = '';
      }, 5000);
    } catch (err) {
      studentFeedbackMsg.className = 'text-sm text-red-600 font-semibold';
      studentFeedbackMsg.textContent = '✗ ' + (err.message || 'Something went wrong.');
    }
  });
}

// Faculty Feedback Form Submission
const facultyFeedbackForm = document.getElementById('facultyFeedbackForm');
const facultyFeedbackMsg = document.getElementById('facultyFeedbackMsg');
if (facultyFeedbackForm) {
  facultyFeedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    facultyFeedbackMsg.textContent = '';
    const formData = new FormData(facultyFeedbackForm);
    const payload = Object.fromEntries(formData.entries());
    try {
      const res = await fetch('/api/submit-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Submission failed');
      facultyFeedbackMsg.className = 'text-sm text-green-600 font-semibold';
      facultyFeedbackMsg.textContent = '✓ Thank you for your feedback!';
      facultyFeedbackForm.reset();
      setTimeout(() => {
        facultyFeedbackMsg.textContent = '';
      }, 5000);
    } catch (err) {
      facultyFeedbackMsg.className = 'text-sm text-red-600 font-semibold';
      facultyFeedbackMsg.textContent = '✗ ' + (err.message || 'Something went wrong.');
    }
  });
}


