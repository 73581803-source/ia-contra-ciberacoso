/* Servidor local sencillo para probar/instalar la app.
   Ejecuta:  node servidor.js   y abre  http://localhost:8080  */
const http = require('http'), fs = require('fs'), path = require('path');
const TIPOS = {'.html':'text/html','.js':'text/javascript','.json':'application/manifest+json','.css':'text/css'};
const PORT = 8080;
http.createServer((req,res)=>{
  let f = decodeURIComponent(req.url.split('?')[0]);
  if(f==='/') f='/index.html';
  const ruta = path.join(__dirname, f);
  fs.readFile(ruta,(err,data)=>{
    if(err){ res.writeHead(404); res.end('No encontrado'); return; }
    res.writeHead(200, {'Content-Type': TIPOS[path.extname(ruta)] || 'application/octet-stream'});
    res.end(data);
  });
}).listen(PORT, ()=>console.log('Servidor en http://localhost:'+PORT));
