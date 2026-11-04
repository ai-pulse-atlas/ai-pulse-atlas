import { techEvents } from '../../lib/data';
export function GET() { return new Response(JSON.stringify(techEvents, null, 2), {headers: {'Content-Type':'application/json; charset=utf-8'}}); }
