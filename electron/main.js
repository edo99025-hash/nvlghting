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
  const plainPath = path.join(__dirname, 'app', 'index.html');

  try {
    if (fs.existsSync(encPath) && !NOVA_KEY_HEX.startsWith('__NOVA')) {
      const encrypted = fs.readFileSync(encPath);
      const key = Buffer.from(NOVA_KEY_HEX, 'hex');
      const iv = Buffer.from(NOVA_IV_HEX, 'hex');
      const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
      const html = Buffer.concat([decipher.update(encrypted), decipher.final()]);

      // File HTML-nya besar — data: URL kena limit ukuran Electron/Chromium dan
      // gagal render (layar putih blank). Jadi tulis sementara ke folder data
      // app sendiri (bukan folder app/, tetap terpisah dari nova_data.bin asli)
      // lalu load dari situ. Tetap tidak menaruh plaintext di paket instalasi.
      const tmpDir = path.join(app.getPath('userData'), 'nova-runtime');
      fs.mkdirSync(tmpDir, { recursive: true });
      const tmpFile = path.join(tmpDir, 'index.html');
      fs.writeFileSync(tmpFile, html);

      win.loadFile(tmpFile);
      return;
    }
  } catch (err) {
    console.error('Gagal load app terenkripsi:', err);
  }

  // Fallback untuk development lokal (npm run dist tanpa lewat CI)
  if (fs.existsSync(plainPath)) {
    win.loadFile(plainPath);
    return;
  }

  win.loadURL('data:text/html,<h1>App data tidak ditemukan</h1>');
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
