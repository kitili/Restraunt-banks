const API_BASE = window.location.origin;

async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: POST,
    headers: { Content-Type: application/json },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`${res.status}: ${t}`);
  }
  return res.json();
}

function parseWindows(input) {
  if (!input) return [];
  return input.split(,).map(w => w.trim()).filter(Boolean).map(w => {
    const [s, e] = w.split(-);
    return { start_time: s, end_time: e };
  });
}

const npForm = document.getElementById(nonprofit-form);
npForm?.addEventListener(submit, async (e) => {
  e.preventDefault();
  const fd = new FormData(npForm);
  const payload = {
    name: fd.get(name),
    address: fd.get(address),
    latitude: parseFloat(fd.get(latitude)),
    longitude: parseFloat(fd.get(longitude)),
    contact_phone: fd.get(contact_phone) || null,
    contact_email: fd.get(contact_email) || null,
    pickup_windows: parseWindows(fd.get(windows)),
  };
  try {
    const data = await postJSON(/nonprofits, payload);
    document.getElementById(nonprofit-result).textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById(nonprofit-result).textContent = err.message;
  }
});

const dForm = document.getElementById(donation-form);
dForm?.addEventListener(submit, async (e) => {
  e.preventDefault();
  const fd = new FormData(dForm);
  const payload = {
    donor_name: fd.get(donor_name),
    address: fd.get(address),
    latitude: parseFloat(fd.get(latitude)),
    longitude: parseFloat(fd.get(longitude)),
    ready_at: fd.get(ready_at),
    expires_at: fd.get(expires_at),
    food_description: fd.get(food_description),
  };
  try {
    const data = await postJSON(/donations, payload);
    document.getElementById(donation-result).textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById(donation-result).textContent = err.message;
  }
});
