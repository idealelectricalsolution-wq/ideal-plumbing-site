// Writes src/data/lastmod.json: page path -> date its source file last changed in git.
// Runs before every build. On a shallow clone (no full history) it keeps the committed file.
import { execSync } from 'node:child_process';
import { readdirSync, statSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
const OUT = 'src/data/lastmod.json';
let shallow = true;
try { shallow = execSync('git rev-parse --is-shallow-repository').toString().trim() === 'true'; } catch {}
if (shallow) { console.log('lastmod: shallow or no git, keeping', OUT); process.exit(0); }
const walk = (d) => readdirSync(d).flatMap((f) => { const p = join(d, f); return statSync(p).isDirectory() ? walk(p) : [p]; });
const map = {};
const today = new Date().toISOString().slice(0, 10);
let dirty = '';
try { dirty = execSync('git status --porcelain -- src/pages').toString(); } catch {}
for (const f of walk('src/pages').filter((f) => f.endsWith('.astro'))) {
  let d = '';
  try { d = execSync(`git log -1 --format=%cs -- "${f}"`).toString().trim(); } catch {}
  if (dirty.includes(f)) d = today; // edited but not committed yet
  if (!d) continue;
  const path = '/' + f.replace(/^src\/pages\//, '').replace(/\.astro$/, '').replace(/(^|\/)index$/, '');
  map[path.replace(/\/$/, '') || '/'] = d;
}
writeFileSync(OUT, JSON.stringify(map, null, 1) + '\n');
console.log('lastmod: wrote', Object.keys(map).length, 'pages');
