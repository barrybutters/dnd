/* Fifty original vector portrait tokens. Shared by gallery, map and TV display. */
(function(root){const roles=['Warrior','Scout','Ranger','Mage','Cleric','Bard','Paladin','Druid','Monk','Adventurer'],styles=['Hooded','Armoured','Braided','Bearded','Masked'];const colors=['#b45448','#497f68','#4f7894','#796299','#b0904d','#a46389','#697e9f','#60824b','#ab7951','#598d89'];const catalog=roles.flatMap((role,r)=>styles.map((style,s)=>({id:'hero-'+(r*5+s+1).toString().padStart(2,'0'),name:style+' '+role,role,style,r,s,color:colors[r]})));
function draw(ctx,id,x,y,r){const t=catalog.find(t=>t.id===id);if(!t)return false;ctx.save();ctx.translate(x,y);ctx.scale(r/64,r/64);ctx.beginPath();ctx.arc(0,0,63,0,7);ctx.fillStyle=t.color;ctx.fill();ctx.clip();const grad=ctx.createRadialGradient(-15,-20,5,0,0,80);grad.addColorStop(0,'#ffffff44');grad.addColorStop(1,'#101b2299');ctx.fillStyle=grad;ctx.fillRect(-64,-64,128,128);
const skin=['#e8bc94','#bc865f','#885b43','#d9a57e','#a57556'][(t.r+t.s)%5],hair=['#42352c','#c4a16b','#302f34','#8d4931','#d4c9af'][(t.r+2*t.s)%5];
const path=(pts,color)=>{ctx.beginPath();pts.forEach(([a,b],i)=>i?ctx.lineTo(a,b):ctx.moveTo(a,b));ctx.closePath();ctx.fillStyle=color;ctx.fill()};const ellipse=(a,b,c,d,color)=>{ctx.beginPath();ctx.ellipse(a,b,c,d,0,0,7);ctx.fillStyle=color;ctx.fill()};
path([[-62,66],[-48,25],[-23,14],[23,14],[48,25],[62,66]],t.s===1?'#8d9b9b':t.color);path([[-24,18],[0,45],[24,18],[16,64],[-16,64]],'#d8c7a0');ctx.fillStyle=skin;ctx.fillRect(-10,7,20,25);
if(t.s===0){ellipse(0,-13,37,42,'#26372f');path([[-37,-7],[-31,22],[-18,8],[0,27],[18,8],[31,22],[37,-7]],'#26372f')}
else ellipse(0,-16,29,32,hair);
ellipse(0,-7,23,29,skin);if(t.s===1){path([[-29,-21],[-20,-39],[17,-39],[29,-21],[25,-5],[16,-15],[-16,-15],[-25,-5]],'#abb7b0');ctx.fillStyle='#d4b472';ctx.fillRect(-3,-37,6,23)}
if(t.s===2){path([[-26,-17],[-22,-38],[17,-34],[29,-19],[7,-25],[-10,-20]],hair);for(let i=0;i<7;i++)ellipse(24,4+i*6,5,5,hair)}
if(t.s===3){path([[-23,0],[-16,28],[0,39],[16,28],[23,0],[12,13],[-12,13]],hair);path([[-25,-25],[-18,-37],[17,-37],[26,-20],[1,-26]],hair)}
if(t.s===4){path([[-25,-2],[25,-2],[21,22],[0,31],[-21,22]],'#263d43');ctx.strokeStyle='#d6c38e';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-20,7);ctx.lineTo(20,7);ctx.stroke()}
ctx.strokeStyle='#302c28';ctx.lineWidth=2.5;for(const a of [-9,9]){ctx.beginPath();ctx.moveTo(a-3,-9);ctx.lineTo(a+3,-9);ctx.stroke()}ctx.strokeStyle='#9a674e';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(1,-4);ctx.lineTo(-1,4);ctx.lineTo(3,4);ctx.stroke();
if(t.s!==3&&t.s!==4){ctx.strokeStyle='#83513e';ctx.beginPath();ctx.moveTo(-6,12);ctx.quadraticCurveTo(0,15,7,11);ctx.stroke()}
// Distinct class equipment rather than letters or simple colour swaps.
ctx.save();ctx.translate(-38,28);ctx.strokeStyle='#f1dca6';ctx.fillStyle='#f1dca6';ctx.lineWidth=4;ctx.lineCap='round';const line=(a,b,c,d)=>{ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke()};
if([0,6,8].includes(t.r)){line(0,-27,0,28);path([[0,-32],[-7,-18],[0,4],[7,-18]],'#dce1d7');line(-10,5,10,5);if(t.r===6)path([[10,10],[25,10],[24,29],[17,37],[10,29]],'#d7b471')}
else if(t.r===1||t.r===2){ctx.beginPath();ctx.moveTo(0,-28);ctx.quadraticCurveTo(27,0,0,28);ctx.stroke();ctx.lineWidth=1.5;line(0,-28,0,28);line(-7,-8,20,12)}
else if(t.r===3||t.r===7){line(0,-24,0,35);ellipse(0,-26,9,9,t.r===7?'#a5c773':'#97c4db');if(t.r===7){line(0,-20,-13,-33);line(0,-20,13,-33)}}
else if(t.r===4){line(0,-28,0,31);line(-13,-14,13,-14);ellipse(0,-14,6,6,'#f4e0ac')}
else if(t.r===5){ellipse(0,8,13,17,'#c7a168');line(0,-25,0,13);ctx.lineWidth=1;for(let a=-4;a<=4;a+=4)line(a,-23,a,17);ellipse(0,7,4,5,'#3e382f')}
else {path([[-10,-14],[10,-14],[17,25],[-17,25]],'#b7a479');ctx.fillStyle='#695b43';ctx.fillRect(-6,-4,12,10);line(-5,-14,-5,-22);line(5,-14,5,-22);line(-5,-22,5,-22)}ctx.restore();ctx.restore();ctx.save();ctx.translate(x,y);ctx.beginPath();ctx.arc(0,0,r*.97,0,7);ctx.strokeStyle='#e2c488';ctx.lineWidth=Math.max(1.5,r*.055);ctx.stroke();ctx.restore();return true;}
root.EmberTokens={catalog,draw};if(typeof module!=='undefined')module.exports=root.EmberTokens;
})(globalThis);
