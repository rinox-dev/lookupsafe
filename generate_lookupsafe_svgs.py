#!/usr/bin/env python3
# lookupsafe — Generador de mockups SVG + ZIP
# Uso: python generate_lookupsafe_svgs.py

import os, zipfile

W, H = 390, 844
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
GREEN, GREEN_D, GREEN_L = "#1F8A70", "#146A55", "#E6F4EF"
AMBER, AMBER_BG = "#F2A900", "#FEF6E0"
RED, RED_BG = "#D64545", "#FCE9E9"
BG, WHITE, TEXT, MUTED, BORDER = "#F5F7FA", "#FFFFFF", "#1A1F24", "#6B7480", "#E3E7EC"

def style():
    return f'<style>text{{font-family:{FONT};}}</style>'

def sb(dark=False):
    c = "#fff" if dark else TEXT
    return f'''<g fill="{c}">
      <text x="26" y="30" font-size="13" font-weight="600">9:41</text>
      <g transform="translate(324,22)">
        <rect y="5" width="3" height="5" rx="1"/>
        <rect x="4.5" y="2.5" width="3" height="7.5" rx="1"/>
        <rect x="9" width="3" height="10" rx="1"/>
        <rect x="13.5" y="-2" width="3" height="12" rx="1" opacity=".35"/>
        <path d="M23 7.5a5 5 0 0 1 6 0l-3 3z"/>
        <rect x="50" width="14" height="8" rx="2" fill="none" stroke="{c}" stroke-width="1.2" opacity=".5"/>
        <rect x="51.5" y="1.5" width="9" height="5" rx="1"/>
      </g></g>'''

def badge(text, kind, x, y):
    pal = {"ok":(GREEN_L,GREEN_D),"warn":(AMBER_BG,"#8A6100"),"danger":(RED_BG,"#A32B2B"),"muted":("#EEF1F4",MUTED)}
    bg, fg = pal[kind]
    w = len(text)*6.3 + 18
    return f'''<g>
      <rect x="{x}" y="{y}" width="{w}" height="20" rx="6" fill="{bg}"/>
      <text x="{x+w/2}" y="{y+14}" text-anchor="middle" font-size="11" font-weight="700" fill="{fg}">{text}</text>
    </g>'''

def btn(label, x, y, w, kind="primary", h=50, fs=14.5):
    pal = {"primary":(GREEN,"#fff","none"),"dark":("#111","#fff","none"),
           "outline":(WHITE,TEXT,BORDER),"ghost":("none",GREEN,"none")}
    bg, fg, br = pal[kind]
    return f'''<g>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{bg}" stroke="{br}" stroke-width="1"/>
      <text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-size="{fs}" font-weight="600" fill="{fg}">{label}</text>
    </g>'''

def input_field(label, x, y, w):
    return f'''<g>
      <rect x="{x}" y="{y}" width="{w}" height="50" rx="14" fill="{WHITE}" stroke="{BORDER}" stroke-width="1"/>
      <text x="{x+16}" y="{y+30}" font-size="14" fill="{MUTED}">{label}</text>
    </g>'''

def card(x, y, w, h, r=16, fill=WHITE, border=BORDER):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{border}" stroke-width="1"/>'

def back_btn():
    return f'''<g>{card(22,52,36,36,10)}
      <path d="M44 64l-5 6 5 6" stroke="{TEXT}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    </g>'''

# ============ 1. LOGIN ============
def screen_login():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    <rect x="28" y="70" width="70" height="70" rx="22" fill="{GREEN}"/>
    <text x="63" y="115" text-anchor="middle" font-size="24" font-weight="800" fill="#fff">LS</text>
    <text x="28" y="188" font-size="34" font-weight="800" fill="{TEXT}">lookupsafe</text>
    <text x="28" y="214" font-size="14" fill="{MUTED}">Decisiones de consumo informadas</text>

    <g transform="translate(46,428)">
      <rect width="18" height="18" rx="3" fill="#4285F4"/>
      <rect x="0" y="0" width="8" height="8" fill="#EA4335"/>
      <rect x="10" y="0" width="8" height="8" fill="#FBBC05"/>
      <rect x="0" y="10" width="8" height="8" fill="#34A853"/>
    </g>
    {btn("Continuar con Google", 22, 420, W-44, "outline")}
    {btn("Continuar con Apple", 22, 478, W-44, "dark")}
    <g><line x1="46" y1="558" x2="170" y2="558" stroke="{BORDER}"/><text x="195" y="562" text-anchor="middle" font-size="12" fill="{MUTED}">o</text><line x1="220" y1="558" x2="344" y2="558" stroke="{BORDER}"/></g>
    {input_field("tucorreo@email.com", 22, 578, W-44)}
    {input_field("Contraseña", 22, 636, W-44)}
    {btn("Entrar con correo", 22, 694, W-44, "primary")}
    {btn("Entrar sin cuenta · Escaneo rápido", 22, 754, W-44, "ghost", 32, 13)}
    <text x="{W/2}" y="808" text-anchor="middle" font-size="10.5" fill="{MUTED}">Al continuar aceptas la Política de Privacidad y Términos.</text>
    <text x="{W/2}" y="822" text-anchor="middle" font-size="10.5" fill="{MUTED}">La app informa; no sustituye consejo médico.</text>
    </svg>'''

# ============ 2. HOME ============
def screen_home():
    items = [
        ("🍪","Galletas Choco Crunch","Hace 2 h · 12 ingredientes","warn","58"),
        ("🥤","Bebida energética Zero","Ayer · 9 ingredientes","danger","34"),
        ("🥣","Cereal Integral Avena","Lun · 8 ingredientes","ok","82"),
    ]
    rows = ""
    for i,(emo,name,meta,kind,score) in enumerate(items):
        y = 415 + i*62
        rows += f'''<g>{card(22,y,W-44,52,14)}
          <rect x="34" y="{y+8}" width="36" height="36" rx="10" fill="#E8EEF3"/>
          <text x="52" y="{y+32}" text-anchor="middle" font-size="18">{emo}</text>
          <text x="80" y="{y+23}" font-size="13" font-weight="700" fill="{TEXT}">{name}</text>
          <text x="80" y="{y+40}" font-size="11" fill="{MUTED}">{meta}</text>
          {badge(score,kind,W-72,y+16)}
        </g>'''
    icons = [("📷","Etiqueta"),("🕐","Historial"),("📊","Infografías"),("👤","Mi perfil")]
    act = ""
    for i,(ic,label) in enumerate(icons):
        x = 22 + i*88
        act += f'''<g>
          <rect x="{x}" y="300" width="46" height="46" rx="14" fill="{WHITE}" stroke="{BORDER}"/>
          <text x="{x+23}" y="329" text-anchor="middle" font-size="20">{ic}</text>
          <text x="{x+23}" y="365" text-anchor="middle" font-size="10.5" font-weight="600" fill="{TEXT}">{label}</text>
        </g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    <rect x="22" y="56" width="26" height="26" rx="8" fill="{GREEN}"/>
    <text x="35" y="74" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">LS</text>
    <text x="56" y="74" font-size="16" font-weight="800" fill="{TEXT}">lookupsafe</text>
    <circle cx="{W-38}" cy="69" r="16" fill="#DDE4EA"/>
    <text x="{W-38}" y="74" text-anchor="middle" font-size="12" font-weight="700" fill="#4A5560">A</text>

    <text x="22" y="118" font-size="20" font-weight="800" fill="{TEXT}">Hola, Ana</text>
    <text x="22" y="136" font-size="13" font-weight="600" fill="{MUTED}">Escanea un producto para empezar</text>

    <defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#27A486"/><stop offset="1" stop-color="#146A55"/>
    </linearGradient></defs>
    <rect x="22" y="155" width="{W-44}" height="130" rx="22" fill="url(#g1)"/>
    <circle cx="335" cy="175" r="60" fill="#fff" opacity=".12"/>
    <rect x="36" y="170" width="42" height="42" rx="12" fill="#fff" opacity=".18"/>
    <text x="57" y="197" text-anchor="middle" font-size="20">📷</text>
    <text x="36" y="238" font-size="18" font-weight="800" fill="#fff">Escanear producto</text>
    <text x="36" y="256" font-size="12" fill="#fff" opacity=".85">Apunta a la etiqueta de ingredientes</text>

    {act}

    <text x="22" y="400" font-size="14" font-weight="800" fill="{TEXT}">Últimos escaneos</text>
    <text x="{W-22}" y="400" text-anchor="end" font-size="12" font-weight="700" fill="{GREEN}">Ver todo</text>
    {rows}

    <line x1="0" y1="{H-80}" x2="{W}" y2="{H-80}" stroke="{BORDER}"/>
    <rect y="{H-80}" width="{W}" height="80" fill="{WHITE}"/>
    {''.join(f'<g><text x="{48+i*98}" y="{H-40}" text-anchor="middle" font-size="18">{ic}</text><text x="{48+i*98}" y="{H-22}" text-anchor="middle" font-size="10" font-weight="600" fill="{GREEN if i==0 else MUTED}">{lbl}</text></g>' for i,(ic,lbl) in enumerate([("🏠","Inicio"),("📷","Escanear"),("🕐","Historial"),("👤","Perfil")]))}
    </svg>'''

# ============ 3. CAMERA ============
def screen_camera():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <defs><radialGradient id="cam" cx=".5" cy=".3" r=".9">
      <stop offset="0" stop-color="#1B2430"/><stop offset="1" stop-color="#0B0F14"/>
    </radialGradient></defs>
    <rect width="{W}" height="{H}" fill="url(#cam)"/>
    {sb(dark=True)}

    <circle cx="42" cy="73" r="20" fill="#fff" opacity=".1"/>
    <path d="M42 65l12 12M54 65l-12 12" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
    <text x="{W/2}" y="78" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">Escanear etiqueta</text>
    <circle cx="{W-42}" cy="73" r="20" fill="#fff" opacity=".1"/>
    <text x="{W-42}" y="79" text-anchor="middle" font-size="16">⚡</text>

    <rect x="60" y="310" width="270" height="270" rx="20" fill="none" stroke="#fff" stroke-width="1" stroke-dasharray="6 6" opacity=".25"/>
    <path d="M60 344V310h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 344V310h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M60 546V580h34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
    <path d="M330 546V580h-34" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>

    <rect x="95" y="615" width="200" height="34" rx="17" fill="#fff" opacity=".1"/>
    <text x="{W/2}" y="637" text-anchor="middle" font-size="12.5" font-weight="600" fill="#fff">Enfoca la lista de ingredientes</text>

    <circle cx="55" cy="770" r="26" fill="#fff" opacity=".12"/>
    <text x="55" y="777" text-anchor="middle" font-size="18" fill="#fff">⬆</text>
    <circle cx="{W/2}" cy="770" r="37" fill="#fff"/>
    <circle cx="{W/2}" cy="770" r="30" fill="none" stroke="#0B0F14" stroke-width="3"/>
    <circle cx="{W-55}" cy="770" r="26" fill="#fff" opacity=".12"/>
    <text x="{W-55}" y="777" text-anchor="middle" font-size="16" fill="#fff">▤</text>
    </svg>'''

# ============ 4. ANALYSIS ============
def screen_analysis():
    ings = [
        ("Harina de trigo","Base","ok","Sin evidencia"),
        ("Azúcar","Endulzante","warn","Evid. limitada"),
        ("Aceite de palma","Grasa","warn","Evid. limitada"),
        ("TBHQ (E319)","Antioxidante","danger","Posible riesgo"),
        ("Colorante caramelo IV","Colorante","danger","Posible riesgo"),
        ("Lecitina de soya","Emulsionante","ok","Sin evidencia"),
    ]
    rows = ""
    for i,(name,role,kind,label) in enumerate(ings):
        y = 340 + i*52
        rows += f'''<g>{card(22,y,W-44,44,12)}
          <text x="36" y="{y+22}" font-size="13" font-weight="700" fill="{TEXT}">{name}</text>
          <text x="36" y="{y+36}" font-size="10.5" fill="{MUTED}">{role}</text>
          {badge(label,kind,W-130,y+12)}
        </g>'''
    stats = f'''
      <rect x="22" y="192" width="112" height="60" rx="12" fill="{RED_BG}"/>
      <text x="78" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="#A32B2B">2</text>
      <text x="78" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="#A32B2B">Posible riesgo</text>
      <rect x="139" y="192" width="112" height="60" rx="12" fill="{AMBER_BG}"/>
      <text x="195" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="#8A6100">2</text>
      <text x="195" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="#8A6100">Evid. limitada</text>
      <rect x="256" y="192" width="112" height="60" rx="12" fill="{GREEN_L}"/>
      <text x="312" y="220" text-anchor="middle" font-size="19" font-weight="800" fill="{GREEN_D}">8</text>
      <text x="312" y="236" text-anchor="middle" font-size="9.5" font-weight="600" fill="{GREEN_D}">Sin evidencia</text>'''
    chips = ""
    for i,(lbl,active) in enumerate([("Todos",1),("Posible riesgo",0),("Evid. limitada",0),("Sin evidencia",0)]):
        x = 22 + sum([70 if j<2 else 95 for j in range(i)]) + i*8
        bg = TEXT if active else WHITE
        fg = "#fff" if active else MUTED
        w = 50 if len(lbl)<8 else 90
        chips += f'''<g><rect x="{x}" y="272" width="{w}" height="28" rx="14" fill="{bg}" stroke="{BORDER}"/>
          <text x="{x+w/2}" y="290" text-anchor="middle" font-size="11.5" font-weight="700" fill="{fg}">{lbl}</text></g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    {back_btn()}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{TEXT}">Análisis</text>
    <g>{card(W-58,52,36,36,10)}<text x="{W-40}" y="76" text-anchor="middle" font-size="15">🔖</text></g>

    {card(22,102,W-44,64,16)}
    <rect x="34" y="110" width="48" height="48" rx="12" fill="#E8EEF3"/>
    <text x="58" y="142" text-anchor="middle" font-size="22">🍪</text>
    <text x="94" y="132" font-size="14" font-weight="700" fill="{TEXT}">Galletas Choco Crunch</text>
    <text x="94" y="149" font-size="11.5" fill="{MUTED}">12 ingredientes detectados</text>

    {stats}
    {chips}
    {rows}
    {btn("Ver resumen y recomendación", 22, 776, W-44, "primary")}
    </svg>'''

# ============ 5. DETAIL ============
def screen_detail():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    {back_btn()}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{TEXT}">Ingrediente</text>

    <text x="22" y="135" font-size="24" font-weight="800" fill="{TEXT}">TBHQ (E319)</text>
    {badge("Posible riesgo según evidencia", "danger", 22, 148)}

    <rect x="22" y="182" width="{W-44}" height="34" rx="10" fill="#FFF8E6" stroke="#F6E3AC"/>
    <text x="34" y="203" font-size="10.5" fill="#7A5B00">Esta información no es diagnóstico médico.</text>

    <text x="22" y="242" font-size="11" font-weight="700" fill="{MUTED}">¿POR QUÉ SE CONSIDERA POSIBLE RIESGO?</text>
    <text x="22" y="262" font-size="12.5" fill="#3A424B">Antioxidante sintético usado para conservar grasas.</text>
    <text x="22" y="278" font-size="12.5" fill="#3A424B">Algunas evaluaciones señalan posibles efectos a dosis</text>
    <text x="22" y="294" font-size="12.5" fill="#3A424B">altas en estudios animales; evidencia humana limitada.</text>

    <text x="22" y="324" font-size="11" font-weight="700" fill="{MUTED}">EVIDENCIA CIENTÍFICA</text>
    {card(22,334,W-44,44,10)}
    <text x="34" y="352" font-size="11.5" font-weight="700" fill="{TEXT}">Reevaluación de aditivos alimentarios</text>
    <text x="34" y="368" font-size="10.5" fill="{MUTED}">[AGENCIA] · [FUENTE CIENTÍFICA]</text>
    {card(22,384,W-44,44,10)}
    <text x="34" y="402" font-size="11.5" font-weight="700" fill="{TEXT}">Estudio in vivo sobre estrés oxidativo</text>
    <text x="34" y="418" font-size="10.5" fill="{MUTED}">[FUENTE CIENTÍFICA] · [FECHA]</text>

    <text x="22" y="456" font-size="11" font-weight="700" fill="{MUTED}">NOTICIAS RELACIONADAS</text>
    {card(22,466,W-44,44,10)}
    <text x="34" y="484" font-size="11.5" font-weight="700" fill="{TEXT}">Autoridad europea revisa límites de antioxidantes</text>
    <text x="34" y="500" font-size="10.5" fill="{MUTED}">[NOTICIA] · [FECHA]</text>

    <text x="22" y="542" font-size="11" font-weight="700" fill="{MUTED}">CERTEZA DE LA EVIDENCIA: MEDIA</text>
    <rect x="22" y="552" width="108" height="7" rx="4" fill="{AMBER}"/>
    <rect x="134" y="552" width="108" height="7" rx="4" fill="{AMBER}"/>
    <rect x="246" y="552" width="108" height="7" rx="4" fill="#EAEEF2"/>

    {btn("Ver fuentes", 22, 770, W-44, "primary")}
    </svg>'''

# ============ 6. SUMMARY ============
def screen_summary():
    r, cx, cy = 64, W//2, 180
    circ = 2 * 3.14159 * r
    offset = circ * (1 - 0.58)
    bullets = [
        "2 ingredientes con posible riesgo detectados.",
        "Azúcar y aceite de palma con evidencia limitada.",
        "8 ingredientes sin evidencia relevante.",
        "Revisa las fuentes antes de decidir.",
    ]
    btxt = ""
    for i,b in enumerate(bullets):
        y = 350 + i*26
        btxt += f'''<circle cx="31" cy="{y-3}" r="9" fill="{GREEN_L}"/>
          <path d="M27 {y-3}l2.5 2.5L35 {y-7}" stroke="{GREEN_D}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="46" y="{y+1}" font-size="12" fill="#3A424B">{b}</text>'''
    chips = f'''{badge("TBHQ (E319)","danger",22,480)}
        {badge("Caramelo IV","danger",22+95,480)}
        {badge("Azúcar","warn",22,506)}
        {badge("Aceite de palma","warn",22+68,506)}'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    {back_btn()}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{TEXT}">Resumen</text>

    <g transform="translate({cx},{cy})">
      <circle r="{r}" fill="none" stroke="#EAEEF2" stroke-width="14"/>
      <circle r="{r}" fill="none" stroke="{AMBER}" stroke-width="14" stroke-linecap="round"
              stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}" transform="rotate(-90)"/>
    </g>
    <text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="38" font-weight="800" fill="{TEXT}">58</text>
    <text x="{cx}" y="{cy+20}" text-anchor="middle" font-size="11" fill="{MUTED}">de 100</text>

    <rect x="22" y="272" width="{W-44}" height="52" rx="14" fill="{AMBER_BG}" stroke="#F6E3AC"/>
    <circle cx="40" cy="298" r="6" fill="{AMBER}"/>
    <circle cx="40" cy="298" r="10" fill="{AMBER}" opacity=".2"/>
    <text x="58" y="294" font-size="14" font-weight="700" fill="#7A5B00">Consumir con moderación</text>
    <text x="58" y="310" font-size="10.5" fill="#8A6100">Según la evidencia disponible</text>

    {btxt}
    {chips}

    <rect x="22" y="548" width="{W-44}" height="42" rx="10" fill="#F1F4F7"/>
    <text x="34" y="566" font-size="10" fill="{MUTED}">Esta información no sustituye consejo médico.</text>
    <text x="34" y="580" font-size="10" fill="{MUTED}">Basada en fuentes disponibles a la fecha.</text>

    {btn("Generar infografía", 22, 606, W-44, "primary")}
    {btn("Guardar resultado", 22, 664, W-44, "outline")}
    {btn("Ver fuentes", 22, 722, W-44, "ghost", 32, 13)}
    </svg>'''

# ============ 7. INFOGRAPHIC ============
def screen_infographic():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{style()}
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {sb()}
    {back_btn()}
    <text x="{W/2}" y="75" text-anchor="middle" font-size="16" font-weight="800" fill="{TEXT}">Infografía</text>
    <g>{card(W-58,52,36,36,10)}<text x="{W-40}" y="76" text-anchor="middle" font-size="15">⬇</text></g>

    {card(45,105,300,533,16)}
    <rect x="61" y="121" width="20" height="20" rx="6" fill="{GREEN}"/>
    <text x="71" y="135" text-anchor="middle" font-size="8" font-weight="800" fill="#fff">LS</text>
    <text x="88" y="135" font-size="11" font-weight="800" fill="{TEXT}">lookupsafe</text>
    <text x="329" y="135" text-anchor="end" font-size="6.5" fill="{MUTED}">Consumo informado</text>

    <text x="61" y="168" font-size="14" font-weight="800" fill="{TEXT}">Galletas Choco Crunch</text>
    <text x="61" y="180" font-size="7" fill="{MUTED}">12 ingredientes analizados · [FECHA]</text>

    <rect x="61" y="192" width="268" height="46" rx="10" fill="{AMBER_BG}" stroke="#F6E3AC"/>
    <circle cx="74" cy="215" r="5" fill="{AMBER}"/>
    <text x="86" y="212" font-size="9.5" font-weight="700" fill="#7A5B00">Consumir con moderación</text>
    <text x="86" y="226" font-size="7" fill="#8A6100">Según evidencia disponible</text>
    <text x="318" y="210" text-anchor="end" font-size="16" font-weight="800" fill="#7A5B00">58</text>
    <text x="318" y="222" text-anchor="end" font-size="6" fill="#8A6100">/100</text>

    <text x="61" y="262" font-size="7" font-weight="800" fill="{MUTED}">INGREDIENTES A REVISAR</text>
    {badge("TBHQ (E319)","danger",61,270) and ""}
    <text x="65" y="284" font-size="8" font-weight="600" fill="{TEXT}">TBHQ (E319)</text>
    <text x="320" y="284" text-anchor="end" font-size="5.5" font-weight="800" fill="#A32B2B">POSIBLE RIESGO</text>
    <line x1="61" y1="292" x2="329" y2="292" stroke="#EEF1F4" stroke-dasharray="2 2"/>
    <text x="65" y="306" font-size="8" font-weight="600" fill="{TEXT}">Colorante caramelo IV</text>
    <text x="320" y="306" text-anchor="end" font-size="5.5" font-weight="800" fill="#A32B2B">POSIBLE RIESGO</text>
    <line x1="61" y1="314" x2="329" y2="314" stroke="#EEF1F4" stroke-dasharray="2 2"/>
    <text x="65" y="328" font-size="8" font-weight="600" fill="{TEXT}">Azúcar</text>
    <text x="320" y="328" text-anchor="end" font-size="5.5" font-weight="800" fill="#8A6100">EVID. LIMITADA</text>
    <line x1="61" y1="336" x2="329" y2="336" stroke="#EEF1F4" stroke-dasharray="2 2"/>
    <text x="65" y="350" font-size="8" font-weight="600" fill="{TEXT}">Aceite de palma</text>
    <text x="320" y="350" text-anchor="end" font-size="5.5" font-weight="800" fill="#8A6100">EVID. LIMITADA</text>

    <text x="61" y="376" font-size="7" font-weight="800" fill="{MUTED}">FUENTES CONSULTADAS</text>
    <text x="61" y="392" font-size="6" fill="{MUTED}">• [AGENCIA] · Reevaluación de aditivos</text>
    <text x="61" y="404" font-size="6" fill="{MUTED}">• [FUENTE CIENTÍFICA] · Estudio in vivo</text>
    <text x="61" y="416" font-size="6" fill="{MUTED}">• [NOTICIA] · [FECHA]</text>

    <line x1="61" y1="608" x2="329" y2="608" stroke="{BORDER}"/>
    <text x="61" y="622" font-size="5.8" fill="{MUTED}">Información basada en fuentes disponibles.</text>
    <text x="61" y="632" font-size="5.8" fill="{MUTED}">No sustituye consejo médico.</text>
    <text x="329" y="628" text-anchor="end" font-size="6.5" font-weight="700" fill="{GREEN_D}">lookupsafe.app</text>

    {btn("Guardar imagen", 22, 660, 168, "outline", 46, 13)}
    {btn("Exportar", 200, 660, 168, "primary", 46, 13)}
    </svg>'''

# ============ MAIN ============
if __name__ == "__main__":
    screens = {
        "01-login.svg":       screen_login(),
        "02-home.svg":        screen_home(),
        "03-camera.svg":      screen_camera(),
        "04-analysis.svg":    screen_analysis(),
        "05-detail.svg":      screen_detail(),
        "06-summary.svg":     screen_summary(),
        "07-infographic.svg": screen_infographic(),
    }
    os.makedirs("lookupsafe-svgs", exist_ok=True)
    for name, content in screens.items():
        with open(f"lookupsafe-svgs/{name}", "w", encoding="utf-8") as f:
            f.write(content)
    with zipfile.ZipFile("lookupsafe-mockups.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in screens:
            z.write(f"lookupsafe-svgs/{name}", name)
    print(f"✓ {len(screens)} SVG generados en lookupsafe-svgs/")
    print("✓ Empaquetados en lookupsafe-mockups.zip")