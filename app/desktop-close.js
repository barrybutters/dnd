/* Called asynchronously after the native closing callback has returned. */
window.prepareDesktopClose=async function(){
 const api=window.pywebview.api;let cancelled=false;
 const cancel=()=>{cancelled=true;api.cancel_close()};
 let dialog=document.getElementById('closeDialog');if(dialog)dialog.remove();
 dialog=document.createElement('dialog');dialog.id='closeDialog';dialog.innerHTML='<h2>Saving before closing…</h2><p id="closeStatus">Finishing local saves. This window will close automatically.</p><div class="tools"><button type="button" id="cancelExit">Keep working</button><button type="button" id="forceExit">Exit without waiting</button></div>';document.body.append(dialog);dialog.showModal();
 $('#cancelExit').onclick=()=>{dialog.close();cancel()};
 $('#forceExit').onclick=()=>{if(confirm('Exit now? Any unsaved changes or unfinished imports may be lost.'))api.finish_close()};
 dialog.addEventListener('cancel',cancel,{once:true});
 clearTimeout(scratchTimer);window.__scratchPending=false;
 if(!window.__loadFailed)save();
 const start=Date.now();
 while(!cancelled){
  if(window.__saveError){$('#closeStatus').textContent='The last save failed. Keep working to retry from Diagnostics, or exit without waiting.';return}
  if(!window.__saving&&!window.__bookImporting&&!window.__externalBackup){await api.finish_close();return}
  if(Date.now()-start>15000){$('#closeStatus').textContent='A save, import or backup is taking longer than expected. You can keep working or exit without waiting.';return}
  await new Promise(r=>setTimeout(r,150));
 }
};
