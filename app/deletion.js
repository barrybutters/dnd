/* Explicit, recoverable delete controls and relationship cleanup. */
function deleteCampaign(){const c=C();if(!c)return;const id=c.id,expected=c.name;form('Delete campaign',[txt('confirmation','Type the campaign name exactly to delete: '+expected)],v=>{if(v.confirmation!==expected)throw Error('The campaign name does not match. Nothing was deleted.');stopAllAudio();state.campaigns=state.campaigns.filter(x=>x.id!==id);state.selected=state.campaigns[0]?.id;currentChar=C()?.characters[0]?.id;inventoryOwner='Party';page='Overview';selectedToken=null;toast('Campaign deleted. Undo or automatic backups can restore it.');})}
remove=function(kind,id){const c=C();if(!c)return;const entry=c[kind]?.find(x=>x.id===id);if(!entry)return;const name=entry.title||entry.name||'this entry';let extra='';if(kind==='characters')extra=' Encounter entries will be removed and equipment moved to party inventory.';if(kind==='items')extra=' Contents will stay in the inventory without this container.';if(!confirm('Delete '+name+'?'+extra+' You can Undo this change.'))return;
if(kind==='characters'){c.combat=c.combat.filter(x=>x.source!==id);c.items.filter(x=>x.owner===id).forEach(x=>x.owner='Party');if(currentChar===id)currentChar=null;if(inventoryOwner===id)inventoryOwner='Party'}
if(kind==='items')c.items.filter(x=>x.container===id).forEach(x=>x.container='');
if(kind==='audio'){const player=soundPlayers.get(id);if(player){player.pause();player.currentTime=0;soundPlayers.delete(id)}}
if(kind==='combat'){const i=c.combat.findIndex(x=>x.id===id);if(i<c.turn)c.turn--;else if(i===c.turn&&c.turn===c.combat.length-1)c.turn=0}
c[kind]=c[kind].filter(x=>x.id!==id);save();render();toast('Deleted '+name+' · Undo is available')};
function deleteAttachment(pageId,index){const p=C()?.wiki.find(p=>p.id===pageId);if(!p?.attachments?.[index])return;if(!confirm('Remove this attachment from the wiki page? You can Undo this change.'))return;p.attachments.splice(index,1);save();render()}
function clearRollHistory(){if(!confirm('Clear roll history? You can Undo this change.'))return;state.rolls=[];save();render()}
function deleteRoll(index){if(!confirm('Delete this roll from history?'))return;state.rolls.splice(index,1);save();render()}
const deletionRender=render;render=function(){deletionRender();
const quick=document.querySelector('header button[onclick="openNote()"]');if(quick)quick.disabled=!C();
if(C()&&['Overview','Campaign'].includes(page))$('#view').insertAdjacentHTML('beforeend',`<section class="card dangerzone"><h2>Campaign settings</h2><p>Delete <b>${esc(C().name)}</b> and its characters, notes, maps, inventory and encounters. Shared rulebooks stay available. Undo and automatic backups can restore a deleted campaign.</p>${btn('Delete campaign','deleteCampaign()','danger')}</section>`);
// Make formerly icon-only delete controls discoverable and readable.
document.querySelectorAll('#view button').forEach(button=>{if(button.textContent.trim()==='×'){button.textContent='Delete';button.classList.add('danger');button.setAttribute('aria-label','Delete entry')}});
if(page==='Dice'){const card=[...document.querySelectorAll('#view .card')].find(c=>c.querySelector('h2')?.textContent==='Roll history');if(card)card.insertAdjacentHTML('afterbegin',btn('Clear roll history','clearRollHistory()','danger'))}
};
const priorWikiView=wikiView;wikiView=function(){const html=priorWikiView();queueMicrotask(()=>{if(page!=='Wiki')return;const pages=C().wiki.filter(p=>state.role==='dm'||!p.secret);document.querySelectorAll('#view article.searchable').forEach((card,i)=>{const p=pages[i];if(!p)return;card.querySelectorAll('a.assetlink').forEach((a,j)=>{const b=document.createElement('button');b.className='danger';b.textContent='Remove attachment';b.onclick=()=>deleteAttachment(p.id,j);a.after(b)})})});return html};
// Each history row gets an individual delete button without altering the dice result.
const priorRollHistory=rollHistory;rollHistory=function(){return state.rolls.slice(0,30).map((r,i)=>`<div class="row"><div><b>${esc(r.label||r.expr)}</b><div class="sub">${esc(r.expr)} · ${esc(r.detail)} · ${r.role==='player'?'Player':'DM'}</div></div><span class="stat">${r.total}</span>${btn('Delete',`deleteRoll(${i})`,'danger')}</div>`).join('')||'<p>No rolls in history.</p>'};
render();
