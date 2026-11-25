import { analyze, concernCategories, concernIds } from '../../../shared/analysis';
export type Analysis = ReturnType<typeof analyze>;
export type Scan = { id: string; productName: string; labelText: string; analysis: Analysis; favorite: boolean; createdAt: string };
export type Profile = { displayName: string; allergens: string[] };
export type ScanPage = { items: Scan[]; nextOffset: number | null };
export const concernOptions: Record<string,string> = {
  milk:'Leche',egg:'Huevo',peanut:'Maní',tree_nut:'Frutos de cáscara',soy:'Soya',wheat:'Trigo',fish:'Pescado',shellfish:'Crustáceos',sesame:'Sésamo',
  fragrance:'Fragancia/perfume',linalool:'Linalool',limonene:'Limoneno',citronellol:'Citronelol',geraniol:'Geraniol',eugenol:'Eugenol',cinnamal:'Cinamal',coumarin:'Cumarina',benzyl_alcohol:'Alcohol bencílico',benzyl_salicylate:'Salicilato de bencilo',
  methylisothiazolinone:'Metilisotiazolinona',methylchloroisothiazolinone:'Metilcloroisotiazolinona',formaldehyde:'Formaldehído',parabens:'Parabenos',phthalates:'Ftalatos',aluminum_compounds:'Compuestos de aluminio',baking_soda:'Bicarbonato de sodio'
};
export const concernGroups: Record<string,string[]> = Object.fromEntries([...new Set(Object.values(concernCategories))].map(category=>[category,concernIds.filter(id=>concernCategories[id]===category)]));
export const allergens=concernOptions;
export const demoProfile: Profile = { displayName:'', allergens:['fragrance','linalool'] };
export function demoScans(): Scan[] {
  return [
    ['Perfume floral','Alcohol denat., parfum, linalool, limonene, benzyl salicylate','2026-11-25T08:00:00Z'],
    ['Desodorante sin fragancia','Aqua, glycerin, sodium bicarbonate, aluminum chlorohydrate','2026-11-24T10:30:00Z'],
    ['Champú de uso diario','Aqua, parfum, cocamidopropyl betaine, methylisothiazolinone','2026-11-23T15:20:00Z'],
  ].map(([productName,labelText,createdAt],i)=>({id:`example-${i}`,productName:productName!,labelText:labelText!,createdAt:createdAt!,analysis:analyze(labelText!,demoProfile.allergens),favorite:i===0}));
}
export function dateLabel(date:string) { return new Intl.DateTimeFormat('es',{day:'numeric',month:'short',timeZone:'UTC'}).format(new Date(date)); }
