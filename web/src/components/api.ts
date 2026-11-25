import { createClient, type SupabaseClient } from '@supabase/supabase-js';
const url=import.meta.env.PUBLIC_SUPABASE_URL ?? '';
const key=import.meta.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? '';
export const configured=url.startsWith('https://') && !url.includes('YOUR_PROJECT') && !!key && !key.startsWith('YOUR_');
let client: SupabaseClient | null=null;
export function getAuth() {
  if(!configured) return null;
  return client ??= createClient(url,key,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
}
export async function api<T>(path:string,method='GET',body?:unknown,signal?:AbortSignal):Promise<T> {
  const auth=getAuth();
  if(!auth) throw new Error('El acceso con cuenta aún no está disponible. Puedes explorar la vista de ejemplo.');
  const {data,error}=await auth.auth.getSession();
  if(error || !data.session) throw new Error('Inicia sesión para continuar.');
  const response=await fetch(`${(import.meta.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8787').replace(/\/$/,'')}/v1/${path}`,{
    method,headers:{Authorization:`Bearer ${data.session.access_token}`,...(body===undefined?{}:{'Content-Type':'application/json'})},
    body:body===undefined?undefined:JSON.stringify(body),signal:signal ?? AbortSignal.timeout(20000),
  });
  if(!response.ok) {
    const payload=await response.json().catch(()=>null);
    if(response.status===401) throw new Error('Tu sesión no es válida. Cierra sesión y vuelve a entrar.');
    throw new Error(payload?.error ?? 'No pudimos completar la solicitud. Intenta de nuevo.');
  }
  return response.status===204 ? undefined as T : await response.json() as T;
}
