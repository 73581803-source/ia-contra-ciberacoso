/* ============================================================
   WEB WORKER — hilo en SEGUNDO PLANO
   Ejecuta el análisis fuera del hilo de la interfaz, para que
   la app NUNCA se congele ni se cierre, aunque analice miles
   de mensajes a la vez (requisito "que no se sature").
   ============================================================ */

// Carga el mismo "cerebro" de la IA dentro del worker
importScripts('motor.js');

self.onmessage = function(e){
  const { tipo, datos, id } = e.data;

  if(tipo === 'uno'){
    self.postMessage({ tipo:'uno', id, res: clasificar(datos) });

  } else if(tipo === 'lote'){
    // Analiza en bloques y reporta progreso (así se ve fluido)
    const total = datos.length;
    const res = new Array(total);
    const BLOQUE = 200;
    let i = 0;
    (function paso(){
      const fin = Math.min(i + BLOQUE, total);
      for(; i < fin; i++){ res[i] = clasificar(datos[i]); }
      self.postMessage({ tipo:'progreso', id, hechos:i, total });
      if(i < total){ setTimeout(paso, 0); }      // cede el control -> no bloquea
      else { self.postMessage({ tipo:'lote', id, res }); }
    })();

  } else if(tipo === 'prueba'){
    // Corre el set de 50 frases dentro del worker
    let ok=0, fp=0, fn=0;
    const detalle = SET_PRUEBA.map(it=>{
      const r = clasificar(it.texto);
      const acerto = r.etiqueta === it.real;
      if(acerto) ok++;
      else if(it.real==='seguro') fp++; else fn++;
      return { texto:it.texto, real:it.real, dijo:r.etiqueta, acerto };
    });
    self.postMessage({ tipo:'prueba', id, ok, fp, fn, total:SET_PRUEBA.length, detalle });
  }
};
