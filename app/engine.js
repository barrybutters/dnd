/* Pure, offline tabletop calculations shared by the UI and automated checks. */
(function(root){
const skills={'Acrobatics':'dex','Animal Handling':'wis','Arcana':'int','Athletics':'str','Deception':'cha','History':'int','Insight':'wis','Intimidation':'cha','Investigation':'int','Medicine':'wis','Nature':'int','Perception':'wis','Performance':'cha','Persuasion':'cha','Religion':'int','Sleight of Hand':'dex','Stealth':'dex','Survival':'wis'};
const mod=n=>Math.floor((Number(n??10)-10)/2),prof=level=>2+Math.floor((Math.max(1,Number(level)||1)-1)/4);
const map=(id,name='Untitled map',w=24,h=24)=>({id,name,w,h,feet:5,cells:Array(w*h).fill(0),fog:Array(w*h).fill(false),marks:[],tokens:[],image:null,grid:true,notes:''});
function normalize(s,id){s.version=2;s.settings=Object.assign({animation:true,sound:true,diceColor:'#d7b471'},s.settings);s.rolls||=[];s.role=s.role==='player'?'player':'dm';s.campaigns.forEach(c=>{for(const k of ['notes','characters','quests','npcs','sessions','items','combat','wiki','timeline','encounterPlans','library','audio','attachments','recaps'])if(!Array.isArray(c[k]))c[k]=[];c.round||=1;c.turn=Math.min(Math.max(0,c.turn||0),Math.max(0,c.combat.length-1));c.coins=Object.assign({cp:0,sp:0,ep:0,gp:0,pp:0},c.coins);c.calendar=Object.assign({day:1,weather:'Clear',travel:'',month:'Firstmoon',year:1},c.calendar);if(!c.maps?.length)c.maps=[Object.assign(map(id(),'First battlefield'),{cells:c.map?.length===576?[...c.map]:Array(576).fill(0)})];c.activeMap=c.maps.some(m=>m.id===c.activeMap)?c.activeMap:c.maps[0].id;c.maps.forEach(m=>{m.tokens||=[];m.marks||=[];m.fog||=Array(m.w*m.h).fill(false);m.feet||=5});c.characters.forEach(x=>normalizeCharacter(x));});if(!s.campaigns.some(c=>c.id===s.selected))s.selected=s.campaigns[0]?.id;return s}
function normalizeCharacter(x){x.abilities=Object.assign({str:10,dex:10,con:10,int:10,wis:10,cha:10},x.abilities);x.skills||={};x.proficiencies||=[];x.saveProf||=[];x.actions||=[];x.spells||=[];x.slots||=Array.from({length:9},()=>({max:0,used:0}));x.resources||=[];x.death||={success:0,failure:0};x.tempHp||=0;x.conditions||=[];x.speed??=30;x.currency||={cp:0,sp:0,ep:0,gp:0,pp:0};return x}
function damage(x,amount){let n=Number(amount);if(n>0){let used=Math.min(x.tempHp||0,n);x.tempHp=Math.max(0,(x.tempHp||0)-used);x.hp=Math.max(0,x.hp-(n-used))}else x.hp=Math.min(x.maxHp,x.hp-n);return x}
function skill(x,name){return Object.hasOwn(x.skills,name)?Number(x.skills[name]):mod(x.abilities[skills[name]])+(x.proficiencies.includes(name)?prof(x.level):0)}
function distance(a,b,feet=5){return Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y))*feet}
function rollExpression(expr,rng){let m=String(expr).replace(/\s/g,'').match(/^(\d{1,3})d(\d{1,4})([+-]\d{1,5})?$/i);if(!m||+m[1]<1||+m[1]>100||+m[2]<2||+m[2]>1000)throw Error('Use 1–100 dice with 2–1000 sides, such as 2d6+3.');let values=Array.from({length:+m[1]},()=>rng(+m[2])),modifier=+(m[3]||0);return{expr,values,sides:+m[2],modifier,total:values.reduce((a,b)=>a+b,modifier)}}

const finite=(v,fallback=0,min=-999999,max=999999)=>Number.isFinite(Number(v))?Math.max(min,Math.min(max,Number(v))):fallback;
function sanitize(s,id){
    if(!s||!Array.isArray(s.campaigns))throw Error('Invalid workspace.');
    const goodId=o=>{if(!/^[a-zA-Z0-9_-]{1,100}$/.test(o.id||''))o.id=id()};
    s.settings=typeof s.settings==='object'&&s.settings?s.settings:{};
    if(!/^#[a-f0-9]{6}$/i.test(s.settings.diceColor||''))s.settings.diceColor='#d7b471';
    s.rolls=Array.isArray(s.rolls)?s.rolls.filter(x=>x&&typeof x==='object').slice(0,100):[];
    s.campaigns.forEach(c=>{
        goodId(c);c.name=String(c.name||'Campaign');
        for(const k of ['notes','characters','quests','npcs','sessions','items','combat','wiki','timeline','encounterPlans','library','audio','attachments','recaps']){
            c[k]=Array.isArray(c[k])?c[k].filter(x=>x&&typeof x==='object'&&!Array.isArray(x)):[];
            c[k].forEach(x=>goodId(x));
        }
        c.maps=Array.isArray(c.maps)?c.maps.filter(m=>m&&typeof m==='object'):[];
        c.maps.forEach(m=>{
            if(m.art&&typeof m.art==='object'){
                const a=m.art;
                a.layers=(Array.isArray(a.layers)?a.layers:[]).filter(l=>l&&typeof l==='object').slice(0,20);
                if(!a.layers.length)a.layers=[{id:'ground',name:'Terrain',visible:true,locked:false,opacity:1}];
                a.layers.forEach(l=>{goodId(l);l.name=String(l.name||'Layer');l.visible=l.visible!==false;l.locked=!!l.locked;l.opacity=finite(l.opacity,1,0,1)});
                if(!a.layers.some(l=>l.id===a.activeLayer))a.activeLayer=a.layers[0].id;
                a.custom=(Array.isArray(a.custom)?a.custom:[]).filter(x=>x&&typeof x==='object'&&/^\/assets\/[a-f0-9]{32}\.(png|jpg|jpeg|webp|gif)$/.test(x.url||'')).slice(0,500);
                a.custom.forEach(x=>{goodId(x);x.name=String(x.name||'Stamp')});
                a.objects=(Array.isArray(a.objects)?a.objects:[]).filter(o=>o&&typeof o==='object'&&['paint','stamp','label','path','wall','shape'].includes(o.type)).slice(0,5000);
                a.objects.forEach(o=>{goodId(o);if(!a.layers.some(l=>l.id===o.layer))o.layer=a.layers[0].id;o.size=finite(o.size,1,.05,200);o.opacity=finite(o.opacity,1,0,1);o.angle=finite(o.angle,0,-3600,3600);o.softness=finite(o.softness,0,0,.95);o.x=finite(o.x,0,-200,300);o.y=finite(o.y,0,-200,300);o.text=String(o.text||'').slice(0,500);o.points=(Array.isArray(o.points)?o.points:[]).filter(p=>Array.isArray(p)&&p.length===2&&p.every(n=>Number.isFinite(Number(n)))).slice(0,10000).map(p=>p.map(n=>finite(n,0,-200,300)));if(!/^#[a-f0-9]{6}$/i.test(o.color||''))o.color='#695b42';if(!/^\/assets\/[a-f0-9]{32}\.(png|jpg|jpeg|webp|gif)$/.test(o.url||''))delete o.url});
            }else delete m.art;
            goodId(m);m.w=Math.round(finite(m.w,24,8,60));m.h=Math.round(finite(m.h,24,8,60));m.feet=finite(m.feet,5,1,100);
            m.cells=Array.from({length:m.w*m.h},(_,i)=>Math.round(finite(m.cells?.[i],0,0,5)));
            m.fog=Array.from({length:m.w*m.h},(_,i)=>Boolean(m.fog?.[i]));
            m.tokens=Array.isArray(m.tokens)?m.tokens.filter(t=>t&&typeof t==='object'):[];
            m.tokens.forEach(t=>{goodId(t);t.x=Math.round(finite(t.x,0,0,m.w-1));t.y=Math.round(finite(t.y,0,0,m.h-1));if(!/^#[a-f0-9]{6}$/i.test(t.color||''))t.color='#dbb576'});
            m.marks=Array.isArray(m.marks)?m.marks.filter(v=>v&&Array.isArray(v.points)):[];
            m.marks.forEach(mark=>{mark.points=mark.points.filter(p=>Array.isArray(p)&&p.length===2&&p.every(n=>Number.isFinite(Number(n))));if(!/^#[a-f0-9]{6}$/i.test(mark.color||''))mark.color='#dbb576';mark.width=finite(mark.width,3,1,12)});
        });
    });
    normalize(s,id);
    s.campaigns.forEach(c=>{
        c.dmPanels=Array.isArray(c.dmPanels)?[...new Set(c.dmPanels.filter(p=>['Party','Initiative','Quick rules','Scratchpad','Quests','Conditions'].includes(p)))]:['Party','Initiative','Quick rules','Scratchpad','Quests','Conditions'];
        if(c.relationships){const b=c.relationships;b.nodes=(Array.isArray(b.nodes)?b.nodes:[]).filter(n=>n&&typeof n==='object').slice(0,200);b.nodes.forEach(n=>{goodId(n);n.title=String(n.title||'Node');n.type=String(n.type||'Other');n.x=finite(n.x,150,80,920);n.y=finite(n.y,100,40,610)});b.edges=(Array.isArray(b.edges)?b.edges:[]).filter(e=>e&&b.nodes.some(n=>n.id===e.from)&&b.nodes.some(n=>n.id===e.to)).slice(0,1000);b.edges.forEach(e=>{goodId(e);e.label=String(e.label||'')})}
        c.recaps.forEach(r=>{r.checklist=(Array.isArray(r.checklist)?r.checklist:[]).filter(t=>t&&typeof t==='object').map(t=>({text:String(t.text||''),done:!!t.done}))});
        c.round=Math.round(finite(c.round,1,1));c.turn=Math.round(finite(c.turn,0,0,Math.max(0,c.combat.length-1)));
        c.coins=Object.fromEntries(['cp','sp','ep','gp','pp'].map(k=>[k,finite(c.coins[k],0,0)]));
        c.characters.forEach(x=>{
            x.name=String(x.name||'Adventurer');x.level=finite(x.level,1,1,100);x.maxHp=finite(x.maxHp,10,1);x.hp=finite(x.hp,x.maxHp,0,x.maxHp);x.tempHp=finite(x.tempHp,0,0);x.ac=finite(x.ac,10,0);x.speed=finite(x.speed,30,0);
            x.abilities=Object.fromEntries(['str','dex','con','int','wis','cha'].map(k=>[k,finite(x.abilities[k],10,0,99)]));
            x.skills=Object.fromEntries(Object.keys(skills).filter(k=>Object.hasOwn(x.skills,k)).map(k=>[k,finite(x.skills[k],0,-99,999)]));
            for(const k of ['proficiencies','saveProf','conditions'])x[k]=Array.isArray(x[k])?x[k].map(String):[];
            for(const k of ['actions','spells','resources']){x[k]=Array.isArray(x[k])?x[k].filter(v=>v&&typeof v==='object'):[];x[k].forEach(v=>goodId(v))}
            x.actions.forEach(a=>a.bonus=finite(a.bonus,0,-99,999));
            x.spells.forEach(sp=>sp.level=Math.round(finite(sp.level,0,0,9)));
            x.resources.forEach(r=>{r.max=finite(r.max,1,0);r.remaining=finite(r.remaining,r.max,0,r.max)});
            x.slots=Array.from({length:9},(_,i)=>{let slot=x.slots?.[i]||{},max=finite(slot.max,0,0);return{max,used:finite(slot.used,0,0,max)}});
            x.death={success:finite(x.death?.success,0,0,3),failure:finite(x.death?.failure,0,0,3)};
            x.currency=Object.fromEntries(['cp','sp','ep','gp','pp'].map(k=>[k,finite(x.currency[k],0,0)]));
        });
        c.combat.forEach(x=>{x.maxHp=finite(x.maxHp,x.hp||10,1);x.hp=finite(x.hp,x.maxHp,0,x.maxHp);x.ac=finite(x.ac,10,0);x.initiative=finite(x.initiative,0,-99,999);x.effects=Array.isArray(x.effects)?x.effects.filter(e=>e&&typeof e==='object'):[]});
        c.items.forEach(x=>{x.quantity=finite(x.quantity,1,0);x.weight=finite(x.weight,0,0)});
        c.timeline.forEach(x=>x.day=finite(x.day,1,1));
        c.calendar.day=finite(c.calendar.day,1,1);c.calendar.year=finite(c.calendar.year,1,0);
    });return s;
}

root.EmberEngine={skills,mod,prof,map,normalize:sanitize,normalizeCharacter,damage,skill,distance,rollExpression};
})(typeof module==='object'?module.exports:globalThis);
