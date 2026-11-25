import { Hono, type Context } from 'hono';
import { bodyLimit } from 'hono/body-limit';
import { secureHeaders } from 'hono/secure-headers';
import { cors } from 'hono/cors';
import { HTTPException } from 'hono/http-exception';
import { z } from 'zod';
import { analyze, concernIds } from './analysis';

type Env = { Bindings:{DB:D1Database;SUPABASE_URL:string;SUPABASE_PUBLISHABLE_KEY:string;WEB_ORIGINS?:string}; Variables:{userId:string} };
type Scan = {id:string;user_id:string;product_name:string;label_text:string;analysis_json:string;favorite:number;created_at:string};
const app = new Hono<Env>();
app.use('*',secureHeaders());
// Exact origin allowlist. Native Android requests have no Origin header.
app.use('/v1/*', cors({
  origin: (origin,c) => String(c.env.WEB_ORIGINS ?? '').split(',').map(s=>s.trim()).filter(Boolean).includes(origin) ? origin : undefined,
  allowMethods: ['GET','POST','PUT','PATCH','DELETE','OPTIONS'],
  allowHeaders: ['Authorization','Content-Type'],
  maxAge: 600,
}));
app.use('*',bodyLimit({maxSize:24_000,onError:c=>c.json({error:'Request too large'},413)}));
app.get('/health',c=>c.json({status:'ok',app:'lookupsafe'}));
app.use('/v1/*',async(c,next)=>{
  c.header('Cache-Control','no-store');
  const token = c.req.header('Authorization')?.match(/^Bearer (\S+)$/i)?.[1];
  if(!token) return c.json({error:'Authentication required'},401);
  if(!c.env.SUPABASE_URL || !c.env.SUPABASE_PUBLISHABLE_KEY) return c.json({error:'Authentication is not configured'},503);
  let response:Response;
  try {
    response=await fetch(`${c.env.SUPABASE_URL.replace(/\/$/,'')}/auth/v1/user`,{headers:{apikey:c.env.SUPABASE_PUBLISHABLE_KEY,Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(8000)});
  } catch { return c.json({error:'Authentication service unavailable'},503); }
  if(!response.ok) {
    const unavailable=response.status>=500 || response.status===429;
    return c.json({error:unavailable?'Authentication service unavailable':'Invalid or expired session'},unavailable?503:401);
  }
  const user=await response.json().catch(()=>null) as {id?:string} | null;
  if(!user || typeof user.id!=='string' || !user.id) return c.json({error:'Invalid session'},401);
  c.set('userId',user.id);
  await next();
});
async function body(c: Context<Env>) { // JSON parsing errors must be 400, never 500
  try { return await c.req.json(); } catch { throw new HTTPException(400,{message:'Invalid JSON body'}); }
}
const scanInput=z.object({productName:z.string().trim().min(1).max(120),labelText:z.string().trim().min(2).max(12000)}).strict();
const profileInput=z.object({displayName:z.string().trim().max(80),allergens:z.array(z.enum(concernIds)).max(26).transform(a=>[...new Set(a)])}).strict();
const dto=(s:Scan)=>({id:s.id,productName:s.product_name,labelText:s.label_text,analysis:JSON.parse(s.analysis_json),favorite:!!s.favorite,createdAt:s.created_at});
app.get('/v1/profile',async c=>{
  const p=await c.env.DB.prepare('SELECT display_name, allergens_json FROM profiles WHERE user_id = ?').bind(c.get('userId')).first<{display_name:string;allergens_json:string}>();
  return c.json({displayName:p?.display_name??'',allergens:JSON.parse(p?.allergens_json??'[]')});
});
app.put('/v1/profile',async c=>{
  const p=profileInput.parse(await body(c));
  await c.env.DB.prepare('INSERT INTO profiles (user_id,display_name,allergens_json,updated_at) VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name,allergens_json=excluded.allergens_json,updated_at=excluded.updated_at')
    .bind(c.get('userId'),p.displayName,JSON.stringify(p.allergens),new Date().toISOString()).run();
  return c.json(p);
});
app.post('/v1/scans',async c=>{
  const input=scanInput.parse(await body(c));
  const profile=await c.env.DB.prepare('SELECT allergens_json FROM profiles WHERE user_id = ?').bind(c.get('userId')).first<{allergens_json:string}>();
  const analysis=analyze(input.labelText,JSON.parse(profile?.allergens_json??'[]'));
  const scan={id:crypto.randomUUID(),productName:input.productName,labelText:input.labelText,analysis,favorite:false,createdAt:new Date().toISOString()};
  await c.env.DB.prepare('INSERT INTO scans (id,user_id,product_name,label_text,analysis_json,created_at) VALUES (?,?,?,?,?,?)')
    .bind(scan.id,c.get('userId'),scan.productName,scan.labelText,JSON.stringify(analysis),scan.createdAt).run();
  return c.json(scan,201);
});
app.get('/v1/scans',async c=>{
  const limit=z.coerce.number().int().min(1).max(100).parse(c.req.query('limit')??30);
  const offset=z.coerce.number().int().min(0).max(100000).parse(c.req.query('offset')??0);
  const rows=await c.env.DB.prepare('SELECT * FROM scans WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?').bind(c.get('userId'),limit+1,offset).all<Scan>();
  return c.json({items:rows.results.slice(0,limit).map(dto),nextOffset:rows.results.length>limit?offset+limit:null});
});
app.get('/v1/scans/:id',async c=>{
  const row=await c.env.DB.prepare('SELECT * FROM scans WHERE id = ? AND user_id = ?').bind(c.req.param('id'),c.get('userId')).first<Scan>();
  return row?c.json(dto(row)):c.json({error:'Scan not found'},404);
});
app.patch('/v1/scans/:id',async c=>{
  const {favorite}=z.object({favorite:z.boolean()}).strict().parse(await body(c));
  const row=await c.env.DB.prepare('UPDATE scans SET favorite = ? WHERE id = ? AND user_id = ? RETURNING *').bind(favorite?1:0,c.req.param('id'),c.get('userId')).first<Scan>();
  return row?c.json(dto(row)):c.json({error:'Scan not found'},404);
});
app.delete('/v1/scans/:id',async c=>{
  const result=await c.env.DB.prepare('DELETE FROM scans WHERE id = ? AND user_id = ?').bind(c.req.param('id'),c.get('userId')).run();
  return result.meta.changes?c.body(null,204):c.json({error:'Scan not found'},404);
});
app.delete('/v1/data',async c=>{
  await c.env.DB.batch([c.env.DB.prepare('DELETE FROM scans WHERE user_id = ?').bind(c.get('userId')),c.env.DB.prepare('DELETE FROM profiles WHERE user_id = ?').bind(c.get('userId'))]);
  return c.body(null,204);
});
app.notFound(c=>c.json({error:'Not found'},404));
app.onError((err,c)=>{
  if(err instanceof z.ZodError) return c.json({error:'Invalid input',issues:err.issues.map(i=>({path:i.path,message:i.message}))},400);
  if(err instanceof HTTPException) return c.json({error:err.message},err.status);
  // Do not log labels, bearer tokens, or upstream responses.
  console.error('API operation failed',err.name);
  return c.json({error:'Unable to complete request'},500);
});
export default app;
