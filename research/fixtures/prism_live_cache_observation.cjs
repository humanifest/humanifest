/** Read-only observation of public PRISM staging in a fresh automated browser.
 * Requires existing Playwright via NODE_PATH and the named Canary executable.
 * No target setup or deployment. Writes local observations/screenshot under /tmp.
 * This records observations/errors; it is not a full-app assertion test.
 */
const {chromium}=require('playwright');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',headless:true});
 const context=await browser.newContext(); const page=await context.newPage();
 const session=await context.newCDPSession(page);await session.send('Network.enable');
 const records=new Map();let phase='cold';let bytes=0;let limit=false;
 const wanted=u=>/^https:\/\/staging-prism-frontend\.web\.app\/data\/mozambique\/moz_bnd_adm[123]_WFP\.json(?:\?|$)/.test(u);
 session.on('Network.requestWillBeSent',e=>{if(wanted(e.request.url)) records.set(e.requestId,{phase,path:new URL(e.request.url).pathname,method:e.request.method,requestCacheControl:e.request.headers['Cache-Control']??null});});
 session.on('Network.responseReceived',e=>{const r=records.get(e.requestId);if(r)Object.assign(r,{status:e.response.status,mimeType:e.response.mimeType,fromDiskCache:!!e.response.fromDiskCache,fromServiceWorker:!!e.response.fromServiceWorker,headers:Object.fromEntries(Object.entries(e.response.headers).filter(([k])=>['cache-control','content-length','content-encoding','etag'].includes(k.toLowerCase())))});});
 session.on('Network.responseReceivedExtraInfo',e=>{const r=records.get(e.requestId);if(r)r.networkStatus=e.statusCode;});
 session.on('Network.loadingFinished',e=>{bytes+=e.encodedDataLength;const r=records.get(e.requestId);if(r)r.encodedDataLength=e.encodedDataLength;if(bytes>65000000){limit=true;page.close().catch(()=>{});}});
 session.on('Network.loadingFailed',e=>{const r=records.get(e.requestId);if(r)r.error=e.errorText;});
 const observations=[];
 try {
  for(const current of ['cold','warm']) {
   phase=current;
   await page.goto('https://staging-prism-frontend.web.app/',{waitUntil:'domcontentloaded',timeout:30000});
   await page.waitForTimeout(12000);
   observations.push({phase:current,title:await page.title(),bodyExcerpt:(await page.locator('body').innerText()).slice(0,700),resources:await page.evaluate(()=>performance.getEntriesByType('resource').filter(x=>/\/moz_bnd_adm[123]_WFP\.json/.test(x.name)).map(x=>({path:new URL(x.name).pathname,transferSize:x.transferSize,encodedBodySize:x.encodedBodySize,decodedBodySize:x.decodedBodySize})))});
  }
  phase='forced-revalidation';
  const revalidation=await page.evaluate(async()=>{
   performance.clearResourceTimings();
   const responses=await Promise.all([1,2,3].map(async n=>{
    const path=`/data/mozambique/moz_bnd_adm${n}_WFP.json`;
    const response=await fetch(path,{cache:'no-cache'});
    const body=await response.arrayBuffer();
    return {path,status:response.status,decodedBytes:body.byteLength};
   }));
   return {responses,resources:performance.getEntriesByType('resource').filter(x=>/\/moz_bnd_adm[123]_WFP\.json/.test(x.name)).map(x=>({path:new URL(x.name).pathname,transferSize:x.transferSize,encodedBodySize:x.encodedBodySize,decodedBodySize:x.decodedBodySize}))};
  });
  observations.push({phase,...revalidation});
  await page.waitForTimeout(100);
  await page.screenshot({path:'/tmp/humanifest-prism-staging.png'});
 }catch(e){observations.push({error:e.message});}
 finally{const result={browser:browser.version(),live:true,sourceRevision:'deployed revision unverified',downloadLimitHit:limit,totalObservedEncodedBytes:bytes,observations,boundaryRequests:[...records.values()]};fs.writeFileSync('/tmp/humanifest-prism-live-cache-results.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));await browser.close();}
})();
