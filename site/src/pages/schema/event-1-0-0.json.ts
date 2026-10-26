import { readFileSync } from 'node:fs';
export function GET() { return new Response(readFileSync('../schema/event.schema.json', 'utf8'), {headers:{'Content-Type':'application/schema+json; charset=utf-8'}}); }
