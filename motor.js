/* ============================================================
   MOTOR DE DETECCIÓN DE AGRESIVIDAD  (IA contra el Ciberacoso)
   - 100% local, sin internet, funciona en PC y Android
   - Clasifica un mensaje como "agresivo" o "seguro"
   ============================================================ */

/* --- 1. Diccionarios --- */

// Insultos / palabras agresivas (peso alto = más grave)
const INSULTOS = {
  // insultos directos
  "idiota":3,"imbecil":3,"estupido":3,"estupida":3,"tonto":2,"tonta":2,"tarado":3,
  "tarada":3,"subnormal":3,"retrasado":3,"retrasada":3,"inutil":3,"inutiles":3,
  "basura":3,"escoria":3,"asqueroso":3,"asquerosa":3,"repugnante":3,"perdedor":3,
  "perdedora":3,"fracasado":3,"fracasada":3,"payaso":2,"payasa":2,"ridiculo":2,
  "ridicula":2,"patetico":3,"patetica":3,"cerdo":2,"cerda":2,"rata":2,"gusano":2,
  "estorbo":3,"nadie":1,"fenomeno":2,"anormal":3,"deforme":3,"monstruo":2,
  // groserías fuertes
  "puto":3,"puta":3,"pendejo":3,"pendeja":3,"cabron":3,"cabrona":3,"mierda":3,
  "maricon":3,"marica":3,"zorra":3,"perra":3,"imbeciles":3,"gilipollas":3,
  "mongolico":3,"mongola":3,"baboso":2,"babosa":2,"naco":2,"naca":2,"tarugo":2,
  // ataques al cuerpo/persona
  "gordo":2,"gorda":2,"feo":2,"fea":2,"asco":2,"apestas":3,"apestoso":3,
  // amenazas / incitación
  "muerete":4,"matate":4,"suicidate":4,"desaparece":3,"largate":3,"vete":2,
  "callate":2,"odio":2,"odioso":2,"amenazo":3,"golpear":2,"pegarte":3,"destruir":2
};

// Frases/expresiones agresivas compuestas (se buscan como texto)
const FRASES_AGRESIVAS = [
  {f:"nadie te quiere",p:4},{f:"nadie te soporta",p:4},{f:"no sirves para nada",p:4},
  {f:"das asco",p:4},{f:"ojala te",p:3},{f:"deberias morir",p:5},{f:"deberias desaparecer",p:4},
  {f:"te odio",p:3},{f:"eres un cero",p:3},{f:"no vales nada",p:4},{f:"eres una verguenza",p:4},
  {f:"te voy a",p:3},{f:"vas a pagar",p:3},{f:"nadie te va a extrañar",p:4},
  {f:"para que naciste",p:4},{f:"mejor no existieras",p:4},{f:"eres un error",p:4},
  {f:"cierra la boca",p:3},{f:"nadie te invito",p:3},{f:"no perteneces aqui",p:3}
];

// Palabras positivas/amistosas (reducen el riesgo -> evitan falsos positivos)
const POSITIVAS = [
  "gracias","felicidades","felicitaciones","excelente","genial","bravo","crack",
  "grande","campeon","campeona","orgulloso","orgullosa","teamo","quiero","aprecio",
  "buen","buena","buenos","buenas","bien","hermoso","hermosa","lindo","linda",
  "increible","admiro","apoyo","cuenta conmigo","estoy contigo","animo","tranquilo",
  "tranquila","porfa","porfavor","porfavor","ayudar","ayuda","juntos","equipo",
  "amigo","amiga","compañero","compañera","exito","suerte","abrazo","carino"
];

/* --- 2. Normalización de texto (quita acentos, alarga repetidos, leet) --- */
function normalizar(txt){
  let t = txt.toLowerCase();
  // acentos (quita diacríticos combinantes U+0300–U+036F)
  t = t.normalize("NFD").replace(/[̀-ͯ]/g,"");
  // leetspeak común usado para esquivar filtros
  t = t.replace(/0/g,"o").replace(/1/g,"i").replace(/3/g,"e")
       .replace(/4/g,"a").replace(/5/g,"s").replace(/7/g,"t")
       .replace(/@/g,"a").replace(/\$/g,"s");
  // separadores DENTRO de palabras (i.d.i.o.t.a -> idiota) SIN unir palabras separadas por espacio
  t = t.replace(/(\w)[\.\-\*_]+(?=\w)/g, (m,a)=>a);
  // letras repetidas: idiotaaaa -> idiota, holaaaa -> hola
  t = t.replace(/(.)\1{2,}/g,"$1$1");
  return t;
}

/* --- 3. Clasificador principal --- */
function clasificar(textoOriginal){
  const norm = normalizar(textoOriginal);
  const limpio = norm.replace(/[^a-z0-9ñ\s]/g," ").replace(/\s+/g," ").trim();
  const palabras = limpio.split(" ").filter(Boolean);

  let score = 0;
  const motivos = [];

  // a) insultos por palabra
  let insultoFuerte = false;   // ¿hay un insulto claramente ofensivo (peso >=3)?
  palabras.forEach(w=>{
    // quitar repetición de par (idiotaa->idiota) para calzar diccionario
    const base = w.replace(/(.)\1+$/,"$1");
    let peso;
    if(INSULTOS[w]!==undefined){ peso=INSULTOS[w]; score+=peso; motivos.push('palabra ofensiva: "'+w+'"'); }
    else if(INSULTOS[base]!==undefined){ peso=INSULTOS[base]; score+=peso; motivos.push('palabra ofensiva: "'+base+'"'); }
    if(peso>=3) insultoFuerte = true;
  });

  // b) frases agresivas compuestas
  FRASES_AGRESIVAS.forEach(o=>{
    if(limpio.includes(o.f)){ score += o.p; motivos.push('expresión hostil: "'+o.f+'"'); }
  });

  // c) estructura de ataque directo "eres/sos un(a) ..."
  if(/\b(eres|sos|eras|pareces)\b/.test(limpio) && score>0){
    score += 1; motivos.push("ataque personal directo");
  }

  // d) gritos (MAYÚSCULAS) + signos de exclamación repetidos
  const letras = textoOriginal.replace(/[^A-Za-zÁÉÍÓÚÑ]/g,"");
  const mays = textoOriginal.replace(/[^A-ZÁÉÍÓÚÑ]/g,"");
  if(letras.length>6 && mays.length/letras.length>0.7){ score += 1; motivos.push("mensaje GRITADO (mayúsculas)"); }
  if((textoOriginal.match(/!/g)||[]).length>=3){ score += 0.5; }

  // e) reducción por contexto amistoso (evita marcar bromas sanas)
  let positivo = 0;
  POSITIVAS.forEach(p=>{ if(limpio.includes(p)) positivo++; });
  const risa = /\b(ja(ja)+|je(je)+|lol|jaja)\b/.test(limpio) || /😂|🤣|😅|❤|😊|👍|🙌/.test(textoOriginal);
  // Las señales amistosas SOLO reducen el riesgo si NO hay un insulto fuerte
  // (así una broma sana no se marca, pero un insulto claro nunca se "disfraza").
  if(!insultoFuerte){
    if(positivo>0) score -= positivo * 1.2;
    if(risa) score -= 1;
  }

  if(score<0) score = 0;

  // f) decisión
  const UMBRAL = 2;               // a partir de aquí se considera agresivo
  const etiqueta = score >= UMBRAL ? "agresivo" : "seguro";
  // confianza 0-100 (mapeo suave del score)
  const confianza = etiqueta==="agresivo"
    ? Math.min(99, Math.round(55 + score*8))
    : Math.max(2, Math.round(score*15));

  return { etiqueta, score:Math.round(score*10)/10, confianza,
           motivos: motivos.length?motivos:(etiqueta==="seguro"?["sin señales de agresión"]:[]) };
}

/* ============================================================
   4. CONJUNTO DE PRUEBA: 25 insultos + 25 amigables (= 50)
   Sirve para verificar el requisito de precisión ≥ 90%.
   ============================================================ */
const SET_PRUEBA = [
  // ---- 25 AGRESIVOS ----
  {texto:"Eres un inútil, nadie te quiere aquí.", real:"agresivo"},
  {texto:"Cállate idiota, no sirves para nada.", real:"agresivo"},
  {texto:"Das asco, deberías desaparecer del salón.", real:"agresivo"},
  {texto:"Qué estúpido eres, siempre arruinas todo.", real:"agresivo"},
  {texto:"Lárgate basura, aquí nadie te soporta.", real:"agresivo"},
  {texto:"Eres una vergüenza para todos.", real:"agresivo"},
  {texto:"Gordo asqueroso, nadie quiere estar contigo.", real:"agresivo"},
  {texto:"Mejor no existieras, eres un error.", real:"agresivo"},
  {texto:"Te voy a pegar cuando salgas de clase.", real:"agresivo"},
  {texto:"Pareces un retrasado, no entiendes nada.", real:"agresivo"},
  {texto:"Eres un perdedor y siempre lo serás.", real:"agresivo"},
  {texto:"Ojalá te vaya mal en todo, te odio.", real:"agresivo"},
  {texto:"Payaso patético, das pena ajena.", real:"agresivo"},
  {texto:"Nadie te invitó, no perteneces aquí.", real:"agresivo"},
  {texto:"Eres tan feo que asustas a todos.", real:"agresivo"},
  {texto:"CÁLLATE YA, ERES UN ESTORBO PARA TODOS.", real:"agresivo"},
  {texto:"Muérete, nadie te va a extrañar.", real:"agresivo"},
  {texto:"Eres basura, tus ideas son una mierda.", real:"agresivo"},
  {texto:"Tarado, ni siquiera sabes hablar bien.", real:"agresivo"},
  {texto:"Vas a pagar por lo que dijiste, imbécil.", real:"agresivo"},
  {texto:"No vales nada y todos lo saben.", real:"agresivo"},
  {texto:"Eres un fracasado, deja de intentarlo.", real:"agresivo"},
  {texto:"Qué asco me das, apestas horrible.", real:"agresivo"},
  {texto:"Cierra la boca subnormal, nadie te escucha.", real:"agresivo"},
  {texto:"Eres una zorra y todos te odian.", real:"agresivo"},

  // ---- 25 SEGUROS (incluye bromas sanas) ----
  {texto:"¡Buen trabajo compañero, quedó excelente!", real:"seguro"},
  {texto:"¿Estudiamos juntos para el examen de mañana?", real:"seguro"},
  {texto:"Gracias por ayudarme con la tarea, eres genial.", real:"seguro"},
  {texto:"Jajaja qué chistoso, me hiciste reír mucho.", real:"seguro"},
  {texto:"Felicidades por tu presentación, estuvo increíble.", real:"seguro"},
  {texto:"Ánimo, sé que puedes lograrlo, cuenta conmigo.", real:"seguro"},
  {texto:"¿Vamos a jugar fútbol después de clases?", real:"seguro"},
  {texto:"Te quedó súper bien el dibujo, eres un crack.", real:"seguro"},
  {texto:"No te preocupes, todos cometemos errores a veces.", real:"seguro"},
  {texto:"Oye, se te olvidó el cuaderno, yo te lo guardo.", real:"seguro"},
  {texto:"Jaja perdiste otra vez en el videojuego, la revancha va.", real:"seguro"},
  {texto:"Qué bonito día, deberíamos salir al recreo juntos.", real:"seguro"},
  {texto:"Gracias equipo, ganamos gracias a todos.", real:"seguro"},
  {texto:"Estoy contigo, cualquier cosa aquí estoy para apoyarte.", real:"seguro"},
  {texto:"Me encantó tu idea, deberíamos presentarla al profe.", real:"seguro"},
  {texto:"Feliz cumpleaños amigo, que cumplas muchos más.", real:"seguro"},
  {texto:"¿Me pasas los apuntes de historia, porfa?", real:"seguro"},
  {texto:"Tranquilo, mañana nos va a ir mejor en el partido.", real:"seguro"},
  {texto:"Qué buena onda que viniste, la pasamos genial.", real:"seguro"},
  {texto:"Eres muy inteligente, siempre entiendes rápido.", real:"seguro"},
  {texto:"Vamos a la biblioteca a terminar el proyecto.", real:"seguro"},
  {texto:"Te admiro mucho por cómo tocas la guitarra.", real:"seguro"},
  {texto:"Jaja te ganó el sueño en clase otra vez, descansa más.", real:"seguro"},
  {texto:"Buenos días a todos, ¡hoy será un gran día!", real:"seguro"},
  {texto:"Gracias por invitarme, la fiesta estuvo divertida.", real:"seguro"}
];

/* ============================================================
   5. LISTA DE EJEMPLO: 100 mensajes (prueba de "no saturación")
   ============================================================ */
const EJEMPLO_100 = (function(){
  const base = [];
  SET_PRUEBA.forEach(x=>base.push(x.texto));           // 50 reales
  const extra = [
    "¿Alguien tiene el resumen de biología?",
    "Nos vemos en la entrada a las 7.",
    "Qué aburrida estuvo la clase de hoy jaja.",
    "Eres un tonto pero te quiero igual jaja.",
    "No hagas la tarea, copiémosla mejor.",
    "El profe dijo que hay examen sorpresa.",
    "Deja de molestar, en serio, ya basta.",
    "Me caes muy bien, eres buena onda.",
    "Tú siempre arruinas todo, qué inútil.",
    "¿Traes lápiz de más? Se me olvidó el mío."
  ];
  while(base.length<100){ base.push(extra[base.length % extra.length]); }
  return base.slice(0,100);
})();
