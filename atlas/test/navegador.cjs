// Browser check (PLAN §8, functional + visual): opens every map and stage of atlas/index.html in headless
// Edge/Chrome through the DevTools protocol, fails on any console error or exception, checks that every
// feature of the stage is drawn, that ←/→ change the stage, and saves screenshots to atlas/test/capturas/.
// Usage: node atlas/test/navegador.cjs   (no server: file:// URL; temporary profile in atlas/_tmp/)
const fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const ATLAS = path.resolve(__dirname, '..');
const BROWSERS = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'];
const exe = BROWSERS.find(p => fs.existsSync(p));
const PORT = 9333, PROFILE = path.join(ATLAS, '_tmp', 'perfil-navegador'), SHOTS = path.join(__dirname, 'capturas');
const url = h => 'file:///' + path.join(ATLAS, 'index.html').replace(/\\/g, '/').replace(/ /g, '%20') + h;
const sleep = ms => new Promise(r => setTimeout(r, ms));

global.ATLAS_CATALOG = null;
const catalog = (() => { const s = fs.readFileSync(path.join(ATLAS, 'data', 'catalog.js'), 'utf8'); const window = {}; eval(s); return window.ATLAS_CATALOG; })();

async function main() {
  setTimeout(() => { console.error('tiempo agotado'); process.exit(2); }, 900000).unref();
  fs.mkdirSync(SHOTS, { recursive: true });
  const br = spawn(exe, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`, '--no-first-run', '--disable-extensions', '--allow-file-access-from-files', 'about:blank'], { stdio: 'ignore' });
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(200);
    try { target = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(t => t.type === 'page' && t.url === 'about:blank'); } catch (e) {}
  }
  if (process.env.TRAZA) console.error('pestaña', target && target.url);
  if (!target) throw new Error('no se encuentra la pestaña del navegador');
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);
  let id = 0; const pending = {}, problems = [];
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; return; }
    if (m.method === 'Runtime.exceptionThrown') problems.push('excepción: ' + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text));
    if (m.method === 'Runtime.consoleAPICalled' && ['error', 'assert'].includes(m.params.type)) problems.push('console.error: ' + m.params.args.map(a => a.value ?? a.description).join(' '));
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error' && !/fonts\.(googleapis|gstatic)/.test(m.params.entry.url || '')) problems.push('log: ' + m.params.entry.text + ' ' + (m.params.entry.url || ''));
  };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pending[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  const evalJs = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.result?.value;
  const waitFor = async (expr, ms = 15000) => { for (let t = 0; t < ms; t += 150) { if (await evalJs(expr)) return true; await sleep(150); } return false; };
  const shot = async name => { const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(path.join(SHOTS, name + '.png'), Buffer.from(r.result.data, 'base64')); };
  const size = (w, h, mobile = false) => send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile });
  await send('Runtime.enable'); await send('Log.enable'); await send('Page.enable');
  const results = [];
  const check = (ok, msg) => { const r = (ok ? 'ok    ' : 'FALLO ') + msg; results.push(r); if (process.env.TRAZA) console.error(r); };

  await size(1440, 900);
  await send('Page.navigate', { url: url('') });
  check(await waitFor(`document.querySelectorAll('.card').length===${catalog.length}`), `portada con ${catalog.length} tarjetas`);
  await shot('portada-oscura');

  // drawn = one SVG path per area part or marker; compare against the stage's own feature list
  const drawnOk = `(()=>{const fr=cur.d.frames.find(f=>f.year===cur.year);const n=Object.keys(byEntity).length;return n===fr.features.length&&document.querySelectorAll('#map path.ent,#map path.mk').length>=fr.features.length})()`;
  for (const c of catalog) {
    for (const y of c.years) {
      await send('Page.navigate', { url: url(`#/${c.id}/${y}`) });
      const ok = await waitFor(`(typeof cur!='undefined'&&cur)&&cur.c.id==='${c.id}'&&cur.year===${y}&&${drawnOk}`, 30000);
      check(ok, `${c.id} ${y}: todas las entidades de la etapa dibujadas`);
      if (!ok) console.error('      ' + await evalJs(`JSON.stringify({hash:location.hash,cur:!!(typeof cur!='undefined'&&cur)&&cur.c&&cur.c.id,year:(typeof cur!='undefined'&&cur)&&cur.year,ents:Object.keys(byEntity).length,paths:document.querySelectorAll('#map path').length,ent:document.querySelectorAll('#map path.ent,#map path.mk').length,status:document.querySelector('#status').textContent})`));
    }
    await sleep(400); await shot(`${c.id}-oscura`);
    // keyboard: Home goes to the first stage, → to the next one
    await evalJs(`document.activeElement&&document.activeElement.blur(),document.body.focus(),1`);
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Home', code: 'Home', windowsVirtualKeyCode: 36 });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Home', code: 'Home', windowsVirtualKeyCode: 36 });
    if (c.years.length > 1) {
      await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 });
      await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 });
      check(await waitFor(`location.hash==='#/${c.id}/${c.years[1]}'`, 3000), `${c.id}: Inicio y → cambian de etapa`);
    }
    // patterns from the original are installed when the map has any
    const pats = await evalJs(`Object.keys(cur.d.patterns||{}).every(n=>document.getElementById('pat-${c.id}-'+n))`);
    check(pats, `${c.id}: tramas originales instaladas`);
  }
  // light palette (stored the same way mapeo does)
  await evalJs(`localStorage.setItem('mapeo.cfg',JSON.stringify({palette:'papel'})),1`);
  await send('Page.navigate', { url: url('#/gran-alemania/1851') }); await send('Page.reload');
  await waitFor(`(typeof cur!='undefined'&&cur)&&cur.year===1851&&${drawnOk}`, 30000); await sleep(400);
  check(await evalJs(`getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()==='#f2f0ea'`), 'paleta clara «Papel» aplicada desde mapeo.cfg');
  await evalJs(`select('9982',true),1`); await sleep(300);
  check(await evalJs(`!!document.querySelector('#card h4')`), 'ficha de entidad (Lauenburg)');
  await shot('gran-alemania-clara-ficha');
  await send('Page.navigate', { url: url('#/centrales/1920') });
  await waitFor(`(typeof cur!='undefined'&&cur)&&cur.year===1920&&${drawnOk}`, 30000); await sleep(300); await shot('centrales-clara');
  // cumulative extent: BC stages and the possession years in the card
  await send('Page.navigate', { url: url('#/max-roma/-133') });
  await waitFor(`(typeof cur!='undefined'&&cur)&&cur.year===-133&&${drawnOk}`, 30000); await sleep(300);
  check(await evalJs(`document.querySelector('#timeline button[aria-current=true]').textContent==='133 a. C.'`), 'años antes de Cristo en la línea del tiempo');
  await evalJs(`select(frameOf().features[0].entityId,false),1`); await sleep(200);
  check(await evalJs(`/Posesión/.test(document.querySelector('#card').textContent)`), 'ficha de extensión con años de posesión');
  await shot('max-roma-clara-ficha');
  await evalJs(`localStorage.removeItem('mapeo.cfg'),1`);
  // mobile
  await size(390, 844, true);
  await send('Page.navigate', { url: url('#/carlos/1600') });
  await waitFor(`(typeof cur!='undefined'&&cur)&&cur.year===1600&&${drawnOk}`, 30000); await sleep(400);
  check(await evalJs(`document.documentElement.scrollWidth<=390`), 'móvil 390 × 844 sin desplazamiento horizontal');
  await shot('carlos-movil');
  await send('Page.navigate', { url: url('') }); await sleep(500); await shot('portada-movil');

  check(problems.length === 0, `sin errores de consola (${problems.length})`);
  problems.forEach(p => results.push('      ' + p));
  console.log(results.join('\n'));
  ws.close(); br.kill();
  await sleep(500);
  try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) {}
  process.exit(results.some(r => r.startsWith('FALLO')) ? 1 : 0);
}
main().catch(e => { console.error(e); process.exit(1); });
