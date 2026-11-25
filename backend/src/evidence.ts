export type Study = { id: string; title: string; year: string; journal: string; authors: string[]; abstract: string; url: string };
export type Evidence = { ingredient: string; count: number; studies: Study[]; searchUrl: string };

const EUTILS = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';

/** Finds biomedical publications mentioning a label ingredient and health-related terms.
 * Search results are citations for review, not a safety assessment or causal finding.
 */
export async function findStudies(ingredient: string): Promise<Evidence> {
  const safeName = ingredient.trim().replace(/["\\[\]{}]/g, ' ').replace(/\s+/g, ' ').slice(0, 100);
  if (safeName.length < 2) throw new Error('Escribe un ingrediente más específico.');
  const term = `"${safeName}"[Title/Abstract] AND (toxicity OR safety OR exposure OR allergy OR irritation OR adverse)`;
  const searchUrl = `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(term)}`;
  const search = new URL(`${EUTILS}/esearch.fcgi`);
  search.search = new URLSearchParams({ db:'pubmed', term, retmode:'json', retmax:'5', tool:'lookupsafe' }).toString();
  const ids = await requestJson<{ esearchresult?: { idlist?: string[]; count?: string } }>(search);
  const idList = ids.esearchresult?.idlist ?? [];
  if (!idList.length) return { ingredient:safeName, count:Number(ids.esearchresult?.count ?? 0), studies:[], searchUrl };

  const abstractsUrl = new URL(`${EUTILS}/efetch.fcgi`);
  abstractsUrl.search = new URLSearchParams({ db:'pubmed', id:idList.join(','), retmode:'xml', tool:'lookupsafe' }).toString();
  const xml = await requestText(abstractsUrl);
  const records = new Map<string,{title:string;year:string;journal:string;authors:string[];abstract:string}>();
  for (const article of xml.matchAll(/<PubmedArticle\b[^>]*>([\s\S]*?)<\/PubmedArticle>/g)) {
    const body = article[1] ?? '';
    const id = body.match(/<PMID\b[^>]*>(\d+)<\/PMID>/)?.[1];
    const pubDate = body.match(/<PubDate\b[^>]*>([\s\S]*?)<\/PubDate>/)?.[1] ?? '';
    const journalBlock = body.match(/<Journal\b[^>]*>([\s\S]*?)<\/Journal>/)?.[1] ?? '';
    const authorBlock = body.match(/<AuthorList\b[^>]*>([\s\S]*?)<\/AuthorList>/)?.[1] ?? '';
    const parts = [...body.matchAll(/<AbstractText\b([^>]*)>([\s\S]*?)<\/AbstractText>/g)].map(part=>{
      const heading = part[1]?.match(/Label="([^"]+)"/)?.[1];
      return `${heading ? `${decodeXml(heading)}: ` : ''}${decodeXml((part[2] ?? '').replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim()}`;
    }).filter(Boolean).join(' ');
    const authors=[...authorBlock.matchAll(/<Author\b[^>]*>([\s\S]*?)<\/Author>/g)].slice(0,3).map(author=>{
      const block=author[1] ?? '';
      return textElement(block,'CollectiveName') || `${textElement(block,'LastName')} ${textElement(block,'Initials')}`.trim();
    }).filter(Boolean);
    if (id) records.set(id,{
      title:textElement(body,'ArticleTitle') || 'Publicación en PubMed',
      year:textElement(pubDate,'Year') || textElement(pubDate,'MedlineDate').match(/\b(?:19|20)\d{2}\b/)?.[0] || '',
      journal:textElement(journalBlock,'Title'),authors,abstract:parts.slice(0,2400),
    });
  }
  const studies = idList.flatMap(id => {
    const row = records.get(id);
    if (!row) return [];
    return [{
      id,
      title: row.title.replace(/\.$/, ''),
      year: row.year,
      journal: row.journal,
      authors: row.authors,
      abstract: row.abstract,
      url: `https://pubmed.ncbi.nlm.nih.gov/${id}/`,
    }];
  });
  return { ingredient:safeName, count:Number(ids.esearchresult?.count ?? studies.length), studies, searchUrl };
}

async function requestJson<T>(url: URL): Promise<T> {
  const response = await fetch(url, { headers:{Accept:'application/json','User-Agent':'lookupsafe/0.1 (PubMed literature lookup)'}, signal:AbortSignal.timeout(8000) });
  if (!response.ok) throw new Error(`PubMed no está disponible (${response.status}).`);
  return await response.json() as T;
}
async function requestText(url: URL): Promise<string> {
  const response = await fetch(url, { headers:{Accept:'application/xml','User-Agent':'lookupsafe/0.1 (PubMed literature lookup)'}, signal:AbortSignal.timeout(8000) });
  if (!response.ok) throw new Error(`PubMed no está disponible (${response.status}).`);
  return response.text();
}
function textElement(xml:string,tag:string):string {
  const content=xml.match(new RegExp(`<${tag}\\b[^>]*>([\\s\\S]*?)<\\/${tag}>`,'i'))?.[1] ?? '';
  return decodeXml(content.replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim();
}
function decodeXml(text:string):string {
  return text.replace(/&#x([\da-f]+);/gi,(_,hex:string)=>String.fromCodePoint(parseInt(hex,16)))
    .replace(/&#(\d+);/g,(_,num:string)=>String.fromCodePoint(Number(num)))
    .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'");
}
