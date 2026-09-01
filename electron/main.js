const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

// Key & IV ini ditimpa oleh workflow GitHub Actions saat build (random tiap build).
// Nilai placeholder di bawah ini TIDAK dipakai kalau build lewat CI.
const NOVA_KEY_HEX = '__NOVA_KEY_HEX__';
const NOVA_IV_HEX = '__NOVA_IV_HEX__';

function loadEncryptedApp(win) {
  const encPath = path.join(__dirname, 'app', 'nova_data.bin');

  if (!fs.existsSync(encPath) || NOVA_KEY_HEX.startsWith('__NOVA')) {
    // Fallback untuk development lokal (npm run dist tanpa lewat CI):
    // load index.html polos kalau ada, biar tetap bisa ditest.
    const plain = path.join(__dirname, 'app', 'index.html');
    if (fs.existsSync(plain)) { win.loadFile(plain); return; }
    win.loadURL('data:text/html,<h1>nova_data.bin tidak ditemukan</h1>');
    return;
  }

  const encrypted = fs.readFileSync(encPath);
  const key = Buffer.from(NOVA_KEY_HEX, 'hex');
  const iv = Buffer.from(NOVA_IV_HEX, 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  const html = Buffer.concat([decipher.update(encrypted), decipher.final()]).toString('utf8');

  const dataUrl = 'data:text/html;charset=utf-8;base64,' + Buffer.from(html, 'utf8').toString('base64');
  win.loadURL(dataUrl);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1600,
    height: 1000,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  loadEncryptedApp(win);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
