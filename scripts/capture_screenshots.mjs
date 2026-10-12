import puppeteer from '../frontend/node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer.js';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.resolve(__dirname, '../docs/screenshots');

async function capture() {
  console.log('Launching Chrome browser...');
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--window-size=1920,1080',
      '--hide-scrollbars'
    ],
    defaultViewport: {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1.5
    }
  });

  const page = await browser.newPage();

  // 1. Landing Page
  console.log('Capturing Landing Page (http://127.0.0.1:5173/)...');
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({
    path: path.join(outputDir, 'landing_page.png'),
    fullPage: false
  });
  console.log('Saved landing_page.png');

  // 2. Clinical Dashboard
  console.log('Capturing Dashboard (http://127.0.0.1:5173/dashboard)...');
  await page.goto('http://127.0.0.1:5173/dashboard', { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));

  try {
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await page.evaluate(el => el.textContent, btn);
      if (text && text.toLowerCase().includes('load demo patient')) {
        console.log('Found "Load demo patient" button, clicking...');
        await btn.click();
        break;
      }
    }
  } catch (e) {
    console.log('Error clicking demo button:', e.message);
  }

  // Wait for 3D render and analysis response
  await new Promise(r => setTimeout(r, 7000));
  await page.screenshot({
    path: path.join(outputDir, 'clinical_dashboard.png'),
    fullPage: false
  });
  console.log('Saved clinical_dashboard.png');

  // 3. Patient Simulator
  console.log('Capturing Simulator (http://127.0.0.1:5173/simulator)...');
  await page.goto('http://127.0.0.1:5173/simulator', { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));

  try {
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await page.evaluate(el => el.textContent, btn);
      if (text && text.includes('Analyze Patient')) {
        console.log('Found "Analyze Patient" button, clicking...');
        await btn.click();
        break;
      }
    }
  } catch (e) {
    console.log('Error clicking analyze button:', e.message);
  }

  // Wait for simulation computation & 3D render
  await new Promise(r => setTimeout(r, 6000));
  await page.screenshot({
    path: path.join(outputDir, 'patient_simulator.png'),
    fullPage: false
  });
  console.log('Saved patient_simulator.png');

  await browser.close();
  console.log('All screenshots captured successfully!');
}

capture().catch(err => {
  console.error('Fatal error during capture:', err);
  process.exit(1);
});
