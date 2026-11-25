import { useEffect, useRef, useState, type SubmitEvent, type ReactNode } from 'react';
import type { Session } from '@supabase/supabase-js';
import { ShieldCheck, LayoutDashboard, ScanLine, History, Bookmark, UserRound, LogOut, Moon, Sun, Plus, Camera, Upload, Search, Leaf, Milk, Wheat, X, Check, Info, BookOpen, Download, Trash2, RefreshCw, LoaderCircle, Menu, CheckCheck, Fingerprint, SlidersHorizontal } from 'lucide-react';
import { analyze } from '../../../shared/analysis';
import { api, configured, getAuth } from './api';
import { allergens, concernGroups, dateLabel, demoProfile, demoScans, type Profile, type Scan, type ScanPage } from './data';
import { exportScan } from './export';

type Tab='home'|'scan'|'history'|'favorites'|'profile';
const nav: {id:Tab;label:string;icon:typeof ScanLine}[]=[{id:'home',label:'Inicio',icon:LayoutDashboard},{id:'scan',label:'Escanear etiqueta',icon:ScanLine},{id:'history',label:'Mi historial',icon:History},{id:'favorites',label:'Favoritos',icon:Bookmark}];

function Modal({title,children,onClose}:{title:string;children:ReactNode;onClose:()=>void}) {
  const ref=useRef<HTMLDialogElement>(null);
  useEffect(()=>{const dialog=ref.current!;dialog.showModal();return()=>dialog.close();},[]);
  return <dialog ref={ref} className="modal" onCancel={e=>{e.preventDefault();onClose();}} onClick={e=>{if(e.target===ref.current) onClose();}} aria-labelledby="modal-title">
    <header><h2 id="modal-title">{title}</h2><button className="icon-button" onClick={onClose} aria-label="Cerrar ventana"><X size={20}/></button></header>{children}
  </dialog>;
}
function LabelArt() {
  return <div className="label-art" aria-hidden="true"><div className="art-ring"/><div className="art-package"><div className="package-band"><Leaf size={28}/><span>LO NATURAL<br/><b>empieza aquí.</b></span></div><div className="package-label"><span className="tiny-label">INGREDIENTES</span><div className="label-line wide"/><div className="label-line"/><div className="label-line wide"/><div className="label-line short"/><div className="barcode"/></div></div><div className="scan-corner tl"/><div className="scan-corner tr"/><div className="scan-corner bl"/><div className="scan-corner br"/><div className="art-caption"><span><Check size={15}/></span> Una etiqueta, más información</div></div>;
}
function ProductIcon({name}:{name:string}) {const Icon=/yogur|leche/i.test(name)?Milk:/galleta|trigo/i.test(name)?Wheat:Leaf;return <span className={`product-icon ${Icon===Milk?'blue':Icon===Wheat?'sand':''}`}><Icon size={24} strokeWidth={1.5}/></span>;}
async function enhanceLabelImage(file:File):Promise<Blob> {
  const bitmap=await createImageBitmap(file);
  try {
    const scale=Math.min(2.5,2400/Math.max(bitmap.width,bitmap.height));
    const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(bitmap.width*scale));canvas.height=Math.max(1,Math.round(bitmap.height*scale));
    const context=canvas.getContext('2d');if(!context)throw new Error('No se pudo preparar la foto.');
    context.filter='grayscale(1) contrast(1.35) brightness(1.04)';context.drawImage(bitmap,0,0,canvas.width,canvas.height);
    return await new Promise<Blob>((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('No se pudo preparar la foto.')),'image/png'));
  } finally {bitmap.close();}
}

export default function App() {
  const [session,setSession]=useState<Session|null>(null);
  const [tab,setTab]=useState<Tab>('home');
  const [scans,setScans]=useState<Scan[]>(demoScans);
  const [profile,setProfile]=useState<Profile>(demoProfile);
  const [nextOffset,setNextOffset]=useState<number|null>(null);
  const [selected,setSelected]=useState<Scan|null>(null);
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState<{text:string;error?:boolean}|null>(null);
  const [authOpen,setAuthOpen]=useState(false);
  const [helpOpen,setHelpOpen]=useState(false);
  const [confirmation,setConfirmation]=useState<'scan'|'data'|null>(null);
  const [mobileNav,setMobileNav]=useState(false);
  const [dark,setDark]=useState(false);
  const [query,setQuery]=useState('');
  const generation=useRef(0);
  const operation=useRef(false);
  const demo=!session;
  useEffect(()=>{window.scrollTo(0,0);},[tab,selected?.id]);
  useEffect(()=>{
    if(!mobileNav)return;
    const close=(event:KeyboardEvent)=>{if(event.key==='Escape')setMobileNav(false);};
    window.addEventListener('keydown',close);
    return()=>window.removeEventListener('keydown',close);
  },[mobileNav]);
  useEffect(()=>{
    let stored:string|null=null;try{stored=localStorage.getItem('lookupsafe-theme');}catch{}
    setDark(stored ? stored==='dark' : window.matchMedia('(prefers-color-scheme: dark)').matches);
    const auth=getAuth();if(!auth) return;
    const {data:{subscription}}=auth.auth.onAuthStateChange((_event,next)=>setSession(next));
    return ()=>subscription.unsubscribe();
  },[]);
  useEffect(()=>{document.documentElement.dataset.theme=dark?'dark':'light';},[dark]);
  useEffect(()=>{
    generation.current++;
    setSelected(null);setNextOffset(null);setMessage(null);
    if(!session) {setScans(demoScans());setProfile(demoProfile);setBusy(false);return;}
    setScans([]);setProfile({displayName:'',allergens:[]});setBusy(true);
    const controller=new AbortController(); const current=generation.current;
    const timer=setTimeout(()=>controller.abort(),20000);
    Promise.all([api<Profile>('profile','GET',undefined,controller.signal),api<ScanPage>('scans','GET',undefined,controller.signal)])
      .then(([p,page])=>{if(current===generation.current){setProfile(p);setScans(page.items);setNextOffset(page.nextOffset);}})
      .catch(e=>{if(current===generation.current)setMessage({text:e.name==='AbortError'?'La solicitud tardó demasiado. Vuelve a intentar.':e.message,error:true});})
      .finally(()=>{clearTimeout(timer);if(current===generation.current)setBusy(false);});
    return()=>{controller.abort();clearTimeout(timer);};
  },[session?.user.id]);
  function navigate(to:Tab) {setTab(to);setSelected(null);setMobileNav(false);setMessage(null);}
  async function perform(work:(current:number)=>Promise<void>) {
    if(operation.current || busy) return;
    operation.current=true;setBusy(true);setMessage(null);const current=generation.current;
    try{await work(current);}catch(e){if(current===generation.current)setMessage({text:e instanceof Error?e.message:'No pudimos completar la solicitud.',error:true});}
    finally{operation.current=false;if(current===generation.current)setBusy(false);}
  }
  const isCurrent=(n:number)=>n===generation.current;
  async function reload() {await perform(async n=>{
    if(demo){setMessage({text:'Estás viendo datos de ejemplo. Inicia sesión para sincronizar tus consultas.'});return;}
    const [p,page]=await Promise.all([api<Profile>('profile'),api<ScanPage>('scans')]);
    if(isCurrent(n)){setProfile(p);setScans(page.items);setNextOffset(page.nextOffset);}
  });}
  function createScan(name:string,label:string) {return perform(async n=>{
    const result:Scan=demo?{id:crypto.randomUUID(),productName:name.trim(),labelText:label.trim(),analysis:analyze(label,profile.allergens),favorite:false,createdAt:new Date().toISOString()}:await api<Scan>('scans','POST',{productName:name.trim(),labelText:label.trim()});
    if(isCurrent(n)){setScans(s=>[result,...s]);setSelected(result);setTab('history');}
  });}
  function toggleFavorite(scan:Scan) {void perform(async n=>{
    const result=demo?{...scan,favorite:!scan.favorite}:await api<Scan>(`scans/${scan.id}`,'PATCH',{favorite:!scan.favorite});
    if(isCurrent(n)){setScans(s=>s.map(x=>x.id===result.id?result:x));setSelected(s=>s?.id===result.id?result:s);}
  });}
  function saveProfile(p:Profile) {void perform(async n=>{
    const result=demo?p:await api<Profile>('profile','PUT',p);
    if(isCurrent(n)){setProfile(result);setMessage({text:demo?'Preferencias actualizadas solo en esta vista de ejemplo.':'Perfil guardado. Se aplicará a tus próximos análisis.'});}
  });}
  function deleteConfirmed() {const kind=confirmation;const scan=selected;setConfirmation(null);void perform(async n=>{
    if(kind==='scan' && scan){if(!demo)await api(`scans/${scan.id}`,'DELETE');if(isCurrent(n)){setScans(s=>s.filter(x=>x.id!==scan.id));setSelected(null);setNextOffset(null);if(!demo){const page=await api<ScanPage>('scans');if(isCurrent(n)){setScans(page.items);setNextOffset(page.nextOffset);}}}}
    if(kind==='data'){if(!demo)await api('data','DELETE');if(isCurrent(n)){setScans([]);setProfile({displayName:'',allergens:[]});setSelected(null);setNextOffset(null);setMessage({text:'Historial y perfil eliminados. Tu cuenta de acceso permanece activa.'});}}
  });}
  function signOut() {void perform(async()=>{
    const auth=getAuth();if(auth){const {error}=await auth.auth.signOut({scope:'local'});if(error)throw error;}
    setSession(null);navigate('home');
  });}
  function more() {void perform(async n=>{if(nextOffset===null)return;const page=await api<ScanPage>(`scans?offset=${nextOffset}`);if(isCurrent(n)){setScans(s=>Array.from(new Map([...s,...page.items].map(x=>[x.id,x])).values()));setNextOffset(page.nextOffset);}});}
  const filtered=scans.filter(s=>s.productName.toLocaleLowerCase().includes(query.toLocaleLowerCase()) && (tab!=='favorites'||s.favorite));
  const tabName=selected?'Detalle de consulta':tab==='profile'?'Mi perfil':nav.find(n=>n.id===tab)?.label;
  function scanList(list:Scan[]) {return list.length?<div className="scan-list">{list.map(scan=><div className="scan-row" key={scan.id}>
    <button className="scan-open" onClick={()=>setSelected(scan)}><ProductIcon name={scan.productName}/><span className="scan-title"><strong>{scan.productName}</strong><small>{scan.analysis.ingredients.length} ingredientes · {dateLabel(scan.createdAt)}</small></span><span className={`status-pill ${scan.analysis.allergens.some(a=>a.personal)?'attention':''}`}>{`${scan.analysis.allergens.length} ${scan.analysis.allergens.length===1?'coincidencia':'coincidencias'}`}</span></button>
    <button className={`icon-button favorite ${scan.favorite?'active':''}`} onClick={()=>toggleFavorite(scan)} disabled={busy} aria-label={`${scan.favorite?'Quitar de':'Añadir a'} favoritos: ${scan.productName}`} aria-pressed={scan.favorite}><Bookmark size={19} fill={scan.favorite?'currentColor':'none'}/></button>
  </div>)}</div>:<div className="empty"><ScanLine size={32}/><h3>Aquí empieza tu historial</h3><p>{query?'No hay consultas que coincidan con tu búsqueda.':'Escanea una etiqueta y conserva lo que aprendes.'}</p><button className="button secondary" onClick={()=>navigate('scan')}>Escanear una etiqueta</button></div>;}
  return <div className="app-shell">
    <a className="skip-link" href="#main">Saltar al contenido</a>
    {mobileNav&&<button className="nav-scrim" aria-label="Cerrar menú" onClick={()=>setMobileNav(false)}/>}
    <aside id="sidebar-menu" className={`sidebar ${mobileNav?'open':''}`}>
      <a className="brand" href="/" aria-label="lookupsafe inicio"><span className="brand-mark"><ShieldCheck size={24}/></span>lookupsafe<span className="brand-dot">.</span></a>
      <div className="workspace-label">TU ESPACIO DE BIENESTAR</div>
      <nav aria-label="Navegación principal">{nav.map(({id,label,icon:Icon})=><button key={id} className={`nav-item ${tab===id&&!selected?'active':''}`} onClick={()=>navigate(id)} aria-current={tab===id&&!selected?'page':undefined}><Icon size={20}/>{label}{id==='favorites'&&<span className="nav-count">{scans.filter(s=>s.favorite).length}</span>}</button>)}</nav>
      <div className="sidebar-tip"><div className="tip-symbol"><Leaf size={22}/></div><h3>Pequeñas decisiones.<br/>Más información.</h3><p>Conocer la etiqueta es un buen lugar para empezar.</p><button onClick={()=>setHelpOpen(true)}>Conoce cómo funciona <Plus size={15}/></button></div>
      <div className="sidebar-bottom"><button className={`nav-item ${tab==='profile'?'active':''}`} onClick={()=>navigate('profile')}><UserRound size={20}/>Mi perfil</button><button className="nav-item" onClick={()=>setHelpOpen(true)}><BookOpen size={20}/>Guía de uso</button><div className="sidebar-footer"><ShieldCheck size={15}/><span>Información para decidir mejor</span></div></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb"><button className="icon-button mobile-menu" onClick={()=>setMobileNav(!mobileNav)} aria-label="Abrir menú" aria-expanded={mobileNav} aria-controls="sidebar-menu"><Menu size={22}/></button><span>Mi espacio</span><span className="breadcrumb-divider">/</span><strong>{tabName}</strong></div><div className="top-actions"><span className={`mode-pill ${demo?'':'connected'}`}><span/>{demo?'Vista de ejemplo':'Mi cuenta'}</span><button className="icon-button theme-toggle" aria-label={dark?'Usar tema claro':'Usar tema oscuro'} onClick={()=>{setDark(!dark);try{localStorage.setItem('lookupsafe-theme',dark?'light':'dark');}catch{}}}>{dark?<Sun size={20}/>:<Moon size={20}/>}</button>{session?<button className="avatar" onClick={()=>navigate('profile')} aria-label="Abrir mi perfil">{(profile.displayName||session.user.email||'U').slice(0,1).toUpperCase()}</button>:<button className="button small secondary" onClick={()=>setAuthOpen(true)}>Iniciar sesión</button>}</div></header>
      <main id="main" className="main-content" tabIndex={-1}>
        {demo&&<div className="demo-banner"><Info size={16}/><span>Explora con datos de ejemplo. Tus cambios duran hasta que recargues la página.</span><button onClick={()=>setAuthOpen(true)}>Guardar en mi cuenta</button></div>}
        {message&&<div className={`notice ${message.error?'error':''}`} role={message.error?'alert':'status'}><Info size={18}/><span>{message.text}</span><button className="icon-button" onClick={()=>setMessage(null)} aria-label="Cerrar aviso"><X size={17}/></button></div>}
        {busy&&<div className="loading" role="status"><LoaderCircle className="spin" size={17}/> Actualizando tu información…</div>}
        {selected?<Detail scan={selected} demo={demo} busy={busy} onBack={()=>setSelected(null)} onFavorite={()=>toggleFavorite(selected)} onDelete={()=>setConfirmation('scan')} onExport={()=>void perform(async()=>{await exportScan(selected,demo);})}/>:
        tab==='home'?<>
          <section className="page-heading"><div><div className="eyebrow">INFORMACIÓN PARA CADA PRODUCTO</div><h1>{profile.displayName?`Hola, ${profile.displayName}.`:'Una etiqueta. Más claridad.'}</h1><p>Revisa alimentos, perfumes, desodorantes, cosméticos, champús y otros productos.</p></div><span className="heading-note"><Leaf size={17}/> Elige con información</span></section>
          <div className="dashboard-grid"><div className="dashboard-primary">
            <section className="hero"><div className="hero-copy"><span className="hero-kicker"><ScanLine size={16}/> ALIMENTOS, PERFUMES, CUIDADO PERSONAL</span><h2>Entiende la etiqueta.<br/>Decide por ti.</h2><p>Lee los ingredientes de productos de uso diario y busca componentes que te interesen.</p><button className="button hero-button" onClick={()=>navigate('scan')}><Camera size={19}/>Revisar producto</button><small><CheckCheck size={15}/> Foto o texto. Tú eliges.</small></div><LabelArt/></section>
        <div className="metrics"><div><span className="metric-icon"><ScanLine size={20}/></span><div><strong>{scans.length}{nextOffset!==null?'+':''}</strong><span>Consultas cargadas</span></div></div><div><span className="metric-icon warm"><Bookmark size={20}/></span><div><strong>{scans.filter(s=>s.favorite).length}</strong><span>Productos favoritos</span></div></div><div><span className="metric-icon lilac"><SlidersHorizontal size={20}/></span><div><strong>{profile.allergens.length}</strong><span>Ingredientes de interés</span></div></div></div>
            <section className="panel recent-panel"><div className="section-heading"><div><h2>{demo?'Consultas de ejemplo':'Últimas consultas'}</h2><p>Un lugar para volver a lo que descubriste.</p></div><button className="text-button" onClick={()=>navigate('history')}>Ver historial</button></div>{scanList(scans.slice(0,4))}</section>
          </div><div className="dashboard-secondary">
            <section className="panel profile-card"><span className="card-icon"><Fingerprint size={25}/></span><h2>Tu etiqueta,<br/>tu contexto.</h2><p>Elige ingredientes que quieres tener presentes al revisar cualquier producto.</p><div className="profile-tags">{profile.allergens.length?profile.allergens.map(id=><span key={id}>{allergens[id]}</span>):<span>Sin preferencias todavía</span>}</div><button className="button secondary full" onClick={()=>navigate('profile')}><SlidersHorizontal size={17}/>Personalizar mi perfil</button><small>Se aplicará a tus próximos análisis.</small></section>
            <section className="how-card"><div className="how-icon"><BookOpen size={21}/></div><h3>¿Qué te dice una etiqueta?</h3><p>Aprende a interpretar las menciones, las trazas y el alcance de cada resultado.</p><button className="text-button" onClick={()=>setHelpOpen(true)}>Leer la guía</button></section>
            <div className="privacy-note"><ShieldCheck size={21}/><p><strong>Tus fotos se quedan contigo.</strong>El texto se reconoce en tu navegador. Solo envías los ingredientes que revises.</p></div>
          </div></div>
          <section className="bottom-note"><Info size={17}/><p>Más contexto, mejores preguntas. lookupsafe identifica coincidencias de texto; no evalúa ni certifica la seguridad de productos.</p></section>
        </>:tab==='scan'?<ScanForm busy={busy} demo={demo} onSubmit={createScan} onError={text=>setMessage({text,error:true})}/>:
        tab==='profile'?<ProfileView profile={profile} email={session?.user.email} demo={demo} busy={busy} onSave={saveProfile} onDelete={()=>setConfirmation('data')} onSignOut={signOut} onLogin={()=>setAuthOpen(true)}/>:
        <><section className="page-heading"><div><div className="eyebrow">TU BIBLIOTECA PERSONAL</div><h1>{tab==='favorites'?'A mano para la próxima vez.':'Cada consulta, en un lugar.'}</h1><p>{tab==='favorites'?'Los productos que elegiste conservar.':'Revisa lo que aprendiste de tus etiquetas.'}</p></div><button className="button" onClick={()=>navigate('scan')}><Plus size={18}/>Nueva consulta</button></section><section className="panel history-panel"><div className="history-toolbar"><label className="search"><Search size={19}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Buscar en consultas cargadas" aria-label="Buscar en consultas cargadas"/></label><button className="icon-button" onClick={()=>void reload()} disabled={busy} aria-label="Actualizar historial"><RefreshCw size={19}/></button></div>{scanList(filtered)}{nextOffset!==null&&<button className="button secondary load-more" disabled={busy} onClick={more}>Cargar más consultas</button>}</section></>}
        <footer className="content-footer"><span>lookupsafe <span className="footer-dot">·</span> Decisiones de consumo informadas</span><button onClick={()=>setHelpOpen(true)}>Alcance y privacidad</button></footer>
      </main>
    </div>
    {authOpen&&<AuthModal onClose={()=>setAuthOpen(false)} onSignedIn={()=>{setAuthOpen(false);setTab('home');}}/>}
    {helpOpen&&<Modal title="Una etiqueta, paso a paso" onClose={()=>setHelpOpen(false)}><div className="guide"><article><Camera/><div><h3>Captura o escribe</h3><p>Usa una foto nítida de los ingredientes o pega el texto. La lectura de imágenes se realiza en tu navegador.</p></div></article><article><CheckCheck/><div><h3>Revisa antes de analizar</h3><p>Corrige el texto reconocido e incluye todas las advertencias visibles. Solo este texto se envía a tu cuenta.</p></div></article><article><BookOpen/><div><h3>Interpreta con contexto</h3><p>Buscamos coincidencias exactas en un catálogo limitado de ingredientes de interés. No evaluamos concentración, exposición, fórmula completa o seguridad. Los efectos dependen del producto, su uso y cada persona.</p></div></article><p className="guide-privacy">Con cuenta, Supabase gestiona tu acceso y Cloudflare guarda tu historial. Puedes borrar historial y preferencias desde tu perfil. La vista de ejemplo solo vive en esta página. Al importar una foto se descargan los modelos de reconocimiento; la imagen no se sube.</p><a className="text-button" href="https://www.fda.gov/cosmetics/cosmetics-science-research/it-here-cosmetics" target="_blank" rel="noopener noreferrer">Consultar información de la FDA sobre cosméticos</a></div></Modal>}
    {confirmation&&<Modal title={confirmation==='scan'?'¿Eliminar esta consulta?':'¿Eliminar tu historial y perfil?'} onClose={()=>setConfirmation(null)}><p className="dialog-copy">{confirmation==='scan'?'La consulta se eliminará de tu historial.':'Se borrarán todas tus consultas y preferencias. Tu cuenta de Supabase seguirá activa.'} Esta acción no se puede deshacer.</p><div className="dialog-actions"><button className="button secondary" onClick={()=>setConfirmation(null)}>Cancelar</button><button className="button danger" onClick={deleteConfirmed}>Eliminar</button></div></Modal>}
  </div>;
}

function AuthModal({onClose,onSignedIn}:{onClose:()=>void;onSignedIn:()=>void}) {
  const [signup,setSignup]=useState(false);const [loading,setLoading]=useState(false);const [message,setMessage]=useState('');
  async function submit(e:SubmitEvent<HTMLFormElement>) {e.preventDefault();if(loading)return;const data=new FormData(e.currentTarget);setLoading(true);setMessage('');
    try{const auth=getAuth();if(!auth)throw new Error('El acceso con cuenta aún no está configurado. La vista de ejemplo está disponible.');
      const credentials={email:String(data.get('email')).trim(),password:String(data.get('password'))};
      const result=signup?await auth.auth.signUp({...credentials,options:{emailRedirectTo:window.location.origin+'/'}}):await auth.auth.signInWithPassword(credentials);
      if(result.error)throw result.error;
      if(result.data.session)onSignedIn();else setMessage('Revisa tu correo para confirmar tu cuenta. Después podrás iniciar sesión.');
    }catch(e){setMessage(e instanceof Error?e.message:'No se pudo iniciar sesión.');}finally{setLoading(false);}
  }
  return <Modal title={signup?'Crea tu cuenta':'Bienvenido a lookupsafe'} onClose={onClose}><p className="dialog-copy">Guarda tus consultas y encuentra tu historial también en la app Android.</p><form onSubmit={submit} className="stack-form"><label>Correo electrónico<input autoFocus name="email" type="email" autoComplete="email" required placeholder="tu@correo.com" disabled={loading}/></label><label>Contraseña<input name="password" type="password" autoComplete={signup?'new-password':'current-password'} minLength={signup?8:1} required placeholder={signup?'Al menos 8 caracteres':'Tu contraseña'} disabled={loading}/></label>{!configured&&<p className="inline-note">El acceso con cuenta aún no está disponible en esta instalación. Puedes explorar y probar etiquetas en la vista de ejemplo.</p>}{message&&<p className="inline-note" role="status">{message}</p>}<button className="button full" disabled={loading||!configured}>{loading?<LoaderCircle className="spin" size={18}/>:null}{signup?'Crear cuenta':'Iniciar sesión'}</button><button type="button" className="text-button" disabled={loading} onClick={()=>{setSignup(!signup);setMessage('');}}>{signup?'Ya tengo una cuenta':'Crear una cuenta'}</button></form></Modal>;
}

function ScanForm({busy,demo,onSubmit,onError}:{busy:boolean;demo:boolean;onSubmit:(name:string,label:string)=>Promise<void>;onError:(text:string)=>void}) {
  const [name,setName]=useState('');const [label,setLabel]=useState('');const [progress,setProgress]=useState<number|null>(null);const [preview,setPreview]=useState<string|null>(null);const [ocrConfidence,setOcrConfidence]=useState<number|null>(null);const [retrying,setRetrying]=useState(false);
  const fileInput=useRef<HTMLInputElement>(null);const alive=useRef(true);const workerRef=useRef<{terminate:()=>Promise<unknown>}|null>(null);const reading=useRef(false);
  useEffect(()=>{alive.current=true;return()=>{alive.current=false;const worker=workerRef.current;workerRef.current=null;void worker?.terminate().catch(()=>{});};},[]);
  useEffect(()=>()=>{if(preview)URL.revokeObjectURL(preview);},[preview]);
  async function read(file?:File) {
    if(!file||reading.current||busy)return;
    if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>10*1024*1024){onError('Elige una imagen JPG, PNG o WebP de hasta 10 MB.');return;}
    reading.current=true;setProgress(0);setOcrConfidence(null);setRetrying(false);setPreview(URL.createObjectURL(file));
    try{
      const {createWorker}=await import('tesseract.js');if(!alive.current)return;
      const worker=await createWorker(['spa','eng'],1,{logger:m=>{if(alive.current&&m.status==='recognizing text')setProgress(Math.round(m.progress*100));}});
      if(!alive.current){await worker.terminate();return;}workerRef.current=worker;
      let result=await worker.recognize(file);
      if(result.data.confidence<72&&alive.current){setRetrying(true);setProgress(0);try{const enhanced=await enhanceLabelImage(file);const second=await worker.recognize(enhanced);if(second.data.confidence>result.data.confidence)result=second;}catch{}}
      if(alive.current){setLabel(result.data.text.slice(0,12000));setOcrConfidence(Math.round(result.data.confidence));if(!result.data.text.trim())onError('No se detectó texto. Prueba otra foto o escribe los ingredientes.');}
    }catch{if(alive.current)onError('No pudimos leer la foto. Revisa tu conexión para descargar los modelos o escribe el texto.');}
    finally{const worker=workerRef.current;workerRef.current=null;await worker?.terminate().catch(()=>{});reading.current=false;if(alive.current){setProgress(null);setRetrying(false);}}
  }
  function submit(e:SubmitEvent<HTMLFormElement>) {e.preventDefault();if(progress===null&&!busy)void onSubmit(name,label);}
  return <><section className="page-heading"><div><div className="eyebrow">DE LA ETIQUETA AL CONTEXTO</div><h1>Revisa cualquier producto.</h1><p>Alimentos, perfumes, desodorantes, cosméticos, champús y más.</p></div></section><form onSubmit={submit} className="scan-grid"><section className="panel upload-panel"><div className="section-heading"><h2>Captura la etiqueta</h2><span className="subtle">JPG, PNG o WebP</span></div><div className={`drop-zone ${progress!==null?'reading':''}`} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();void read(e.dataTransfer.files[0]);}}>{preview?<img src={preview} alt="Etiqueta importada para revisar"/>:<span className="upload-symbol"><ScanLine size={44} strokeWidth={1.3}/></span>}<h3 aria-live="polite">{progress!==null?(retrying?`Mejorando lectura… ${progress}%`:`Leyendo ingredientes… ${progress}%`):'Una foto con buena luz.'}</h3><p>Arrastra una foto o selecciona una imagen de la etiqueta.</p><input ref={fileInput} className="visually-hidden" type="file" aria-label="Imagen de etiqueta" accept="image/jpeg,image/png,image/webp" capture="environment" tabIndex={-1} onChange={e=>{void read(e.target.files?.[0]);e.target.value='';}}/><button type="button" className="button secondary" disabled={busy||progress!==null} onClick={()=>fileInput.current?.click()}>{progress!==null?<LoaderCircle className="spin" size={18}/>:<Upload size={18}/>}Seleccionar imagen</button></div><div className="privacy-note"><ShieldCheck size={20}/><p><strong>La imagen permanece en tu navegador.</strong>Solo el texto revisado se usa para el análisis.</p></div></section><section className="panel edit-panel"><h2>Revisa el texto</h2><p>Corrige lo que sea necesario antes de continuar.</p><label>Nombre del producto<input value={name} onChange={e=>setName(e.target.value)} maxLength={120} required placeholder="Por ejemplo, perfume floral o desodorante" disabled={busy}/></label><label>Ingredientes y componentes<textarea value={label} onChange={e=>setLabel(e.target.value)} maxLength={12000} minLength={2} required rows={8} placeholder="Pega o escribe los ingredientes, incluidas todas las advertencias visibles…" disabled={busy||progress!==null}/></label><div className="field-meta"><span>{ocrConfidence!==null?`Lectura OCR: ${ocrConfidence}% · Verifica cada ingrediente.`:'Incluye los nombres y advertencias visibles.'}</span><span>{label.length}/12000</span></div><button className="button full" disabled={busy||progress!==null||!name.trim()||label.trim().length<2}><ScanLine size={18}/>{demo?'Probar análisis de ejemplo':'Analizar y guardar'}</button><small>{demo?'Este resultado solo se conserva mientras esta página esté abierta.':'La consulta se guardará en tu historial privado.'}</small></section></form></>;
}

function Detail({scan,demo,busy,onBack,onFavorite,onDelete,onExport}:{scan:Scan;demo:boolean;busy:boolean;onBack:()=>void;onFavorite:()=>void;onDelete:()=>void;onExport:()=>void}) {
  const personal=scan.analysis.allergens.some(a=>a.personal);
  return <><button className="text-button back-button" onClick={onBack}>Volver a mis consultas</button><section className="page-heading"><div><div className="eyebrow">LECTURA DE ETIQUETA {demo?'· EJEMPLO':''}</div><h1>{scan.productName}</h1><p>{dateLabel(scan.createdAt)} · {scan.analysis.ingredients.length} ingredientes reconocidos</p></div><div className="detail-actions"><button className={`button secondary ${scan.favorite?'saved':''}`} onClick={onFavorite} disabled={busy}><Bookmark size={18} fill={scan.favorite?'currentColor':'none'}/>{scan.favorite?'Guardado':'Guardar favorito'}</button><button className="button" onClick={onExport} disabled={busy}><Download size={18}/>Exportar resumen</button></div></section><div className="detail-grid"><div><section className={`analysis-summary ${personal?'attention':''}`}><Info size={24}/><div><h2>{scan.analysis.summary}</h2><p>Coincidencias de texto. Sin puntuación de seguridad.</p></div></section><section className="panel ingredients-panel"><div className="section-heading"><h2>Ingredientes reconocidos</h2><span className="count-chip">{scan.analysis.ingredients.length}</span></div>{scan.analysis.ingredients.map((i,n)=><details className="ingredient" key={n}><summary><span>{i.name}</span><span className="unreviewed">Texto por revisar <Plus size={15}/></span></summary><p>Este texto se separó de la etiqueta, pero puede contener errores de lectura o varios componentes.</p><EvidenceLookup ingredient={i.name} demo={demo}/></details>)}</section><details className="panel raw-label"><summary>Ver el texto original revisado</summary><p>{scan.labelText}</p></details></div><aside><section className="panel"><h2>Ingredientes de interés</h2><p>Una mención puede ser una advertencia, una traza o una negación.</p><div className="allergen-results">{scan.analysis.allergens.length?scan.analysis.allergens.map(a=><div key={a.id}><span>{a.name}</span>{a.personal?<span className="status-pill attention">Tu perfil</span>:<Check size={17}/>}</div>):<p>Sin coincidencias en el catálogo. No confirma ausencia de ingredientes de interés.</p>}</div></section><section className="source-card"><BookOpen size={22}/><h3>Información con contexto</h3><p>{scan.analysis.notice}</p>{scan.analysis.sources.map(s=><a key={s.url} href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>)}</section><button className="text-button delete-button" onClick={onDelete} disabled={busy}><Trash2 size={17}/>Eliminar consulta</button></aside></div></>;
}

type StudyLookup={ingredient:string;count:number;studies:{id:string;title:string;year:string;journal:string;authors:string[];abstract:string;url:string}[];searchUrl:string};
function EvidenceLookup({ingredient,demo}:{ingredient:string;demo:boolean}) {
  const [result,setResult]=useState<StudyLookup|null>(null);const [loading,setLoading]=useState(false);const [error,setError]=useState('');
  async function search(){setLoading(true);setError('');try{setResult(await api<StudyLookup>('evidence','POST',{ingredient}));}catch(e){setError(e instanceof Error?e.message:'No se pudo consultar PubMed.');}finally{setLoading(false);}}
  const directUrl=`https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(`"${ingredient.replace(/["\\[\]{}]/g,' ').replace(/\s+/g,' ').slice(0,100)}"[Title/Abstract] AND (toxicity OR safety OR exposure OR allergy OR irritation OR adverse)`)}`;
  return <div className="evidence-lookup">{demo?<><a className="text-button" href={directUrl} target="_blank" rel="noopener noreferrer"><BookOpen size={16}/> Buscar estudios relacionados en PubMed</a><small>Los resúmenes dentro de Lookupsafe requieren iniciar sesión.</small></>:<button type="button" className="text-button" onClick={()=>void search()} disabled={loading}>{loading?<LoaderCircle className="spin" size={16}/>:<BookOpen size={16}/>} {loading?'Buscando estudios…':'Buscar estudios relacionados en PubMed'}</button>}{error&&<p role="alert">{error}</p>}{result&&<div className="study-results"><p>PubMed reporta {result.count} publicaciones para esta búsqueda; se muestran hasta {result.studies.length}. La cantidad y el título no indican por sí solos que el ingrediente cause daño.</p>{result.studies.map(study=><article key={study.id}><a href={study.url} target="_blank" rel="noopener noreferrer">{study.title}</a><small>{[study.year,study.journal,study.authors.join(', ')].filter(Boolean).join(' · ')}</small>{study.abstract&&<p>{study.abstract}</p>}</article>)}{!result.studies.length&&<p>No se encontraron publicaciones con esta búsqueda. Eso no demuestra que el ingrediente sea seguro.</p>}<a href={result.searchUrl} target="_blank" rel="noopener noreferrer">Abrir búsqueda y revisar resúmenes en PubMed</a></div>}</div>;
}

function ProfileView({profile,email,demo,busy,onSave,onDelete,onSignOut,onLogin}:{profile:Profile;email?:string;demo:boolean;busy:boolean;onSave:(p:Profile)=>void;onDelete:()=>void;onSignOut:()=>void;onLogin:()=>void}) {
  const [name,setName]=useState(profile.displayName);const [selected,setSelected]=useState(profile.allergens);
  useEffect(()=>{setName(profile.displayName);setSelected(profile.allergens);},[profile]);
  return <><section className="page-heading"><div><div className="eyebrow">PREFERENCIAS PERSONALES</div><h1>Lo que importa en tus productos.</h1><p>Un poco de contexto para revisar tus próximas etiquetas.</p></div></section><div className="profile-grid"><form className="panel profile-form" onSubmit={e=>{e.preventDefault();onSave({displayName:name.trim(),allergens:selected});}}><div className="profile-identity"><span className="large-avatar"><UserRound size={30}/></span><div><h2>{demo?'Tu perfil de ejemplo':email}</h2><p>{demo?'Prueba las preferencias sin crear una cuenta.':'Tus preferencias se comparten con la app Android.'}</p></div></div><label>Tu nombre<input value={name} onChange={e=>setName(e.target.value)} maxLength={80} placeholder="¿Cómo te llamas?" disabled={busy}/></label><fieldset disabled={busy}><legend>Ingredientes que quieres revisar</legend><p>Las coincidencias se resaltarán en tus próximos análisis.</p><div className="concern-groups">{Object.entries(concernGroups).map(([category,ids])=><div className="concern-group" key={category}><h3>{category}</h3><div className="allergen-options">{ids.map(id=>{const label=allergens[id]??id;return <label className={selected.includes(id)?'checked':''} key={id}><input type="checkbox" checked={selected.includes(id)} onChange={()=>setSelected(s=>s.includes(id)?s.filter(x=>x!==id):[...s,id])}/>{label}</label>})}</div></div>)}</div></fieldset><button className="button" disabled={busy}><Check size={18}/>Guardar preferencias</button></form><aside><section className="panel"><ShieldCheck className="green-icon" size={26}/><h2>Tú controlas tus datos.</h2><p>Las fotos se procesan en tu navegador. Tu cuenta guarda el texto revisado, tus consultas y tus preferencias.</p><p className="subtle">Borrar estos datos no elimina tu cuenta de acceso en Supabase.</p><button className="button secondary full" disabled={busy} onClick={onDelete}><Trash2 size={17}/>Eliminar historial y perfil</button>{demo?<button className="text-button profile-login" onClick={onLogin}>Iniciar sesión para guardar</button>:<button className="text-button profile-login" disabled={busy} onClick={onSignOut}><LogOut size={17}/>Cerrar sesión</button>}</section><p className="scope-note"><Info size={17}/>El catálogo es limitado. Tus preferencias no reemplazan la lectura completa del envase.</p></aside></div></>;
}
