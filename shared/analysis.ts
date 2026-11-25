// A transparent text-matching utility, not a clinical or nutritional scoring model.
export const allergenIds = ['milk','egg','peanut','tree_nut','soy','wheat','fish','shellfish','sesame'] as const;
export const concernIds = [...allergenIds, 'fragrance','linalool','limonene','citronellol','geraniol','eugenol','cinnamal','coumarin','benzyl_alcohol','benzyl_salicylate','methylisothiazolinone','methylchloroisothiazolinone','formaldehyde','parabens','phthalates','aluminum_compounds','baking_soda'] as const;
export const concernCategories: Record<string,string> = {
  milk:'Alérgenos alimentarios',egg:'Alérgenos alimentarios',peanut:'Alérgenos alimentarios',tree_nut:'Alérgenos alimentarios',soy:'Alérgenos alimentarios',wheat:'Alérgenos alimentarios',fish:'Alérgenos alimentarios',shellfish:'Alérgenos alimentarios',sesame:'Alérgenos alimentarios',
  fragrance:'Fragancias',linalool:'Fragancias',limonene:'Fragancias',citronellol:'Fragancias',geraniol:'Fragancias',eugenol:'Fragancias',cinnamal:'Fragancias',coumarin:'Fragancias',benzyl_alcohol:'Fragancias',benzyl_salicylate:'Fragancias',
  methylisothiazolinone:'Conservantes',methylchloroisothiazolinone:'Conservantes',formaldehyde:'Conservantes',parabens:'Conservantes',phthalates:'Fragancias y ftalatos',aluminum_compounds:'Ingredientes de antitranspirantes',baking_soda:'Ingredientes de desodorantes',
};
const catalog: {id: typeof concernIds[number]; name: string; terms: string[]}[] = [
  {id:'milk',name:'Leche',terms:['milk','leche','lactosa','lactose','suero de leche','whey','caseina','casein']},
  {id:'egg',name:'Huevo',terms:['egg','eggs','huevo','huevos','albumina','albumin']},
  {id:'peanut',name:'Maní',terms:['peanut','peanuts','mani','cacahuate','cacahuetes']},
  {id:'tree_nut',name:'Frutos de cáscara',terms:['almond','almonds','almendra','almendras','walnut','walnuts','nuez','nueces','avellana','hazelnut','cashew','pistacho']},
  {id:'soy',name:'Soya',terms:['soy','soya','soja','soybean']},
  {id:'wheat',name:'Trigo',terms:['wheat','trigo']},
  {id:'fish',name:'Pescado',terms:['fish','pescado','atun','tuna','salmon','anchoa','anchovy']},
  {id:'shellfish',name:'Crustáceos',terms:['shrimp','prawn','crab','lobster','camaron','camarones','cangrejo','langosta']},
  {id:'sesame',name:'Sésamo',terms:['sesame','sesamo','ajonjoli','tahini']},
  {id:'fragrance',name:'Fragancia o perfume',terms:['parfum','perfume','fragrance','aroma']},
  {id:'linalool',name:'Linalool',terms:['linalool']},
  {id:'limonene',name:'Limoneno',terms:['limonene','limoneno']},
  {id:'citronellol',name:'Citronelol',terms:['citronellol','citronelol']},
  {id:'geraniol',name:'Geraniol',terms:['geraniol']},
  {id:'eugenol',name:'Eugenol',terms:['eugenol']},
  {id:'cinnamal',name:'Cinamal',terms:['cinnamal','cinnamaldehyde','cinamal']},
  {id:'coumarin',name:'Cumarina',terms:['coumarin','cumarina']},
  {id:'benzyl_alcohol',name:'Alcohol bencílico',terms:['benzyl alcohol','alcohol bencilico']},
  {id:'benzyl_salicylate',name:'Salicilato de bencilo',terms:['benzyl salicylate','salicilato de bencilo']},
  {id:'methylisothiazolinone',name:'Metilisotiazolinona (MI)',terms:['methylisothiazolinone','metilisotiazolinona']},
  {id:'methylchloroisothiazolinone',name:'Metilcloroisotiazolinona (MCI)',terms:['methylchloroisothiazolinone','metilcloroisotiazolinona']},
  {id:'formaldehyde',name:'Formaldehído',terms:['formaldehyde','formaldehido','formalin']},
  {id:'parabens',name:'Parabenos',terms:['paraben','parabens','metilparabeno','propilparabeno']},
  {id:'phthalates',name:'Ftalatos',terms:['phthalate','phthalates','ftalato','ftalatos','diethyl phthalate']},
  {id:'aluminum_compounds',name:'Compuesto de aluminio',terms:['aluminum chlorohydrate','aluminum zirconium','aluminium chlorohydrate','aluminium zirconium','clorhidrato de aluminio','zirconio de aluminio']},
  {id:'baking_soda',name:'Bicarbonato de sodio',terms:['sodium bicarbonate','baking soda','bicarbonato de sodio']},
];
export const normalize = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function analyze(label: string, preferences: string[]) {
  const text = normalize(label);
  const matches = catalog.filter(a => a.terms.some(term => new RegExp(`(?:^|[^a-z])${term}(?:$|[^a-z])`).test(text)))
    .map(a => ({id:a.id,name:a.name,personal:preferences.includes(a.id),category:concernCategories[a.id]}));
  // Split only at top-level separators so nested ingredient declarations stay together.
  let depth = 0, part = ''; const pieces: string[] = [];
  for (const char of label.replace(/^\s*(ingredientes|ingredients)\s*:\s*/i,'')) {
    if ('(['.includes(char)) depth++;
    if (')]'.includes(char)) depth = Math.max(0,depth-1);
    if (depth === 0 && /[,;\n]/.test(char)) { if(part.trim()) pieces.push(part.trim()); part=''; }
    else part += char;
  }
  if(part.trim()) pieces.push(part.trim());
  const ingredients = [...new Set(pieces)].slice(0,100).map(name=>({name,status:'unreviewed' as const}));
  return {
    version:2, status:matches.some(a=>a.personal)?'personal_match':matches.length?'label_match':'unreviewed',
    ingredients, allergens:matches, score:null,
    summary: matches.some(a=>a.personal) ? 'La etiqueta menciona un ingrediente que marcaste para revisar.' : matches.length ? 'Se encontraron ingredientes de interés en el texto.' : 'Sin coincidencias en este catálogo limitado. No confirma ausencia de otros ingredientes.',
    notice:'Este análisis encuentra coincidencias de texto en un catálogo limitado en español e inglés. No evalúa concentraciones, formulaciones, exposición, regulación, seguridad ni riesgo médico. Los efectos dependen del producto, el uso y cada persona. Puede omitir nombres, mezclas, sinónimos, negaciones o advertencias. Verifica el envase y consulta a un profesional si tienes una alergia o sensibilidad.',
    sources:[{title:'FDA · Introducción a los cosméticos',url:'https://www.fda.gov/cosmetics/cosmetics-science-research/it-here-cosmetics'}],
  };
}
