import { metadata } from '../lib/data';
export function GET() { return new Response(JSON.stringify(metadata, null, 2), {headers: {'Content-Type':'application/json; charset=utf-8'}}); }
