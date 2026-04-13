const driverStore = {
  list: [],
  selectedId: null,
};

function readInitialDrivers() {
  const el = document.getElementById("drivers-data");
  if (!el) return [];
  try {
    return JSON.parse(el.textContent);
  } catch (e) {
    console.warn("Cannot parse drivers", e);
    return [];
  }
}

function renderDrivers() {
  const container = document.getElementById("drivers");
  container.innerHTML = "";
  driverStore.list
    .sort((a, b) => a.price - b.price)
    .forEach((drv, idx) => {
      const card = document.createElement("button");
      card.className = "driver-card";
      if (!driverStore.selectedId && idx === 0) {
        driverStore.selectedId = drv.id;
      }
      if (driverStore.selectedId === drv.id) card.classList.add("active");
      card.innerHTML = `
        <div class="driver-main">
          <div>
            <div class="driver-name">${drv.full_name}</div>
            <div class="driver-car">${drv.car}</div>
          </div>
          <div class="driver-price">${drv.price.toLocaleString()} so'm</div>
        </div>
        <div class="driver-meta">
          <span>☎ ${drv.phone}</span>
          <span>ETA ~${drv.eta} daqiqa</span>
        </div>
      `;
      card.addEventListener("click", () => {
        driverStore.selectedId = drv.id;
        renderDrivers();
      });
      container.appendChild(card);
    });
}

async function refreshDrivers() {
  try {
    const resp = await fetch("/api/drivers/");
    const data = await resp.json();
    driverStore.list = data.drivers || [];
    if (driverStore.list.length && !driverStore.selectedId) {
      driverStore.selectedId = driverStore.list[0].id;
    }
    renderDrivers();
  } catch (e) {
    console.error("Failed to load drivers", e);
  }
}

function currentPayment() {
  const active = document.querySelector(".pill-group button.active");
  return active ? active.dataset.value : "naqd";
}

function setupPaymentToggle() {
  document.querySelectorAll(".pill-group button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".pill-group button")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

function updateMap() {
  const dest = document.getElementById("destination").value.trim();
  const origin = document.getElementById("origin").value.trim();
  const query = dest || origin || "Tashkent";
  const map = document.getElementById("map");
  const url = `https://www.google.com/maps?q=${encodeURIComponent(
    query
  )}&output=embed`;
  map.src = url;
}

async function sendOrder() {
  const origin = document.getElementById("origin").value.trim();
  const destination = document.getElementById("destination").value.trim();
  const note = document.getElementById("note").value.trim();
  const driverId = driverStore.selectedId;

  if (!origin || !destination) {
    alert("Qayerdan va Qayerga maydonlari to'ldirilishi shart.");
    return;
  }
  if (!driverId) {
    alert("Haydovchini tanlang.");
    return;
  }

  const payload = {
    driver_id: driverId,
    origin,
    destination,
    payment: currentPayment(),
    note,
  };

  try {
    const resp = await fetch("/api/order/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error || "Noma'lum xato");
    document.getElementById("eta-value").textContent = `${data.eta} daqiqa`;
    updateMap();
    alert("Buyurtma qabul qilindi! Haydovchi yo'lda.");
  } catch (e) {
    console.error(e);
    alert("Buyurtma yuborishda xatolik: " + e.message);
  }
}

function init() {
  driverStore.list = readInitialDrivers();
  if (driverStore.list.length) {
    driverStore.selectedId = driverStore.list[0].id;
  }
  setupPaymentToggle();
  renderDrivers();
  refreshDrivers();

  document.getElementById("order-btn").addEventListener("click", sendOrder);
  document
    .getElementById("destination")
    .addEventListener("change", updateMap);
  document.getElementById("origin").addEventListener("change", updateMap);
}

document.addEventListener("DOMContentLoaded", init);
