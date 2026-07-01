/* ============================================================
   SERVICE WORKER — permite que la app:
   · funcione SIN INTERNET (offline)
   · se instale como app real en Android/PC
   · siga disponible aunque cierres el navegador
   ============================================================ */

const CACHE = 'antiacoso-v1';
const ARCHIVOS = [
  './',
  'index.html',
  'motor.js',
  'worker.js',
  'manifest.json'
];

// Instalación: guarda los archivos en caché
self.addEventListener('install', (e)=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ARCHIVOS)));
  self.skipWaiting();
});

// Activación: limpia cachés viejas
self.addEventListener('activate', (e)=>{
  e.waitUntil(
    caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
  );
  self.clients.claim();
});

// Peticiones: responde desde caché y, si no está, desde la red
self.addEventListener('fetch', (e)=>{
  e.respondWith(
    caches.match(e.request).then(r=> r || fetch(e.request).catch(()=>r))
  );
});
