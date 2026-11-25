// Checks that atlas/index.html carries a literal copy of PALETTES from mapeo/index.html (PLAN §5.4, P5).
// Usage: node atlas/test/paleta.cjs
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..', '..');
const block = f => {
  const s = fs.readFileSync(path.join(root, f), 'utf8');
  const m = s.match(/const PALETTES=\[[\s\S]*?\n\];/);
  if (!m) throw new Error('PALETTES not found in ' + f);
  return m[0];
};
const a = block('mapeo/index.html'), b = block('atlas/index.html');
if (a !== b) { console.error('PALETTES differ between mapeo/index.html and atlas/index.html'); process.exit(1); }
console.log('ok: PALETTES igual en mapeo y atlas (' + (a.match(/id:'/g) || []).length + ' paletas)');
