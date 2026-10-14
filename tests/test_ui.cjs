const {JSDOM}=require(process.env.SCOPELEDGER_JSDOM || 'jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');
(async()=>{
 const dom=new JSDOM(fs.readFileSync(root+'/dist/index.html','utf8'),{url:'https://demo.example/',runScripts:'outside-only'});
 const w=dom.window;w.structuredClone=structuredClone;w.fetch=async u=>({json:async()=>JSON.parse(fs.readFileSync(root+'/dist/sample.json','utf8'))});w.HTMLElement.prototype.scrollIntoView=()=>{};
 let blobText='';w.Blob=class{constructor(parts){blobText=parts.join('');}};w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=()=>{};
 w.eval(fs.readFileSync(root+'/dist/app.js','utf8')+'\nwindow._render=render;');
 const $=id=>w.document.getElementById(id),tick=()=>new Promise(r=>setTimeout(r,10));
 $('sample').click();await tick();assert.equal($('cards').children.length,4);assert.equal($('n-change').textContent,'2');assert($('export').disabled);
 const cards=$('cards').children;
 for(const [i,h] of [[0,3],[2,2]]){let inp=cards[i].querySelector('input[type=number]');inp.value=h;inp.dispatchEvent(new w.Event('input'));let c=cards[i].querySelector('input[type=checkbox]');c.checked=true;c.dispatchEvent(new w.Event('input'));}
 assert.equal($('total').textContent,'$500.00');assert(!$('export').disabled);
 $('export').click();await tick();assert(blobText.includes('$500.00'));assert(!blobText.includes('Please adjust the homepage colors'));assert(blobText.includes('not live AI'));
 // Owner override removes a selected item from the price immediately.
 const select=cards[0].querySelector('select');select.value='clarify';select.dispatchEvent(new w.Event('input'));assert.equal($('total').textContent,'$200.00');assert(!cards[0].querySelector('input[type=checkbox]').checked);
 // Fractional dollar rate avoids binary floating point rejection.
 $('rate').value='1.13';$('rate').dispatchEvent(new w.Event('input'));assert.equal($('total').textContent,'$2.26');
 // Invalid inputs block export.
 $('rate').value='0';$('rate').dispatchEvent(new w.Event('input'));assert($('export').disabled);
 $('scope').value+=' changed';$('scope').dispatchEvent(new w.Event('input'));assert($('results').hidden);
 $('analyze').click();assert($('message').textContent.includes('Download'));
 const a=structuredClone(JSON.parse(fs.readFileSync(root+'/dist/sample.json','utf8')).analysis);a.items.forEach(r=>{r.request_quote='<img src=x onerror=alert(1)>';r.scope_quotes=[{id:'S1',text:'<script>evil()</script>'}];});w._render(a);assert.equal($('cards').querySelectorAll('img,script').length,0);assert($('cards').textContent.includes('<img'));
 dom.window.close();console.log('UI workflow passed: sample, estimates, approval, export, overrides, decimals, invalidation, local-only boundary.');
})().catch(e=>{console.error(e);process.exit(1)});
