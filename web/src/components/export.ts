import type { Scan } from './data';
export async function exportScan(scan:Scan,demo:boolean) {
  const canvas=document.createElement('canvas'); canvas.width=1080;canvas.height=1600;
  const ctx=canvas.getContext('2d');if(!ctx) throw new Error('Este navegador no permite exportar imágenes.');
  ctx.fillStyle='#f4f7f6';ctx.fillRect(0,0,1080,1600);
  ctx.fillStyle='#12604d';ctx.fillRect(0,0,1080,170);
  ctx.font='bold 52px sans-serif';ctx.fillStyle='#fff';ctx.fillText('lookupsafe',70,110);
  let y=250;
  const text=(value:string,size=32,bold=false)=>{
    ctx.font=`${bold?'bold ':''}${size}px sans-serif`;ctx.fillStyle='#203a32';
    let line='';
    for(const word of value.split(/\s+/)) {
      if(ctx.measureText(`${line} ${word}`).width>940 && line) {ctx.fillText(line,70,y);y+=size*1.45;line='';}
      line+=(line?' ':'')+word;
    }
    if(line) {ctx.fillText(line,70,y);y+=size*1.45;}
    y+=25;
  };
  text(scan.productName,44,true);
  if(demo) text('EJEMPLO · No guardado en una cuenta',24,true);
  text(scan.analysis.summary,34,true);
  text('Ingredientes de interés',28,true);
  text(scan.analysis.allergens.map(a=>a.name).join(', ') || 'Sin coincidencias en el catálogo limitado',30);
  text('Sin puntuación de seguridad',28,true);
  text(scan.analysis.notice,26);
  ctx.font='24px sans-serif';ctx.fillText('Revisa la etiqueta completa del producto',70,1490);
  ctx.fillText('Verifica siempre la etiqueta completa del producto.',70,1540);
  const blob=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('No se pudo crear la imagen.')),'image/png'));
  const link=document.createElement('a');const url=URL.createObjectURL(blob);link.href=url;link.download=`lookupsafe-${scan.id}.png`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
