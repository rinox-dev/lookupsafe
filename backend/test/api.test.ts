import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import app from '../src/index';
import { analyze } from '../src/analysis';

// Execute real migration/SQL in SQLite. Only the D1 transport and Supabase network are adapted.
let sqlite: DatabaseSync;
let env: any;
function statement(sql: string, args: any[] = []): any {
  return {
    bind: (...values: any[]) => statement(sql, values),
    first: async () => sqlite.prepare(sql).get(...args) ?? null,
    all: async () => ({ results: sqlite.prepare(sql).all(...args) }),
    run: async () => ({ meta: { changes: Number(sqlite.prepare(sql).run(...args).changes) } }),
  };
}
const call = (path: string, method = 'GET', data?: unknown, user = 'alice') => app.request(path, {
  method, headers: { Authorization: `Bearer ${user}`, 'Content-Type':'application/json' },
  body: data === undefined ? undefined : JSON.stringify(data),
}, env);
beforeEach(() => {
  sqlite = new DatabaseSync(':memory:');
  sqlite.exec(readFileSync(new URL('../migrations/0001_initial.sql', import.meta.url), 'utf8'));
  env = { DB: { prepare: statement, batch: async (s: any[]) => Promise.all(s.map(x=>x.run())) }, SUPABASE_URL: 'https://project.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'public-test-key' };
  vi.stubGlobal('fetch', vi.fn(async (_url, options) => {
    const token = options.headers.Authorization.replace('Bearer ', '');
    return token === 'invalid' ? new Response('{}',{status:401}) : Response.json({id:token});
  }));
});
afterEach(() => { sqlite.close(); vi.unstubAllGlobals(); });
describe('authorization and storage',()=>{
  it('exposes health without auth, requires verified auth for all data',async()=>{
    expect((await app.request('/health',{},env)).status).toBe(200);
    expect((await app.request('/v1/scans',{},env)).status).toBe(401);
    expect((await call('/v1/scans','GET',undefined,'invalid')).status).toBe(401);
  });
  it('creates, reads, favorites and deletes a scan for its owner only',async()=>{
    await call('/v1/profile','PUT',{displayName:'Alice',allergens:['milk']});
    const created=await call('/v1/scans','POST',{productName:'Galletas',labelText:'Trigo, leche, azúcar'});
    expect(created.status).toBe(201);
    const scan:any=await created.json();
    expect(scan.analysis.status).toBe('personal_match');
    expect(scan.analysis.score).toBeNull();
    expect((await call('/v1/scans/'+scan.id)).status).toBe(200);
    for(const method of ['GET','PATCH','DELETE']) expect((await call('/v1/scans/'+scan.id,method,method==='PATCH'?{favorite:true}:undefined,'bob')).status).toBe(404);
    expect((await (await call('/v1/scans','GET',undefined,'bob')).json() as any).items).toEqual([]);
    const favorite:any=await (await call('/v1/scans/'+scan.id,'PATCH',{favorite:true})).json();
    expect(favorite.favorite).toBe(true);
    expect((await call('/v1/scans/'+scan.id,'DELETE')).status).toBe(204);
    expect((await call('/v1/scans/'+scan.id)).status).toBe(404);
  });
  it('rejects malformed, excessive and attacker-controlled fields',async()=>{
    expect((await call('/v1/scans','POST',{productName:'',labelText:'milk'})).status).toBe(400);
    expect((await call('/v1/scans','POST',{productName:'Test',labelText:'milk',userId:'bob'})).status).toBe(400);
    expect((await call('/v1/profile','PUT',{displayName:'A',allergens:['invented']})).status).toBe(400);
    expect((await call('/v1/profile','PUT',{displayName:'A',allergens:['fragrance','linalool','methylisothiazolinone','aluminum_compounds']})).status).toBe(200);
    expect((await call('/v1/scans?limit=-1')).status).toBe(400);
    expect((await call('/v1/scans','POST',{productName:'T',labelText:'x'.repeat(25000)})).status).toBe(413);
    expect((await app.request('/v1/scans',{method:'POST',headers:{Authorization:'Bearer alice'},body:'{'},env)).status).toBe(400);
  });
  it('paginates and parameterizes SQL content',async()=>{
    for(let i=0;i<3;i++) await call('/v1/scans','POST',{productName:i===0?"'; DROP TABLE scans; --":`Product ${i}`,labelText:'milk, salt'});
    const first:any=await (await call('/v1/scans?limit=2')).json();
    const last:any=await (await call('/v1/scans?limit=2&offset=2')).json();
    expect(first.items).toHaveLength(2); expect(first.nextOffset).toBe(2);
    expect(last.items).toHaveLength(1); expect(last.nextOffset).toBeNull();
    expect(new Set([...first.items,...last.items].map(s=>s.id)).size).toBe(3);
  });
  it('deletes only the authenticated users data',async()=>{
    for(const user of ['alice','bob']) {
      await call('/v1/scans','POST',{productName:'A',labelText:'salt'},user);
      await call('/v1/profile','PUT',{displayName:user,allergens:['soy']},user);
    }
    expect((await call('/v1/data','DELETE')).status).toBe(204);
    expect((await (await call('/v1/scans')).json() as any).items).toHaveLength(0);
    expect((await (await call('/v1/profile')).json() as any).displayName).toBe('');
    expect((await (await call('/v1/scans','GET',undefined,'bob')).json() as any).items).toHaveLength(1);
    expect((await (await call('/v1/profile','GET',undefined,'bob')).json() as any).displayName).toBe('bob');
  });
  it('rejects malformed upstream identity and treats rate limits as unavailable',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response('invalid json')));
    expect((await call('/v1/scans')).status).toBe(401);
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response('{}',{status:429})));
    expect((await call('/v1/scans')).status).toBe(503);
  });
  it('fails closed when auth is unavailable or misconfigured',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('offline')));
    expect((await call('/v1/scans')).status).toBe(503);
    env.SUPABASE_URL='';
    expect((await call('/v1/scans')).status).toBe(503);
  });
});
describe('label matching',()=>{
  it('recognizes food allergens and cosmetic product ingredients',()=>{
    expect(analyze('Alcohol denat., parfum, linalool, limonene, benzyl salicylate, methylisothiazolinone, aluminum chlorohydrate, sodium bicarbonate',['fragrance','linalool']).allergens.map(a=>a.id)).toEqual(['fragrance','linalool','limonene','benzyl_salicylate','methylisothiazolinone','aluminum_compounds','baking_soda']);
  });
  it('recognizes accents and word boundaries while retaining nested ingredients',()=>{
    const result=analyze('Ingredientes: chocolate (azúcar, leche), maní; sal',['peanut']);
    expect(result.ingredients.map(i=>i.name)).toEqual(['chocolate (azúcar, leche)','maní','sal']);
    expect(result.allergens.map(a=>a.id)).toEqual(['milk','peanut']);
    expect(result.status).toBe('personal_match');
    expect(analyze('eggplant, soybean oil',[]).allergens.map(a=>a.id)).toEqual(['soy']);
  });
  it('never presents unmatched or negated text as a safety score',()=>{
    expect(analyze('water, sugar',[])).toMatchObject({status:'unreviewed',score:null});
    expect(analyze('sin leche',[])).toMatchObject({status:'label_match',score:null});
    expect(analyze('sin leche',[]).notice).toContain('negaciones');
  });
});

describe('browser CORS',()=>{
  it('permits an allowed origin preflight without bypassing authentication',async()=>{
    env.WEB_ORIGINS='https://lookupsafe.example,http://localhost:4321';
    const res=await app.request('/v1/scans',{method:'OPTIONS',headers:{Origin:'https://lookupsafe.example','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'authorization,content-type'}},env);
    expect(res.status).toBe(204);
    expect(res.headers.get('Access-Control-Allow-Origin')).toBe('https://lookupsafe.example');
    expect(res.headers.get('Access-Control-Allow-Headers')).toContain('Authorization');
    const unauth=await app.request('/v1/scans',{headers:{Origin:'https://lookupsafe.example'}},env);
    expect(unauth.status).toBe(401);
    expect(unauth.headers.get('Access-Control-Allow-Origin')).toBe('https://lookupsafe.example');
  });
  it('does not grant browser access to arbitrary origins or null origins',async()=>{
    env.WEB_ORIGINS='https://lookupsafe.example';
    for(const origin of ['https://evil.example','https://lookupsafe.example.evil.test','null']) {
      const res=await app.request('/v1/scans',{method:'OPTIONS',headers:{Origin:origin,'Access-Control-Request-Method':'GET'}},env);
      expect(res.headers.get('Access-Control-Allow-Origin')).toBeNull();
    }
  });
  it('has no cross-origin grants by default and preserves native access',async()=>{
    const res=await app.request('/v1/scans',{method:'OPTIONS',headers:{Origin:'http://localhost:4321','Access-Control-Request-Method':'GET'}},env);
    expect(res.headers.get('Access-Control-Allow-Origin')).toBeNull();
    expect((await call('/v1/scans')).status).toBe(200);
  });
});
