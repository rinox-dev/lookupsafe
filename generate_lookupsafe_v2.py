#!/usr/bin/env python3
# lookupsafe Mockups v2 — iconos vectoriales, dark mode, variantes, animación, desktop
# Uso: python3 generate_lookupsafe_v2.py

import os, zipfile

W, H = 390, 844
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"

# ─────────────────────────── THEMES ───────────────────────────
LIGHT = dict(
    bg="#F5F7FA", surface="#FFFFFF", text="#1A1F24", muted="#6B7480", border="#E3E7EC",
    green="#1F8A70", green_d="#146A55", green_l="#E6F4EF",
    amber="#F2A900", amber_bg="#FEF6E0", amber_d="#7A5B00", amber_dd="#8A6100",
    red="#D64545",   red_bg="#FCE9E9",   red_d="#A32B2B",
    subtle="#F1F4F7", thumb="#E8EEF3", avatar="#DDE4EA", avatar_t="#4A5560",
    warn_border="#F6E3AC", score_track="#EAEEF2",
)
DARK = dict(
    bg="#0B0F14", surface="#151C26", text="#E8ECF1", muted="#8B96A3", border="#2A3440",
    green="#2DBE9A", green_d="#7FE0C5", green_l="#0F2A24",
    amber="#F5B831", amber_bg="#2A2210", amber_d="#F5D98A", amber_dd="#F5D98A",
    red="#F26B6B",   red_bg="#2C1515",   red_d="#F5A3A3",
    subtle="#1A212C", thumb="#222C38", avatar="#2A3440", avatar_t="#E8ECF1",
    warn_border="#4A3A10", score_track="#1A212C",
)

# ─────────────────────────── ICONS ───────────────────────────
ICONS = {
 "camera":'<path d="M3 8a2 2 0 0 1 2-2h2l1.5-2h7L17 6h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="13" r="3.5" fill="none" stroke="{c}" stroke-width="1.8"/>',
 "barcode":'<path d="M4 5v14M7 5v14M10 5v10M13 5v14M16 5v10M20 5v14" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "clock":'<circle cx="12" cy="12" r="9" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M12 7v5l3 2" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "grid":'<rect x="4" y="4" width="7" height="7" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><rect x="13" y="4" width="7" height="7" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><rect x="4" y="13" width="7" height="7" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/><rect x="13" y="13" width="7" height="7" rx="1.5" fill="none" stroke="{c}" stroke-width="1.8"/>',
 "user":'<circle cx="12" cy="8" r="4" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M4 21c0-4 3.5-6 8-6s8 2 8 6" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "home":'<path d="M3 10.5 12 3l9 7.5" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 9.5V20h14V9.5" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>',
 "arrow-left":'<path d="m15 18-6-6 6-6" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
 "bookmark":'<path d="M6 3h12v18l-6-4-6 4z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>',
 "bolt":'<path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>',
 "upload":'<path d="M12 16V4" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/><path d="m7 9 5-5 5 5" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 20h14" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "download":'<path d="M12 4v12" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/><path d="m7 11 5 5 5-5" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 20h14" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "check":'<path d="m5 13 4 4L19 7" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
 "package":'<path d="M12 3 3 8v8l9 5 9-5V8z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/><path d="M3 8l9 5 9-5M12 13v8" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>',
 "x":'<path d="M6 6l12 12M18 6 6 18" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>',
 "book":'<path d="M4 4h13v16H6a2 2 0 0 1-2-2z" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/><path d="M17 8h3v10a2 2 0 0 1-2 2" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M7 8h7M7 12h7M7 16h4" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
 "search":'<circle cx="11" cy="11" r="6" fill="none" stroke="{c}" stroke-width="1.8"/><path d="m20 20-4-4" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
}

def icon(name, x, y, size, color):
    return f'<g transform="translate({x},{y}) scale({size/24})">{ICONS[name].format(c=color)}</g>'

# ─────────────────────────── HELPERS ───────────────────────────
def style():
    return f'<style>text{{font-family:{FONT};}}</style>'

def status_bar(t, dark=False):
    c = "#fff" if dark else t["text"]
    return f'''<g fill="{c}">
      <text x="26" y="30" font-size="13" font-weight="600">9:41</text>
      <g transform="translate(324,22)">
        <rect y="5" width="3" height="5" rx="1"/><rect x="4.5" y="2.5" width="3" height="7.5" rx="1"/>
        <rect x="9" width="3" height="10" rx="1"/><rect x="13.5" y="-2" width="3" height="12" rx="1" opacity=".35"/>
        <path d="M23 7.5a5 5 0 0 1 6 0l-3 3z"/>
        <rect x="50" width="14" height="8" rx="2" fill="none" stroke="{c}" stroke-width="1.2" opacity=".5"/>
        <rect x="51.5" y="1.5" width="9" height="5" rx="1"/>
      </g></g>'''

def badge(text, kind, t, x, y):
    pal = {"ok":(t["green_l"],t["green_d"]),"warn":(t["amber_bg"],t["amber_dd"]),"danger":(t["red_bg"],t["red_d"]),"muted":(t["subtle"],t["muted"])}
    bg, fg = pal[kind]
    w = max(60, len(text)*6.3 + 20)
    return f'<g><rect x="{x}" y="{y}" width="{w}" height="20" rx="6" fill="{bg}"/><text x="{x+w/2}" y="{y+14}" text-anchor="middle" font-size="11" font-weight="700" fill="{fg}">{text}</text></g>'

def btn(label, t, x, y, w, kind="primary", h=50, fs=14.5):
    pal = {"primary":(t["green"],"#fff","none"),"dark":("#111","#fff","none"),
           "outline":(t["surface"],t["text"],t["border"]),"ghost":("none",t["green"],"none")}
    bg, fg, br = pal[kind]
    return f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{bg}" stroke="{br}" stroke-width="1"/><text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="{fg}">{label}</text></g>'

def input_field(label, t, x, y, w):
    return f'<g><rect x="{x}" y="{y}" width="{w}" height="50" rx="14" fill="{t["surface"]}" stroke="{t["border"]}"/><text x="{x+16}" y="{y+30}" font-size="14" fill="{t["muted"]}">{label}</text></g>'

def card(t, x, y, w, h, r=16, fill=None, border=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or t["surface"]}" stroke="{border or t["border"]}"/>'

def back_btn(t):
    return f'<g>{card(t,22,52,36,36,10)}{icon("arrow-left",32,60,18,t["text"])}</g>'

# ─────────────────────────── VARIANTS ───────────────────────────
def variant_data(kind):
    base = {
      "warn":{"score":58,"color":"amber","label":"Consumir con moderación",
        "bullets":["2 ingredientes con posible riesgo detectados.","Azúcar y aceite de palma con evidencia limitada.","8 ingredientes sin evidencia relevante.","Revisa las fuentes antes de decidir."],
        "ings":[("TBHQ (E319)","danger","POSIBLE RIESGO"),("Colorante caramelo IV","danger","POSIBLE RIESGO"),("Azúcar","warn","EVID. LIMITADA"),("Aceite de palma","warn","EVID. LIMITADA")]},
      "ok":{"score":82,"color":"green","label":"Recomendable",
        "bullets":["No se detectaron aditivos con posible riesgo.","8 de 8 ingredientes sin evidencia relevante.","Perfil nutricional dentro de parámetros.","Fuentes revisadas y verificables."],
        "ings":[("Avena integral","ok","SIN EVIDENCIA"),("Miel","ok","SIN EVIDENCIA"),("Sal marina","ok","SIN EVIDENCIA"),("Aceite de oliva","warn","EVID. LIMITADA")]},
      "danger":{"score":28,"color":"red","label":"No recomendable",
        "bullets":["3 ingredientes con posible riesgo detectados.","Aditivos con clasificación de agencia desfavorable.","Contiene endulzantes de alta densidad.","Se recomienda revisar alternativas."],
        "ings":[("TBHQ (E319)","danger","POSIBLE RIESGO"),("Colorante caramelo IV","danger","POSIBLE RIESGO"),("Aspartamo","danger","POSIBLE RIESGO"),("Aceite de palma","warn","EVID. LIMITADA")]}
    }
    return base[kind]

def color_for(name, t):
    return {"amber":(t["amber"],t["amber_bg"],t["amber_dd"]),
            "green":(t["green"],t["green_l"],t["green_d"]),
            "red":(t["red"],t["red_bg"],t["red_d"])}[name]

# ─────────────────────────── SCREENS ───────────────────────────
def screen_login(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}
    <rect x="28" y="70" width="70" height="70" rx="22" fill="{t['green']}"/>
    <text x="63" y="115" text-anchor="middle" font-size="24" font-weight="800" fill="#fff">LS</text>
    <text x="28" y="188" font-size="34" font-weight="800" fill="{t['text']}">lookupsafe</text>
    <text x="28" y="214" font-size="14" fill="{t['muted']}">Decisiones de consumo informadas</text>
    <g transform="translate(46,437)"><rect width="18" height="18" rx="3" fill="#4285F4"/><rect width="8" height="8" fill="#EA4335"/><rect x="10" width="8" height="8" fill="#FBBC05"/><rect y="10" width="8" height="8" fill="#34A853"/></g>
    {btn("Continuar con Google", t, 22, 420, W-44, "outline")}
    {btn("Continuar con Apple", t, 22, 478, W-44, "dark")}
    <line x1="46" y1="558" x2="170" y2="558" stroke="{t['border']}"/><text x="195" y="562" text-anchor="middle" font-size="12" fill="{t['muted']}">o</text><line x1="220" y1="558" x2="344" y2="558" stroke="{t['border']}"/>
    {input_field("tucorreo@email.com", t, 22, 578, W-44)}
    {input_field("Contraseña", t, 22, 636, W-44)}
    {btn("Entrar con correo", t, 22, 694, W-44)}
    {btn("Entrar sin cuenta · Escaneo rápido", t, 22, 754, W-44, "ghost", 32, 13)}
    <text x="{W/2}" y="808" text-anchor="middle" font-size="10.5" fill="{t['muted']}">Al continuar aceptas la Política de Privacidad y Términos.</text>
    <text x="{W/2}" y="822" text-anchor="middle" font-size="10.5" fill="{t['muted']}">La app informa; no sustituye consejo médico.</text>
    </svg>'''

def screen_home(t):
    rows=""
    items=[("Galletas Choco Crunch","Hace 2 h · 12 ingredientes","warn","58"),
           ("Bebida energética Zero","Ayer · 9 ingredientes","danger","34"),
           ("Cereal Integral Avena","Lun · 8 ingredientes","ok","82")]
    for i,(name,meta,k,s) in enumerate(items):
        y=415+i*62
        rows+=f'''<g>{card(t,22,y,W-44,52,14)}
          <rect x="34" y="{y+8}" width="36" height="36" rx="10" fill="{t['thumb']}"/>
          {icon("package",44,y+18,16,t['muted'])}
          <text x="80" y="{y+23}" font-size="13" font-weight="700" fill="{t['text']}">{name}</text>
          <text x="80" y="{y+40}" font-size="11" fill="{t['muted']}">{meta}</text>
          {badge(s,k,t,W-72,y+16)}</g>'''
    icons_=[("barcode","Etiqueta"),("clock","Historial"),("grid","Infografías"),("user","Mi perfil")]
    act=""
    for i,(ic,label) in enumerate(icons_):
        x=22+i*88
        act+=f'<rect x="{x}" y="300" width="46" height="46" rx="14" fill="{t["surface"]}" stroke="{t["border"]}"/>'
        act+=icon(ic,x+13,313,20,t["green_d"])
        act+=f'<text x="{x+23}" y="365" text-anchor="middle" font-size="10.5" font-weight="600" fill="{t["text"]}">{label}</text>'
    nav=""
    for i,(ic,lbl) in enumerate([("home","Inicio"),("camera","Escanear"),("clock","Historial"),("user","Perfil")]):
        c = t["green"] if i==0 else t["muted"]
        nav+=icon(ic,38+i*98,H-48,18,c)
        nav+=f'<text x="{48+i*98}" y="{H-18}" text-anchor="middle" font-size="10" font-weight="600" fill="{c}">{lbl}</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}
    <rect x="22" y="56" width="26" height="26" rx="8" fill="{t['green']}"/>
    <text x="35" y="74" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">LS</text>
    <text x="56" y="74" font-size="16" font-weight="800" fill="{t['text']}">lookupsafe</text>
    <circle cx="{W-38}" cy="69" r="16" fill="{t['avatar']}"/>
    <text x="{W-38}" y="74" text-anchor="middle" font-size="12" font-weight="700" fill="{t['avatar_t']}">A</text>
    <text x="22" y="118" font-size="20" font-weight="800" fill="{t['text']}">Hola, Ana</text>
    <text x="22" y="136" font-size="13" font-weight="600" fill="{t['muted']}">Escanea un producto para empezar</text>
    <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#27A486"/><stop offset="1" stop-color="#146A55"/></linearGradient></defs>
    <rect x="22" y="155" width="{W-44}" height="130" rx="22" fill="url(#g1)"/>
    <circle cx="335" cy="175" r="60" fill="#fff" opacity=".12"/>
    <rect x="36" y="170" width="42" height="42" rx="12" fill="#fff" opacity=".18"/>
    {icon("camera",46,180,22,"#fff")}
    <text x="36" y="238" font-size="18" font-weight="800" fill="#fff">Escanear producto</text>
    <text x="36" y="256" font-size="12" fill="#fff" opacity=".85">Apunta a la etiqueta de ingredientes</text>
    {act}
    <text x="22" y="400" font-size="14" font-weight="800" fill="{t['text']}">Últimos escaneos</text>
    <text x="{W-22}" y="400" text-anchor="end" font-size="12" font-weight="700" fill="{t['green']}">Ver todo</text>
    {rows}
    <line x1="0" y1="{H-80}" x2="{W}" y2="{H-80}" stroke="{t['border']}"/>
    <rect y="{H-80}" width="{W}" height="80" fill="{t['surface']}"/>{nav}
    </svg>'''

def screen_camera(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <defs><radialGradient id="cam" cx=".5" cy=".3" r=".9"><stop offset="0" stop-color="#1B2430"/><stop offset="1" stop-color="#0B0F14"/></radialGradient></defs>
    <rect width="{W}" height="{H}" fill="url(#cam)"/>{status_bar(t,dark=True)}
    <circle cx="42" cy="73" r="20" fill="#fff" opacity=".1"/>{icon("x",32,63,20,"#fff")}
    <text x="{W/2}" y="78" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">Escanear etiqueta</text>
    <circle cx="{W-42}" cy="73" r="20" fill="#fff" opacity=".1"/>{icon("bolt",W-52,63,20,"#fff")}
    <rect x="60" y="310" width="270" height="270" rx="20" fill="none" stroke="#fff" stroke-width="1" stroke-dasharray="6 6" opacity=".25"/>
    <path d="M60 344V310h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 344V310h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M60 546V580h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 546V580h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <rect x="95" y="615" width="200" height="34" rx="17" fill="#fff" opacity=".1"/>
    <text x="{W/2}" y="637" text-anchor="middle" font-size="12.5" font-weight="600" fill="#fff">Enfoca la lista de ingredientes</text>
    <circle cx="55" cy="770" r="26" fill="#fff" opacity=".12"/>{icon("upload",45,760,20,"#fff")}
    <circle cx="{W/2}" cy="770" r="37" fill="#fff"/><circle cx="{W/2}" cy="770" r="30" fill="none" stroke="#0B0F14" stroke-width="3"/>
    <circle cx="{W-55}" cy="770" r="26" fill="#fff" opacity=".12"/>{icon("barcode",W-65,760,20,"#fff")}
    </svg>'''

def screen_analysis(t):
    ings=[("Harina de trigo","Base","ok","Sin evidencia"),("Azúcar","Endulzante","warn","Evid. limitada"),
          ("Aceite de palma","Grasa","warn","Evid. limitada"),("TBHQ (E319)","Antioxidante","danger","Posible riesgo"),
          ("Colorante caramelo IV","Colorante","danger","Posible riesgo"),("Lecitina de soya","Emulsionante","ok","Sin evidencia")]
    rows=""
    for i,(n,r,k,l) in enumerate(ings):
        y=340+i*52
        rows+=f'<g>{card(t,22,y,W-44,44,12)}<text x="36" y="{y+22}" font-size="13" font-weight="700" fill="{t["text"]}">{n}</text><text x="36" y="{y+36}" font-size="10.5" fill="{t["muted"]}">{r}</text>{badge(l,k,t,W-130,y+12)}</g>'
    chips=""
    for i,(lbl,a) in enumerate([("Todos",1),("Riesgo",0),("Limitada",0),("Sin evid.",0)]):
        x=22+i*84; bg=t["text"] if a else t["surface"]; fg="#fff" if a else t["muted"]
        chips+=f'<g><rect x="{x}" y="272" width="76" height="28" rx="14" fill="{bg}" stroke="{t["border"]}"/><text x="{x+38}" y="290" text-anchor="middle" font-size="11.5" font-weight="700" fill="{fg}">{lbl}</text></g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}{back_btn(t)}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{t['text']}">Análisis</text>
    <g>{card(t,W-58,52,36,36,10)}{icon("bookmark",W-48,60,16,t["text"])}</g>
    {card(t,22,102,W-44,64,16)}
    <rect x="34" y="110" width="48" height="48" rx="12" fill="{t['thumb']}"/>{icon("package",48,122,20,t["muted"])}
    <text x="94" y="132" font-size="14" font-weight="700" fill="{t['text']}">Galletas Choco Crunch</text>
    <text x="94" y="149" font-size="11.5" fill="{t['muted']}">12 ingredientes detectados</text>
    <rect x="22" y="192" width="112" height="60" rx="12" fill="{t['red_bg']}"/><text x="78" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="{t['red_d']}">2</text><text x="78" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="{t['red_d']}">Posible riesgo</text>
    <rect x="139" y="192" width="112" height="60" rx="12" fill="{t['amber_bg']}"/><text x="195" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="{t['amber_dd']}">2</text><text x="195" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="{t['amber_dd']}">Evid. limitada</text>
    <rect x="256" y="192" width="112" height="60" rx="12" fill="{t['green_l']}"/><text x="312" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="{t['green_d']}">8</text><text x="312" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="{t['green_d']}">Sin evidencia</text>
    {chips}{rows}
    {btn("Ver resumen y recomendación", t, 22, 776, W-44)}
    </svg>'''

def screen_detail(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}{back_btn(t)}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{t['text']}">Ingrediente</text>
    <text x="22" y="135" font-size="24" font-weight="800" fill="{t['text']}">TBHQ (E319)</text>
    {badge("Posible riesgo según evidencia", "danger", t, 22, 148)}
    <rect x="22" y="182" width="{W-44}" height="34" rx="10" fill="{t['amber_bg']}" stroke="{t['warn_border']}"/>
    <text x="34" y="203" font-size="10.5" fill="{t['amber_d']}">Esta información no es diagnóstico médico.</text>
    <text x="22" y="242" font-size="11" font-weight="700" fill="{t['muted']}">¿POR QUÉ SE CONSIDERA POSIBLE RIESGO?</text>
    <text x="22" y="262" font-size="12.5" fill="{t['text']}">Antioxidante sintético usado para conservar grasas.</text>
    <text x="22" y="278" font-size="12.5" fill="{t['text']}">Algunas evaluaciones señalan posibles efectos a dosis</text>
    <text x="22" y="294" font-size="12.5" fill="{t['text']}">altas en estudios animales; evidencia humana limitada.</text>
    <text x="22" y="324" font-size="11" font-weight="700" fill="{t['muted']}">EVIDENCIA CIENTÍFICA</text>
    {card(t,22,334,W-44,44,10)}<text x="34" y="352" font-size="11.5" font-weight="700" fill="{t['text']}">Reevaluación de aditivos alimentarios</text><text x="34" y="368" font-size="10.5" fill="{t['muted']}">[AGENCIA] · [FUENTE CIENTÍFICA]</text>
    {card(t,22,384,W-44,44,10)}<text x="34" y="402" font-size="11.5" font-weight="700" fill="{t['text']}">Estudio in vivo sobre estrés oxidativo</text><text x="34" y="418" font-size="10.5" fill="{t['muted']}">[FUENTE CIENTÍFICA] · [FECHA]</text>
    <text x="22" y="456" font-size="11" font-weight="700" fill="{t['muted']}">NOTICIAS RELACIONADAS</text>
    {card(t,22,466,W-44,44,10)}<text x="34" y="484" font-size="11.5" font-weight="700" fill="{t['text']}">Autoridad europea revisa límites de antioxidantes</text><text x="34" y="500" font-size="10.5" fill="{t['muted']}">[NOTICIA] · [FECHA]</text>
    <text x="22" y="542" font-size="11" font-weight="700" fill="{t['muted']}">CERTEZA DE LA EVIDENCIA: MEDIA</text>
    <rect x="22" y="552" width="108" height="7" rx="4" fill="{t['amber']}"/>
    <rect x="134" y="552" width="108" height="7" rx="4" fill="{t['amber']}"/>
    <rect x="246" y="552" width="108" height="7" rx="4" fill="{t['score_track']}"/>
    {btn("Ver fuentes", t, 22, 770, W-44)}
    </svg>'''

def screen_summary(t, variant="warn"):
    v=variant_data(variant); c,bg,cd = color_for(v["color"], t)
    r,cx,cy=64,W//2,180; circ=2*3.14159*r; off=circ*(1-v["score"]/100)
    btxt=""
    for i,b in enumerate(v["bullets"]):
        y=350+i*26
        btxt+=f'<circle cx="31" cy="{y-3}" r="9" fill="{bg}"/>{icon("check",24,y-10,14,cd)}<text x="46" y="{y+1}" font-size="12" fill="{t["text"]}">{b}</text>'
    chips=""
    for i,(n,k,lbl) in enumerate(v["ings"]):
        cx_,cy_ = 22+(i%2)*130, 480+(i//2)*26
        chips+=badge(n,k,t,cx_,cy_)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}{back_btn(t)}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{t['text']}">Resumen</text>
    <g transform="translate({cx},{cy})"><circle r="{r}" fill="none" stroke="{t['score_track']}" stroke-width="14"/><circle r="{r}" fill="none" stroke="{c}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off:.1f}" transform="rotate(-90)"/></g>
    <text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="38" font-weight="800" fill="{t['text']}">{v['score']}</text>
    <text x="{cx}" y="{cy+20}" text-anchor="middle" font-size="11" fill="{t['muted']}">de 100</text>
    <rect x="22" y="272" width="{W-44}" height="52" rx="14" fill="{bg}" stroke="{cd}" stroke-opacity=".3"/>
    <circle cx="40" cy="298" r="6" fill="{c}"/><circle cx="40" cy="298" r="10" fill="{c}" opacity=".2"/>
    <text x="58" y="294" font-size="14" font-weight="700" fill="{cd}">{v['label']}</text>
    <text x="58" y="310" font-size="10.5" fill="{cd}">Según la evidencia disponible</text>
    {btxt}{chips}
    <rect x="22" y="548" width="{W-44}" height="42" rx="10" fill="{t['subtle']}"/>
    <text x="34" y="566" font-size="10" fill="{t['muted']}">Esta información no sustituye consejo médico.</text>
    <text x="34" y="580" font-size="10" fill="{t['muted']}">Basada en fuentes disponibles a la fecha.</text>
    {btn("Generar infografía", t, 22, 606, W-44)}
    {btn("Guardar resultado", t, 22, 664, W-44, "outline")}
    {btn("Ver fuentes", t, 22, 722, W-44, "ghost", 32, 13)}
    </svg>'''

def screen_infographic(t, variant="warn"):
    v=variant_data(variant); c,bg,cd = color_for(v["color"], t)
    ings_rows=""
    for i,(n,k,lbl) in enumerate(v["ings"]):
        y=270+i*22
        ings_rows+=f'<text x="65" y="{y+8}" font-size="8" font-weight="600" fill="{t["text"]}">{n}</text><text x="320" y="{y+8}" text-anchor="end" font-size="5.5" font-weight="800" fill="{cd}">{lbl}</text>'
        if i<3: ings_rows+=f'<line x1="61" y1="{y+16}" x2="329" y2="{y+16}" stroke="{t["border"]}" stroke-dasharray="2 2"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{t['bg']}"/>{status_bar(t)}{back_btn(t)}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{t['text']}">Infografía</text>
    <g>{card(t,W-58,52,36,36,10)}{icon("download",W-48,60,16,t["text"])}</g>
    {card(t,45,105,300,533,16)}
    <rect x="61" y="121" width="20" height="20" rx="6" fill="{t['green']}"/><text x="71" y="135" text-anchor="middle" font-size="8" font-weight="800" fill="#fff">LS</text>
    <text x="88" y="135" font-size="11" font-weight="800" fill="{t['text']}">lookupsafe</text>
    <text x="329" y="135" text-anchor="end" font-size="6.5" fill="{t['muted']}">Consumo informado</text>
    <text x="61" y="168" font-size="14" font-weight="800" fill="{t['text']}">Galletas Choco Crunch</text>
    <text x="61" y="180" font-size="7" fill="{t['muted']}">12 ingredientes analizados · [FECHA]</text>
    <rect x="61" y="192" width="268" height="46" rx="10" fill="{bg}" stroke="{cd}" stroke-opacity=".3"/>
    <circle cx="74" cy="215" r="5" fill="{c}"/>
    <text x="86" y="212" font-size="9.5" font-weight="700" fill="{cd}">{v['label']}</text>
    <text x="86" y="226" font-size="7" fill="{cd}">Según evidencia disponible</text>
    <text x="318" y="210" text-anchor="end" font-size="16" font-weight="800" fill="{cd}">{v['score']}</text>
    <text x="318" y="222" text-anchor="end" font-size="6" fill="{cd}">/100</text>
    <text x="61" y="262" font-size="7" font-weight="800" fill="{t['muted']}">INGREDIENTES A REVISAR</text>
    {ings_rows}
    <text x="61" y="382" font-size="7" font-weight="800" fill="{t['muted']}">FUENTES CONSULTADAS</text>
    <text x="61" y="398" font-size="6" fill="{t['muted']}">• [AGENCIA] · Reevaluación de aditivos</text>
    <text x="61" y="410" font-size="6" fill="{t['muted']}">• [FUENTE CIENTÍFICA] · Estudio in vivo</text>
    <text x="61" y="422" font-size="6" fill="{t['muted']}">• [NOTICIA] · [FECHA]</text>
    <line x1="61" y1="608" x2="329" y2="608" stroke="{t['border']}"/>
    <text x="61" y="622" font-size="5.8" fill="{t['muted']}">Información basada en fuentes disponibles.</text>
    <text x="61" y="632" font-size="5.8" fill="{t['muted']}">No sustituye consejo médico.</text>
    <text x="329" y="628" text-anchor="end" font-size="6.5" font-weight="700" fill="{t['green_d']}">lookupsafe.app</text>
    {btn("Guardar imagen", t, 22, 660, 168, "outline", 46, 13)}
    {btn("Exportar", t, 200, 660, 168, "primary", 46, 13)}
    </svg>'''

# ────────────────── 4. ANIMATED CAMERA ──────────────────
def screen_camera_animated():
    t = DARK
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <style>
      @keyframes scanY {{ 0% {{ transform: translateY(0); opacity: 0; }} 12% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ transform: translateY(260px); opacity: 0; }} }}
      .scanline {{ animation: scanY 2.4s ease-in-out infinite; }}
      @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
      .fade {{ animation: fadeIn 1s ease-in 0.4s both; }}
    </style>
    <defs>
      <radialGradient id="camA" cx=".5" cy=".3" r=".9"><stop offset="0" stop-color="#1B2430"/><stop offset="1" stop-color="#0B0F14"/></radialGradient>
      <linearGradient id="laser" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2DBE9A" stop-opacity="0"/><stop offset=".5" stop-color="#2DBE9A" stop-opacity=".95"/><stop offset="1" stop-color="#2DBE9A" stop-opacity="0"/></linearGradient>
      <clipPath id="capClip"><rect x="60" y="310" width="270" height="270" rx="20"/></clipPath>
    </defs>
    <rect width="{W}" height="{H}" fill="url(#camA)"/>{status_bar(t,dark=True)}
    <circle cx="42" cy="73" r="20" fill="#fff" opacity=".1"/>{icon("x",32,63,20,"#fff")}
    <text x="{W/2}" y="78" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">Escanear etiqueta</text>
    <circle cx="{W-42}" cy="73" r="20" fill="#fff" opacity=".1"/>{icon("bolt",W-52,63,20,"#fff")}
    <rect x="60" y="310" width="270" height="270" rx="20" fill="#fff" fill-opacity=".03"/>
    <path d="M60 344V310h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 344V310h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M60 546V580h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 546V580h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <g clip-path="url(#capClip)">
      <rect class="scanline" x="60" y="310" width="270" height="20" fill="url(#laser)"/>
      <rect class="scanline" x="60" y="318" width="270" height="2" fill="#7FE0C5" opacity=".9"/>
    </g>
    <g class="fade"><rect x="95" y="615" width="200" height="34" rx="17" fill="#2DBE9A" fill-opacity=".2" stroke="#2DBE9A" stroke-opacity=".5"/><text x="{W/2}" y="637" text-anchor="middle" font-size="12.5" font-weight="600" fill="#fff">Detectando ingredientes…</text></g>
    <circle cx="55" cy="770" r="26" fill="#fff" opacity=".12"/>{icon("upload",45,760,20,"#fff")}
    <circle cx="{W/2}" cy="770" r="37" fill="#fff"/><circle cx="{W/2}" cy="770" r="30" fill="none" stroke="#0B0F14" stroke-width="3"/>
    <circle cx="{W-55}" cy="770" r="26" fill="#fff" opacity=".12"/>{icon("barcode",W-65,760,20,"#fff")}
    </svg>'''

# ────────────────── 5. DESKTOP WEB ──────────────────
def screen_web_desktop(t):
    DW,DH = 1440,900
    nav_items = [("home","Inicio"),("camera","Escanear"),("clock","Historial"),("grid","Infografías"),("user","Perfil")]
    sidebar = ""
    for i,(ic,lbl) in enumerate(nav_items):
        y = 130 + i*52
        active = (i==0)
        if active: sidebar+=f'<rect x="16" y="{y-6}" width="208" height="44" rx="10" fill="{t["green_l"]}"/>'
        c = t["green_d"] if active else t["muted"]
        sidebar+=icon(ic,32,y+4,20,c)+f'<text x="66" y="{y+19}" font-size="14" font-weight="600" fill="{c}">{lbl}</text>'
    ings=[("Harina de trigo","Base","ok","Sin evidencia"),("Azúcar","Endulzante","warn","Evid. limitada"),
          ("Aceite de palma","Grasa","warn","Evid. limitada"),("TBHQ (E319)","Antioxidante","danger","Posible riesgo"),
          ("Colorante caramelo IV","Colorante","danger","Posible riesgo"),("Lecitina de soya","Emulsionante","ok","Sin evidencia")]
    ing_grid=""
    for i,(n,r,k,lbl) in enumerate(ings):
        col,row = i%2, i//2
        x = 320 + col*310; y = 340 + row*64
        ing_grid+=f'<g>{card(t,x,y,296,54,12)}<text x="{x+16}" y="{y+23}" font-size="13" font-weight="700" fill="{t["text"]}">{n}</text><text x="{x+16}" y="{y+40}" font-size="11" fill="{t["muted"]}">{r}</text>{badge(lbl,k,t,x+210,y+17)}</g>'
    v = variant_data("warn"); c,bg,cd = color_for(v["color"], t)
    r=60; cx,cy=1150,420; circ=2*3.14159*r; off=circ*(1-v["score"]/100)
    bullets=""
    for i,b in enumerate(v["bullets"][:3]):
        y=560+i*30
        bullets+=f'<circle cx="990" cy="{y-4}" r="9" fill="{bg}"/>{icon("check",983,y-11,14,cd)}<text x="1006" y="{y+1}" font-size="11.5" fill="{t["text"]}">{b}</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {DW} {DH}">{style()}
    <rect width="{DW}" height="{DH}" fill="{t['bg']}"/>
    <rect x="0" y="0" width="240" height="{DH}" fill="{t['surface']}"/>
    <line x1="240" y1="0" x2="240" y2="{DH}" stroke="{t['border']}"/>
    <rect x="24" y="28" width="34" height="34" rx="10" fill="{t['green']}"/>
    <text x="41" y="50" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">LS</text>
    <text x="66" y="50" font-size="18" font-weight="800" fill="{t['text']}">lookupsafe</text>
    {sidebar}
    <circle cx="40" cy="{DH-44}" r="18" fill="{t['avatar']}"/>
    <text x="40" y="{DH-39}" text-anchor="middle" font-size="13" font-weight="700" fill="{t['avatar_t']}">A</text>
    <text x="68" y="{DH-46}" font-size="13" font-weight="700" fill="{t['text']}">Ana García</text>
    <text x="68" y="{DH-30}" font-size="11" fill="{t['muted']}">Cuenta personal</text>

    <text x="280" y="56" font-size="24" font-weight="800" fill="{t['text']}">Análisis de producto</text>
    <text x="280" y="78" font-size="13" fill="{t['muted']}">Galletas Choco Crunch · Escaneado hace 2 h</text>
    <rect x="1080" y="32" width="220" height="40" rx="10" fill="{t['surface']}" stroke="{t['border']}"/>
    {icon("search",1094,42,18,t["muted"])}
    <text x="1120" y="57" font-size="12" fill="{t['muted']}">Buscar productos…</text>
    {btn("Escanear producto", t, DW-160, 32, 140, "primary", 40, 13)}

    {card(t,280,108,DW-320,140,16)}
    <rect x="296" y="124" width="108" height="108" rx="14" fill="{t['thumb']}"/>
    {icon("package",336,164,32,t["muted"])}
    <text x="424" y="160" font-size="22" font-weight="800" fill="{t['text']}">Galletas Choco Crunch</text>
    <text x="424" y="186" font-size="13" fill="{t['muted']}">12 ingredientes analizados · Categoría: Snacks</text>
    <rect x="424" y="206" width="90" height="26" rx="8" fill="{t['red_bg']}"/>
    <text x="469" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="{t['red_d']}">2 riesgos</text>
    <rect x="522" y="206" width="90" height="26" rx="8" fill="{t['amber_bg']}"/>
    <text x="567" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="{t['amber_dd']}">2 limitada</text>
    <rect x="620" y="206" width="100" height="26" rx="8" fill="{t['green_l']}"/>
    <text x="670" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="{t['green_d']}">8 sin evid.</text>

    <text x="280" y="316" font-size="16" font-weight="800" fill="{t['text']}">Ingredientes detectados</text>
    <text x="440" y="316" font-size="12" fill="{t['muted']}">· 12 en total</text>
    {ing_grid}

    {card(t,960,108,440,720,16)}
    <text x="984" y="146" font-size="16" font-weight="800" fill="{t['text']}">Resumen</text>
    <text x="984" y="168" font-size="12" fill="{t['muted']}">Recomendación final</text>
    <g transform="translate({cx},{cy})">
      <circle r="{r}" fill="none" stroke="{t['score_track']}" stroke-width="14"/>
      <circle r="{r}" fill="none" stroke="{c}" stroke-width="14" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{off:.1f}" transform="rotate(-90)"/>
    </g>
    <text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="42" font-weight="800" fill="{t['text']}">{v['score']}</text>
    <text x="{cx}" y="{cy+26}" text-anchor="middle" font-size="12" fill="{t['muted']}">de 100</text>
    <rect x="984" y="510" width="392" height="52" rx="14" fill="{bg}" stroke="{cd}" stroke-opacity=".3"/>
    <circle cx="1004" cy="536" r="6" fill="{c}"/><circle cx="1004" cy="536" r="10" fill="{c}" opacity=".2"/>
    <text x="1024" y="532" font-size="14" font-weight="700" fill="{cd}">{v['label']}</text>
    <text x="1024" y="548" font-size="10.5" fill="{cd}">Según la evidencia disponible</text>
    {bullets}
    <rect x="984" y="650" width="392" height="56" rx="10" fill="{t['subtle']}"/>
    <text x="1000" y="670" font-size="11" fill="{t['muted']}">Esta información no sustituye consejo médico.</text>
    <text x="1000" y="688" font-size="11" fill="{t['muted']}">Basada en fuentes disponibles a la fecha.</text>
    {btn("Generar infografía", t, 984, 722, 392)}
    {btn("Ver fuentes", t, 984, 782, 392, "outline")}
    </svg>'''

# ─────────────────────────── MAIN ───────────────────────────
def build():
    themes = {"light": LIGHT, "dark": DARK}
    screens = {
        "01-login.svg": screen_login,
        "02-home.svg": screen_home,
        "03-camera.svg": screen_camera,
        "04-analysis.svg": screen_analysis,
        "05-detail.svg": screen_detail,
        "06-summary.svg": screen_summary,
        "07-infographic.svg": screen_infographic,
    }
    outdir = "lookupsafe-v2"
    for theme_name, t in themes.items():
        for fname, fn in screens.items():
            path = os.path.join(outdir, theme_name, fname)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f: f.write(fn(t))
    # Variants
    for vname,kind in [("ok","ok"),("danger","danger")]:
        for fname,fn in [("06-summary.svg",screen_summary),("07-infographic.svg",screen_infographic)]:
            path = os.path.join(outdir, "variants", f"{vname}-{fname}")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f: f.write(fn(LIGHT, kind))
    # Animated
    os.makedirs(os.path.join(outdir,"animated"), exist_ok=True)
    with open(os.path.join(outdir,"animated","03-camera-scanline.svg"),"w",encoding="utf-8") as f:
        f.write(screen_camera_animated())
    # Desktop
    os.makedirs(os.path.join(outdir,"desktop"), exist_ok=True)
    with open(os.path.join(outdir,"desktop","analysis-dashboard.svg"),"w",encoding="utf-8") as f:
        f.write(screen_web_desktop(LIGHT))
    with open(os.path.join(outdir,"desktop","analysis-dashboard-dark.svg"),"w",encoding="utf-8") as f:
        f.write(screen_web_desktop(DARK))
    # Zip
    zip_name = "lookupsafe-mockups-v2.zip"
    with zipfile.ZipFile(zip_name,"w",zipfile.ZIP_DEFLATED) as z:
        for root,_,files in os.walk(outdir):
            for f in files:
                full=os.path.join(root,f)
                z.write(full, os.path.relpath(full, outdir))
    count = sum(len(fs) for _,_,fs in os.walk(outdir))
    print(f"✓ {count} SVG generados en {outdir}/")
    print(f"✓ Empaquetados en {zip_name}")

if __name__ == "__main__":
    build()