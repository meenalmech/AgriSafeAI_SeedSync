const form = document.getElementById('assessmentForm');
const errorBox = document.getElementById('formError');
const resultContent = document.getElementById('resultContent');
const emptyState = document.getElementById('emptyState');
const submitButton = form.querySelector('button[type="submit"]');
const clearAssessmentButton = document.getElementById('clearAssessmentBtn');
let lastPayload = null;
let assessmentInProgress = false;
let farmerKey = localStorage.getItem('agrisafe_farmer_key') || '';

function workspaceMessage(text, isError = false) {
  const el = document.getElementById('workspaceMessage');
  if (el) {
    el.textContent = text;
    el.className = `weather-status${isError ? ' error' : ''}`;
  }
}

function updateProfileStatus(name = '') {
  const el = document.getElementById('profileStatus');
  if (el) el.textContent = farmerKey ? `Profil aktif${name ? `: ${name}` : ''}` : 'Belum didaftarkan';
}

async function workspaceRequest(path, options = {}) {
  if (!farmerKey) throw new Error('Daftar profil petani dahulu.');
  const headers = {'Content-Type': 'application/json', ...(options.headers || {}), 'X-Farmer-Key': farmerKey};
  const response = await fetch(path, {...options, headers});
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Permintaan gagal');
  return data;
}

function setDateTimeLimits() {
  const dateInput = form.elements['planned_date'];
  const timeInput = form.elements['planned_time'];
  const now = new Date();
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  dateInput.min = today;
  if (!dateInput.value) dateInput.value = today;
  if (dateInput.value === today) {
    timeInput.min = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  } else {
    timeInput.min = '';
  }
}

const malaysiaLocations = {
  'Johor': ['Johor Bahru', 'Batu Pahat', 'Muar', 'Kluang', 'Segamat', 'Pasir Gudang', 'Kulai'],
  'Kedah': ['Alor Setar', 'Sungai Petani', 'Langkawi', 'Kulim', 'Baling'],
  'Kelantan': ['Kota Bharu', 'Pasir Mas', 'Tumpat', 'Machang', 'Tanah Merah', 'Kuala Krai'],
  'Melaka': ['Melaka City', 'Jasin', 'Alor Gajah'],
  'Negeri Sembilan': ['Seremban', 'Port Dickson', 'Tampin', 'Kuala Pilah', 'Jempol'],
  'Pahang': ['Kuantan', 'Temerloh', 'Bentong', 'Raub', 'Cameron Highlands', 'Pekan'],
  'Penang': ['George Town', 'Butterworth', 'Bukit Mertajam', 'Seberang Jaya', 'Bayan Lepas'],
  'Perak': ['Ipoh', 'Taiping', 'Kampar', 'Teluk Intan', 'Sitiawan', 'Tapah'],
  'Perlis': ['Kangar', 'Arau', 'Padang Besar'],
  'Selangor': ['Shah Alam', 'Petaling Jaya', 'Subang Jaya', 'Klang', 'Kajang', 'Rawang', 'Sepang', 'Banting'],
  'Terengganu': ['Kuala Terengganu', 'Kemaman', 'Dungun', 'Marang', 'Setiu'],
  'Sabah': ['Kota Kinabalu', 'Sandakan', 'Tawau', 'Lahad Datu', 'Keningau', 'Sipitang', 'Beaufort'],
  'Sarawak': ['Kuching', 'Sibu', 'Miri', 'Bintulu', 'Sri Aman', 'Kota Samarahan', 'Limbang'],
  'Wilayah Persekutuan': ['Kuala Lumpur', 'Putrajaya', 'Labuan']
};

function populateAreaSelect(){
  const areaSelect = document.getElementById('areaSelect');
  if (!areaSelect) return;

  Object.entries(malaysiaLocations).forEach(([state, districts]) => {
    const group = document.createElement('optgroup');
    group.label = state;

    districts.forEach((district) => {
      const option = document.createElement('option');
      option.value = `${state} - ${district}`;
      option.textContent = `${state} - ${district}`;
      group.appendChild(option);
    });

    areaSelect.appendChild(group);
  });
}

async function fetchWeatherFromSelection() {
  const form = document.getElementById('assessmentForm');
  const weatherStatus = document.getElementById('weatherStatus');
  if (!form) return;

  const area = form.elements['area']?.value || '';
  const plannedDate = form.elements['planned_date']?.value || '';
  const plannedTime = form.elements['planned_time']?.value || '';
  const latitude = form.elements['latitude']?.value;
  const longitude = form.elements['longitude']?.value;
  const demoMode = form.elements['demo_mode']?.checked || false;

  if (!area && (!latitude || !longitude)) {
    if (weatherStatus) {
      weatherStatus.textContent = 'Add a location or coordinates';
      weatherStatus.className = 'weather-status';
    }
    return;
  }
  if (!plannedDate || !plannedTime) {
    if (weatherStatus) {
      weatherStatus.textContent = 'Choose date and time';
      weatherStatus.className = 'weather-status';
    }
    return;
  }

  if (weatherStatus) {
    weatherStatus.textContent = 'Fetching forecast...';
    weatherStatus.className = 'weather-status loading';
  }

  const params = new URLSearchParams({
    planned_date: plannedDate,
    planned_time: plannedTime,
    demo_mode: String(demoMode),
  });

  if (area) {
    params.set('area', area);
  } else {
    if (latitude) params.set('latitude', latitude);
    if (longitude) params.set('longitude', longitude);
  }

  try {
    const response = await fetch(`/api/weather?${params.toString()}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to fetch forecast');

    form.elements['temperature_c'].value = data.temperature_c;
    form.elements['humidity_pct'].value = data.humidity_pct;
    form.elements['wind_kmh'].value = data.wind_kmh;
    form.elements['rain_probability_pct'].value = data.rain_probability_pct;

    if (weatherStatus) {
      weatherStatus.textContent = 'Forecast updated';
      weatherStatus.className = 'weather-status';
    }
  } catch (err) {
    console.warn('Weather auto-fill failed:', err);
    if (weatherStatus) {
      weatherStatus.textContent = err.message || 'Forecast unavailable';
      weatherStatus.className = 'weather-status error';
    }
  }
}

function val(form, name){ return form.elements[name].value; }
function numberOrNull(v){ return v === '' ? null : Number(v); }
function checkedValues(name){ return [...form.querySelectorAll(`input[name="${name}"]:checked`)].map(input => input.value); }

populateAreaSelect();
setDateTimeLimits();

const demoScenarios = {
  'spray-risk': {
    crop: 'Chili', task: 'Pesticide spraying', area: 'Selangor - Shah Alam',
    planned_time: '14:00', chemical: 'Demo Pesticide X', growth_stage: 'Flowering',
    equipment: 'Knapsack sprayer', workers_count: 3, worker_exposure_hours: 4,
    temperature_c: 34, humidity_pct: 82, wind_kmh: 18, rain_probability_pct: 70,
    ppe_complete: false, demo_mode: true
  },
  'spray-safe': {
    crop: 'Chili', task: 'Pesticide spraying', area: 'Selangor - Shah Alam',
    planned_time: '07:00', chemical: 'Demo Pesticide X', growth_stage: 'Vegetative',
    equipment: 'Knapsack sprayer', workers_count: 2, worker_exposure_hours: 0,
    temperature_c: 28, humidity_pct: 75, wind_kmh: 6, rain_probability_pct: 15,
    ppe_complete: true, demo_mode: true
  },
  inspection: {
    crop: 'Rice', task: 'Field inspection', area: 'Kedah - Alor Setar',
    planned_time: '07:30', chemical: '', growth_stage: 'Vegetative',
    equipment: 'Manual hand tools', workers_count: 2, worker_exposure_hours: 0,
    temperature_c: 27, humidity_pct: 70, wind_kmh: 5, rain_probability_pct: 10,
    ppe_complete: true, demo_mode: true
  }
};

function loadDemoScenario(name) {
  const scenario = demoScenarios[name];
  if (!scenario) return;
  Object.entries(scenario).forEach(([field, value]) => {
    const input = form.elements[field];
    if (!input) return;
    if (input.type === 'checkbox') input.checked = Boolean(value);
    else input.value = value;
  });
  setDateTimeLimits();
  const weatherStatus = document.getElementById('weatherStatus');
  if (weatherStatus) {
    weatherStatus.textContent = 'Data demo dimuat';
    weatherStatus.className = 'weather-status';
  }
}

document.getElementById('demoScenario')?.addEventListener('change', (event) => {
  loadDemoScenario(event.target.value);
});

document.getElementById('fetchWeatherBtn')?.addEventListener('click', fetchWeatherFromSelection);
document.getElementById('areaSelect')?.addEventListener('change', fetchWeatherFromSelection);
document.querySelector('input[name="planned_date"]')?.addEventListener('change', fetchWeatherFromSelection);
document.querySelector('input[name="planned_time"]')?.addEventListener('change', fetchWeatherFromSelection);
document.querySelector('input[name="planned_date"]')?.addEventListener('change', setDateTimeLimits);
document.querySelector('input[name="latitude"]')?.addEventListener('change', fetchWeatherFromSelection);
document.querySelector('input[name="longitude"]')?.addEventListener('change', fetchWeatherFromSelection);

clearAssessmentButton?.addEventListener('click', () => {
  form.reset();
  setDateTimeLimits();
  form.elements['temperature_c'].value = '';
  form.elements['humidity_pct'].value = '';
  form.elements['wind_kmh'].value = '';
  form.elements['rain_probability_pct'].value = '';
  errorBox.textContent = '';
  emptyState.hidden = false;
  resultContent.hidden = true;
  lastPayload = null;
  const weatherStatus = document.getElementById('weatherStatus');
  if (weatherStatus) {
    weatherStatus.textContent = 'Select a location and fetch a forecast';
    weatherStatus.className = 'weather-status';
  }
  form.elements['crop'].focus();
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (assessmentInProgress) return;
  assessmentInProgress = true;
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Assessing...';
  }
  errorBox.textContent = '';
  const payload = {
    crop: val(form,'crop'), task: val(form,'task'), planned_date: val(form,'planned_date') || null,
    planned_time: val(form,'planned_time'), area: val(form,'area') || null,
    duration_minutes: Number(val(form,'duration_minutes')),
    latitude: numberOrNull(val(form,'latitude')), longitude: numberOrNull(val(form,'longitude')),
    chemical: val(form,'chemical') || null,
    growth_stage: val(form,'growth_stage') || null,
    equipment: val(form,'equipment') || null,
    workers_count: Number(val(form,'workers_count') || 1),
    vulnerability_flags: checkedValues('vulnerability_flags'),
    temperature_c: numberOrNull(val(form,'temperature_c')), humidity_pct: numberOrNull(val(form,'humidity_pct')),
    wind_kmh: numberOrNull(val(form,'wind_kmh')), rain_probability_pct: numberOrNull(val(form,'rain_probability_pct')),
    worker_exposure_hours: Number(val(form,'worker_exposure_hours')),
    ppe_complete: form.elements['ppe_complete'].checked,
    demo_mode: form.elements['demo_mode'].checked,
    language: form.elements['language'].value
  };
  lastPayload = payload;
  try {
    const res = await fetch('/api/assessments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || 'Assessment failed');
    renderResult(data);
    loadHistory();
  } catch(err){ errorBox.textContent = err.message; }
  finally {
    assessmentInProgress = false;
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = 'Assess Safety';
    }
  }
});

function renderResult(data){
  const language = data.language || 'en';
  emptyState.hidden = true; resultContent.hidden = false;
  document.getElementById('decision').textContent = data.decision;
  document.getElementById('decision').className = data.decision;
  document.getElementById('score').textContent = `${data.risk_score}/100`;
  document.getElementById('level').textContent = data.risk_level;
  document.getElementById('level').className = `level ${data.decision}`;
  const summary = language === 'ms'
    ? (data.decision === 'PROCEED' ? 'Keadaan berada dalam had prototaip. Lengkapkan senarai semak keselamatan biasa.' : data.decision === 'MODIFY' ? 'Gunakan kawalan yang disenaraikan dan nilaikan semula sebelum memulakan.' : data.decision === 'DELAY' ? 'Tunggu masa yang lebih selamat dan nilaikan semula sebelum memulakan.' : 'Jangan anggap ini selamat untuk diteruskan sehingga isu yang disenaraikan diselesaikan.')
    : (data.decision === 'PROCEED' ? 'Conditions are within the configured prototype thresholds. Complete the normal checklist.' : data.decision === 'MODIFY' ? 'Apply the listed controls and reassess before starting.' : data.decision === 'DELAY' ? 'Wait for a safer window and reassess before starting.' : 'Do not treat this as a safe-to-proceed decision until the listed issues are resolved.');
  document.getElementById('summary').textContent = summary;
  document.getElementById('reasons').innerHTML = data.reasons.map(x=>`<li>${escapeHtml(x)}</li>`).join('');
  document.getElementById('actions').innerHTML = data.actions.map(x=>`<li>${escapeHtml(x)}</li>`).join('');
  document.getElementById('rules').innerHTML = data.rules_triggered.map(x=>`<span class="chip">${escapeHtml(x)}</span>`).join('');
  const w = data.weather;
  document.getElementById('weather').innerHTML = `<div class="weather-grid"><div><strong>${w.temperature_c}°C</strong><small>Temp</small></div><div><strong>${w.humidity_pct}%</strong><small>Humidity</small></div><div><strong>${w.wind_kmh} km/h</strong><small>Wind</small></div><div><strong>${w.rain_probability_pct}%</strong><small>Rain</small></div></div><small>Source: ${escapeHtml(w.source || 'unknown')}</small>`;
  document.getElementById('ppeChecklist').innerHTML = (data.ppe_checklist || []).map(item => `<li>${escapeHtml(item)}</li>`).join('') || '<li>Tiada PPE khusus dijana</li>';
  const plan = data.work_rest_plan || {};
  document.getElementById('workRestPlan').innerHTML = `${plan.work_minutes || '-'} minit kerja / ${plan.rest_minutes || '-'} minit rehat<br><small>${escapeHtml(plan.message || '')}</small>`;
  const timing = data.safety_timing || {};
  document.getElementById('safetyTiming').innerHTML = timing.reentry_at ? `Masuk semula: <strong>${escapeHtml(timing.reentry_at)}</strong><br>Selamat menuai: <strong>${escapeHtml(timing.harvest_safe_date || 'Rujuk label')}</strong>` : 'Rujuk label produk untuk masa masuk dan menuai.';
  if (data.task_log) {
    const taskLog = document.createElement('div');
    taskLog.className = 'task-log';
    taskLog.innerHTML = `<strong>Task log</strong><ul><li>Crop: ${escapeHtml(data.task_log.crop || '-')}</li><li>Task: ${escapeHtml(data.task_log.task || '-')}</li><li>Stage: ${escapeHtml(data.task_log.growth_stage || 'Not specified')}</li><li>Equipment: ${escapeHtml(data.task_log.equipment || 'Not specified')}</li><li>Workers: ${escapeHtml(String(data.task_log.workers_count || 1))}</li><li>Recommended action: ${escapeHtml(data.task_log.recommended_action || '-')}</li></ul>`;
    document.getElementById('saferResult').innerHTML = '';
    document.getElementById('saferResult').appendChild(taskLog);
  } else {
    document.getElementById('saferResult').innerHTML = '';
  }
}

document.getElementById('saferButton').addEventListener('click', async ()=>{
  if(!lastPayload) return;
  const body = {
    crop:lastPayload.crop,
    task:lastPayload.task,
    planned_date:lastPayload.planned_date,
    area:lastPayload.area,
    latitude:lastPayload.latitude,
    longitude:lastPayload.longitude,
    chemical:lastPayload.chemical,
    growth_stage:lastPayload.growth_stage,
    equipment:lastPayload.equipment,
    workers_count:lastPayload.workers_count,
    vulnerability_flags:lastPayload.vulnerability_flags,
    duration_minutes:lastPayload.duration_minutes,
    worker_exposure_hours:lastPayload.worker_exposure_hours,
    ppe_complete:lastPayload.ppe_complete,
    demo_mode:true,
    language:lastPayload.language || 'ms'
  };
  const box = document.getElementById('saferResult'); box.textContent='Searching windows...';
  try{
    const res=await fetch('/api/safer-windows',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data=await res.json(); if(!res.ok) throw new Error(data.detail || 'Unable to search');
    const recommended = data.recommended ? `<div class="window recommended"><strong>Recommended window: ${data.recommended.label}</strong><br>${data.recommended.temperature_c}°C · ${data.recommended.wind_kmh} km/h wind · ${data.recommended.rain_probability_pct}% rain · ${data.recommended.risk_score}/100 · ${data.recommended.decision}<br><small>${escapeHtml((data.recommended.why || []).join(' • '))}</small></div>` : '<div class="window">No suitable lower-risk window found in the demo horizon.</div>';
    const windows = data.windows.map(w=>`<div class="window"><strong>${w.label}</strong> · ${w.risk_score}/100 · ${w.decision}<br><small>${escapeHtml((w.why || []).join(' • '))}</small><br><small>${escapeHtml(w.best_action || '')}</small></div>`).join('');
    box.innerHTML = recommended + windows;
  }catch(err){ box.textContent=err.message; }
});

document.getElementById('refreshHistory').addEventListener('click', loadHistory);
document.getElementById('farmerForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  try {
    const response = await fetch('/api/farmers', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: formData.get('farmer_name'), phone: formData.get('farmer_phone') || null, preferred_language: 'ms'})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Pendaftaran gagal');
    farmerKey = data.api_key;
    localStorage.setItem('agrisafe_farmer_key', farmerKey);
    updateProfileStatus(data.name);
    workspaceMessage('Profil petani berjaya didaftarkan.');
  } catch (err) { workspaceMessage(err.message, true); }
});

document.getElementById('farmForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  try {
    await workspaceRequest('/api/farms', {method: 'POST', body: JSON.stringify({name: formData.get('farm_name'), location: formData.get('farm_location') || null})});
    workspaceMessage('Ladang berjaya ditambah.');
    event.currentTarget.reset();
  } catch (err) { workspaceMessage(err.message, true); }
});

document.getElementById('incidentForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  try {
    await workspaceRequest('/api/incidents', {method: 'POST', body: JSON.stringify({kind: formData.get('incident_kind'), severity: 'medium', description: formData.get('incident_description')})});
    workspaceMessage('Laporan kejadian disimpan.');
    event.currentTarget.reset();
  } catch (err) { workspaceMessage(err.message, true); }
});

async function openReport(path) {
  if (!farmerKey) { workspaceMessage('Daftar profil petani dahulu.', true); return; }
  try {
    const response = await fetch(path, {headers: {'X-Farmer-Key': farmerKey}});
    if (!response.ok) throw new Error('Laporan tidak dapat dijana.');
    const blob = await response.blob();
    window.open(URL.createObjectURL(blob), '_blank');
  } catch (err) { workspaceMessage(err.message, true); }
}
document.getElementById('downloadCsvBtn')?.addEventListener('click', () => openReport('/api/reports/hirarc.csv'));
document.getElementById('downloadHtmlBtn')?.addEventListener('click', () => openReport('/api/reports/hirarc.html'));
async function loadEmergencyGuidance(){
  const box = document.getElementById('emergencyGuidance');
  if (!box) return;
  try {
    const res = await fetch('/api/emergency?language=ms');
    const data = await res.json();
    box.innerHTML = `<div class="emergency-columns"><div><strong>Pendedahan bahan kimia</strong><ol>${data.poisoning.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ol></div><div><strong>Strok haba</strong><ol>${data.heat_stroke.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ol></div></div>`;
  } catch (err) { box.textContent = 'Panduan kecemasan tidak tersedia.'; }
}
async function loadHistory(){
  const el=document.getElementById('history');
  try{
    const res=await fetch('/api/assessments'); const rows=await res.json();
    if(!rows.length){el.textContent='No assessments yet.';return;}
    el.innerHTML=`<table class="history-table"><thead><tr><th>ID</th><th>Time</th><th>Crop</th><th>Task</th><th>Risk</th><th>Decision</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${r.id}</td><td>${new Date(r.created_at).toLocaleString()}</td><td>${escapeHtml(r.crop)}</td><td>${escapeHtml(r.task)}</td><td>${r.risk_score}/100</td><td class="decision ${r.decision}">${r.decision}</td></tr>`).join('')}</tbody></table>`;
  }catch(err){el.textContent='History unavailable.';}
}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
loadHistory();
loadEmergencyGuidance();
updateProfileStatus();
