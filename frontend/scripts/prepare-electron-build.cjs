#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const outputDir = path.resolve(__dirname, '..', 'dist_app_v2');

const tryRemove = () => {
  try {
    fs.rmSync(outputDir, { recursive: true, force: true });
    return true;
  } catch (_) {
    return false;
  }
};

const killPotentialLocks = () => {
  if (process.platform !== 'win32') return;
  spawnSync('taskkill', ['/F', '/IM', 'backend.exe', '/T'], { stdio: 'ignore' });
  spawnSync('taskkill', ['/F', '/IM', 'AI Arduino IDE.exe', '/T'], { stdio: 'ignore' });
};

killPotentialLocks();

let removed = tryRemove();
if (!removed) {
  killPotentialLocks();
  removed = tryRemove();
}

if (!removed) {
  console.warn(`[prepare-electron-build] Could not fully remove ${outputDir}. Build may fail if files are locked.`);
} else {
  console.log(`[prepare-electron-build] Cleaned ${outputDir}`);
}
