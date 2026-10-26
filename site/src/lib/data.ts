import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const root = pathToFileURL(resolve(process.cwd(), '..') + '/');
export const page = JSON.parse(readFileSync(new URL('build/page-data.json', root), 'utf8'));
export const manifest = JSON.parse(readFileSync(new URL('data/manifest.json', root), 'utf8'));
const dir = new URL('data/events/', root);
export const events = readdirSync(dir).filter(f => f.endsWith('.jsonl')).sort()
  .flatMap(f => readFileSync(new URL(f, dir), 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)))
  .sort((a, b) => b.event_date.localeCompare(a.event_date) || a.id.localeCompare(b.id));
export const metadata = { generated_at: page.generated_at, latest_event_id: events[0]?.id ?? null, event_count: events.length, schema_version: manifest.schema_version };
