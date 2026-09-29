const puppeteer = require('../frontend/node_modules/puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = 'C:\\Users\\Kleberson\\AppData\\Local\\ms-playwright\\chromium-1234\\chrome-win64\\chrome.exe';
const OUTPUT_DIR = path.resolve(__dirname, '../docs/screenshots');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function login(username, password) {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  const res = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  const data = await res.json();
  if (!data.access_token) {
    throw new Error(`Failed to login as ${username}: ` + JSON.stringify(data));
  }
  return data.access_token;
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  console.log('1. Obtaining tokens for Admin and Mariana...');
  const adminToken = await login('admin@myaloca.com', 'admin123');
  const marianaToken = await login('mariana@myaloca.com', 'mariana123');
  console.log('Tokens acquired. Launching Chromium (1920x1080 @2x)...');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
      '--window-size=1920,1080'
    ],
    defaultViewport: {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2
    }
  });

  const page = await browser.newPage();

  // Helper to click navigation button in header
  const clickNav = async (text) => {
    return page.evaluate((t) => {
      const btn = Array.from(document.querySelectorAll('nav button')).find(b => b.innerText.includes(t));
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    }, text);
  };

  // Helper to click subtab button in main content
  const clickMainButton = async (text) => {
    return page.evaluate((t) => {
      const btn = Array.from(document.querySelectorAll('main button')).find(b => b.innerText.includes(t));
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    }, text);
  };

  // Helper to close any open modal
  const closeModal = async () => {
    await page.evaluate(() => {
      const xBtn = Array.from(document.querySelectorAll('.fixed.inset-0 button')).find(btn => btn.querySelector('svg.lucide-x'));
      if (xBtn) {
        xBtn.click();
      } else {
        const cancelBtn = Array.from(document.querySelectorAll('.fixed.inset-0 button')).find(b => b.innerText.includes('Cancelar') || b.innerText.includes('Fechar'));
        if (cancelBtn) cancelBtn.click();
      }
    });
    await page.keyboard.press('Escape');
    await sleep(700);
  };

  // --- START ADMIN SESSION ---
  await page.goto('http://localhost:5173/', { waitUntil: 'domcontentloaded' });
  await page.evaluate((jwt) => localStorage.setItem('myaloca_token', jwt), adminToken);
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await sleep(4000); // Three.js WebGL scene warmup

  // =========================================================================
  // 1. 3D Office Overview
  // =========================================================================
  console.log('📸 1. Capturing 01-3d-office-overview.png...');
  await page.screenshot({ path: path.join(OUTPUT_DIR, '01-3d-office-overview.png') });

  // =========================================================================
  // 2. 3D Desk Detail Modal
  // =========================================================================
  console.log('📸 2. Capturing 02-3d-desk-modal-booking.png...');
  await page.mouse.click(960, 530);
  await sleep(1500);
  let hasModal = await page.evaluate(() => !!document.querySelector('.fixed.inset-0'));
  if (!hasModal) {
    await page.mouse.click(820, 480);
    await sleep(1500);
  }
  await page.screenshot({ path: path.join(OUTPUT_DIR, '02-3d-desk-modal-booking.png') });
  await closeModal();
  await sleep(800);

  // =========================================================================
  // 3. 2D Floorplan & Facilities Management (Baias & Salas)
  // =========================================================================
  console.log('📸 3. Capturing 03-2d-floorplan-facilities.png...');
  await clickNav('Facilities');
  await sleep(2200);
  await clickMainButton('Baias & Salas');
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '03-2d-floorplan-facilities.png') });

  // =========================================================================
  // 4. Facilities - Edifícios & Sedes
  // =========================================================================
  console.log('📸 4. Capturing 04-facilities-buildings.png...');
  await clickMainButton('Edifícios & Sedes');
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '04-facilities-buildings.png') });

  // =========================================================================
  // 5. Facilities - Pavimentos & Plantas
  // =========================================================================
  console.log('📸 5. Capturing 05-facilities-floors-zones.png...');
  await clickMainButton('Pavimentos & Andares');
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '05-facilities-floors-zones.png') });

  // =========================================================================
  // 6. Team & Roles Management (Users tab)
  // =========================================================================
  console.log('📸 6. Capturing 06-team-and-roles-admin.png...');
  await clickNav('Equipe & Cargos');
  await sleep(2000);
  await clickMainButton('Colaboradores & Cargos');
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '06-team-and-roles-admin.png') });

  // =========================================================================
  // 7. Departments CRUD
  // =========================================================================
  console.log('📸 7. Capturing 07-departments-crud.png...');
  await clickMainButton('Departamentos Corporativos');
  await sleep(1800);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '07-departments-crud.png') });

  // =========================================================================
  // 8. Printable QR Code Sticker Modal Preview
  // =========================================================================
  console.log('📸 8. Capturing 08-qr-code-sticker-modal.png...');
  await clickNav('Facilities');
  await sleep(2000);
  await clickMainButton('Baias & Salas');
  await sleep(1500);
  // Click first grid cell to open QR modal
  await page.evaluate(() => {
    const cell = document.querySelector('div[draggable="true"]');
    if (cell) cell.click();
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '08-qr-code-sticker-modal.png') });
  await closeModal();
  await sleep(800);

  // =========================================================================
  // 9. QR Scanner Modal
  // =========================================================================
  console.log('📸 9. Capturing 09-qr-scanner-modal.png...');
  await page.evaluate(() => {
    const scanBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Check-in'));
    if (scanBtn) scanBtn.click();
  });
  await sleep(1500);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '09-qr-scanner-modal.png') });
  await closeModal();
  await sleep(800);

  // =========================================================================
  // 10. User Profile & Avatar
  // =========================================================================
  console.log('📸 10. Capturing 10-user-profile-and-avatar.png...');
  await clickNav('Meu Perfil');
  await sleep(1800);
  await page.evaluate(() => {
    const editBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Editar Perfil'));
    if (editBtn) editBtn.click();
  });
  await sleep(1200);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '10-user-profile-and-avatar.png') });

  // =========================================================================
  // 11. My Bookings with Active Reservation (Switched to Mariana Silva)
  // =========================================================================
  console.log('📸 11. Capturing 11-my-bookings-and-checkin.png (as Mariana Silva)...');
  await page.evaluate((jwt) => localStorage.setItem('myaloca_token', jwt), marianaToken);
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await sleep(1800);
  await clickNav('Minhas Reservas');
  await sleep(2200);
  await page.screenshot({ path: path.join(OUTPUT_DIR, '11-my-bookings-and-checkin.png') });

  await browser.close();
  console.log('✨ All 11 live screenshots captured successfully into docs/screenshots/!');
}

main().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
