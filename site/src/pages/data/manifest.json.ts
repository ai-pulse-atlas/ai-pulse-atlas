import { manifest } from '../../lib/data';
export function GET() { return new Response(JSON.stringify(manifest, null, 2), {headers: {'Content-Type':'application/json; charset=utf-8'}}); }
