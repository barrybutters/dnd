// Bundle PDF.js and its support data for fully offline reading.
const fs=require('node:fs'),path=require('node:path');
const root=path.dirname(require.resolve('pdfjs-dist/package.json')),out=path.resolve('app/vendor/pdfjs');fs.mkdirSync(out,{recursive:true});
for(const name of ['build/pdf.mjs','build/pdf.worker.mjs','LICENSE'])fs.copyFileSync(path.join(root,name),path.join(out,path.basename(name)));
for(const name of ['cmaps','standard_fonts','wasm']){const source=path.join(root,name);if(fs.existsSync(source))fs.cpSync(source,path.join(out,name),{recursive:true})}
console.log('Offline PDF reader bundled.');
