import { events } from '../../lib/data';
export function GET() { return new Response(events.map(e => JSON.stringify(e)).join('\n') + '\n', {headers: {'Content-Type':'application/x-ndjson; charset=utf-8'}}); }
