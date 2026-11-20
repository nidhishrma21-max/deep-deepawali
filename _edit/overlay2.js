// ===== Dev Deepawali v2 – English graphics layer, timed to the voiceover cues =====
const TOTAL = TL.total, LIN = 'linear', O = 'cubic-bezier(.16,1,.3,1)', B = 'cubic-bezier(.34,1.45,.64,1)', IN = 'cubic-bezier(.7,0,.84,0)';
const Q = k => TL.cues[k].s, Qe = k => TL.cues[k].e;
const SH = Object.fromEntries(TL.shots.map(s => [s.name, s]));
const S0 = n => SH[n].start, S1 = n => SH[n].end;
const XPL = SH.blast.start + (7.25 - SH.blast.a) * (SH.blast.end - SH.blast.start) / (SH.blast.b - SH.blast.a);
const $ = s => document.querySelector(s);
const els = e => typeof e === 'string' ? [...document.querySelectorAll(e)] : (Array.isArray(e) ? e : [e]);
function track(e, prop, pts) {
  pts = pts.slice().sort((a, b) => a[0] - b[0]);
  if (pts[0][0] > 0) pts.unshift([0, pts[0][1], LIN]);
  const last = pts[pts.length - 1]; if (last[0] < TOTAL) pts.push([TOTAL, last[1]]);
  const kf = pts.map(([t, v, ez]) => ({ [prop]: v, offset: Math.max(0, Math.min(1, t / TOTAL)), easing: ez || 'ease-in-out' }));
  els(e).forEach(x => x.animate(kf, { duration: TOTAL * 1000, fill: 'both' }));
}
const fade = (e, a, b, fi = .35, fo = .3) => track(e, 'opacity', [[a, 0, LIN], [a + fi, 1, LIN], [b - fo, 1, LIN], [b, 0]]);
let _s = 11; const R = () => { _s = (_s * 16807) % 2147483647; return _s / 2147483647; }, rr = (a, b) => a + R() * (b - a), f1 = n => +n.toFixed(1);
const IMG = n => `url('../Images/${encodeURIComponent(n)}.png')`;
let H = '', A = [];
const add = (html, fn) => { H += html; if (fn) A.push(fn); };
let N = 0; const id = p => `${p}${N++}`;

// ---------- building blocks ----------
function scrim(kind, a, b) { const i = id('sc'); add(`<div class="${kind}" id="${i}"></div>`, () => fade('#' + i, a - .1, b + .1, .4, .4)); }
function title(e, a, b) {
  track(e, 'opacity', [[a, 0, LIN], [a + .5, 1, LIN], [b - .35, 1, LIN], [b, 0]]);
  track(e, 'letterSpacing', [[a, '.32em', O], [a + 1.1, '.06em', LIN], [b, '.08em']]);
  track(e, 'filter', [[a, 'blur(12px)', O], [a + .7, 'blur(0px)', LIN], [b - .35, 'blur(0px)', 'ease-in'], [b, 'blur(8px)']]);
}
function rise(e, a, b, dy = 26) { fade(e, a, b); track(e, 'transform', [[a, `translateY(${dy}px)`, O], [a + .8, 'translateY(0px)', LIN], [b, 'translateY(-8px)']]); }
function slam(e, a, b, rot = 0) { track(e, 'transform', [[a, `rotate(${rot}deg) scale(2.6)`, IN], [a + .16, `rotate(${rot}deg) scale(.94)`, 'ease-out'], [a + .3, `rotate(${rot}deg) scale(1)`, LIN], [b, `rotate(${rot}deg) scale(1.04)`]]); fade(e, a, b, .06, .2); }
function orn(top, a, b) { const i = id('o'); add(`<div class="ctr orn" id="${i}" style="top:${top}px"><i></i><b></b><i></i></div>`, () => { fade('#' + i, a, b, .3, .3); track(`#${i} i`, 'transform', [[a, 'scaleX(0)', O], [a + .9, 'scaleX(1)']]); track(`#${i} b`, 'transform', [[a, 'rotate(45deg) scale(0)', B], [a + .5, 'rotate(225deg) scale(1)']]); }); }
// caption with word-by-word reveal; *word* = highlighted
function cap(text, a, b, top = 1270, size = 52) {
  const i = id('c');
  const words = text.split(' ').map(w => w.startsWith('*') ? `<span class="w hl">${w.replace(/\*/g, '')}</span>` : `<span class="w">${w}</span>`).join(' ');
  add(`<div class="cap" id="${i}" style="top:${top}px"><span style="font-size:${size}px">${words}</span></div>`, () => {
    fade('#' + i, a, b, .05, .25);
    const ws = els(`#${i} .w`), step = Math.min(.12, Math.max(.05, (b - a - .6) * .45 / ws.length));
    ws.forEach((w, j) => { const t = a + j * step; track(w, 'opacity', [[t, 0, LIN], [t + .12, 1]]); track(w, 'transform', [[t, 'translateY(18px) scale(1.15)', B], [t + .35, 'translateY(0px) scale(1)']]); });
  });
}
function lab(kick, main, sub, a, b, top = 1300, size = 70) {
  const i = id('l');
  add(`<div class="lab" id="${i}" style="top:${top}px"><div class="bar"></div><div class="kick">${kick}</div><div class="main gold glow" style="font-size:${size}px">${main}</div>${sub ? `<div class="sub it">${sub}</div>` : ''}</div>`, () => {
    fade('#' + i, a, b, .25, .3);
    track(`#${i} .bar`, 'transform', [[a, 'scaleY(0)', O], [a + .5, 'scaleY(1)']]);
    track(`#${i} .kick`, 'transform', [[a + .05, 'translateX(-30px)', O], [a + .7, 'translateX(0px)']]);
    track(`#${i} .main`, 'clipPath', [[a + .1, 'inset(-20px 100% -20px 0)', O], [a + .8, 'inset(-20px -5% -20px 0)']]);
    if ($(`#${i} .sub`)) track(`#${i} .sub`, 'opacity', [[a + .45, 0, LIN], [a + .9, 1]]);
  });
}
function chip(n, icon, t1, t2, a, b) {
  const i = id('ch');
  add(`<div class="chip" id="${i}"><div style="position:relative"><div class="ic">${icon}</div><div class="num">${n}</div></div><div><div class="t1">${t1}</div><div class="t2 gold glow">${t2}</div></div></div>`, () => {
    fade('#' + i, a, b, .15, .2);
    track(`#${i} .ic`, 'transform', [[a, 'scale(0) rotate(-120deg)', B], [a + .5, 'scale(1) rotate(0deg)']]);
    track(`#${i} .t1`, 'transform', [[a + .08, 'translateX(-40px)', O], [a + .6, 'translateX(0px)']]);
    track(`#${i} .t2`, 'clipPath', [[a + .12, 'inset(-20px 100% -20px 0)', O], [a + .7, 'inset(-20px -5% -20px 0)']]);
  });
}
// chariot parts: a list that builds up; the newest row is bright, earlier rows stay visible but dimmed
function buildList(items, end) {
  const i = id('bl');
  const row = ([ic, a, b], j) => `<div class="row" id="${i}r${j}" style="display:flex;align-items:center;gap:22px;height:86px;opacity:0;transform-origin:0 50%"><div class="ic" style="width:68px;height:68px;flex:none;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:38px;background:radial-gradient(circle at 35% 30%,#3a2a12,#120c06);border:3px solid #f0c060;box-shadow:0 0 18px rgba(255,190,90,.6)">${ic}</div><div style="font:800 40px Montserrat,sans-serif;color:#fff;text-shadow:0 3px 12px rgba(0,0,0,.9);white-space:nowrap">${a} <span style="color:#f0c060">→</span> <span class="cz gold" style="font-size:44px;letter-spacing:.03em">${b}</span></div></div>`;
  add(`<div class="abs" id="${i}" style="left:60px;top:1110px;width:860px">${items.map(row).join('')}</div>`, () => {
    items.forEach((it, j) => {
      const a = Q(it[3]) - .05, nxt = j + 1 < items.length ? Q(items[j + 1][3]) - .05 : end + 30, r = `#${i}r${j}`;
      track(r, 'opacity', j + 1 < items.length ? [[a, 0, LIN], [a + .25, 1, LIN], [nxt, 1, LIN], [nxt + .3, .55, LIN], [end - .3, .55, LIN], [end, 0]] : [[a, 0, LIN], [a + .25, 1, LIN], [end - .3, 1, LIN], [end, 0]]);
      track(r, 'transform', [[a, 'translateX(-60px) scale(1.08)', O], [a + .5, 'translateX(0px) scale(1.08)', LIN], [Math.min(nxt, end), 'translateX(0px) scale(1.08)', 'ease-out'], [Math.min(nxt + .3, end + .1), 'translateX(0px) scale(.94)']]);
      track(`${r} .ic`, 'transform', [[a, 'scale(0) rotate(-120deg)', B], [a + .45, 'scale(1) rotate(0deg)']]);
    });
  });
}
function card(img, name, quote, a, b) {
  const i = id('cd');
  const words = quote.split(' ').map(w => `<span class="w" style="display:inline-block">${w}</span>`).join(' ');
  add(`<div class="card" id="${i}"><div class="ring"><div style="background-image:${IMG(img)}"></div></div><div><div class="nm gold glow">${name}</div><div class="q it">${words}</div></div></div>`, () => {
    fade('#' + i, a, b, .25, .3);
    track(`#${i} .ring`, 'transform', [[a, 'scale(.3) rotate(-100deg)', B], [a + .7, 'scale(1) rotate(0deg)']]);
    track(`#${i} .nm`, 'clipPath', [[a + .2, 'inset(-20px 100% -20px 0)', O], [a + .9, 'inset(-20px -5% -20px 0)']]);
    els(`#${i} .w`).forEach((w, j) => { const t = a + .5 + j * .09; track(w, 'opacity', [[t, 0, LIN], [t + .25, 1]]); track(w, 'transform', [[t, 'translateY(14px)', O], [t + .5, 'translateY(0px)']]); });
  });
}
function big(html, a, b, top, how = 'title') { const i = id('b'); add(`<div class="big" id="${i}" style="top:${top}px">${html}</div>`, () => how === 'slam' ? slam('#' + i, a, b) : (how === 'rise' ? rise('#' + i, a, b) : title('#' + i, a, b))); }

function build() {
  // ambient gold dust
  let dust = '';
  for (let i = 0; i < 24; i++) { const z = f1(rr(3, 7)); dust += `<div class="dust" style="left:${f1(rr(0, 1080))}px;top:${f1(rr(300, 1900))}px;width:${z}px;height:${z}px;--dx:${f1(rr(-60, 60))}px;--dy:${f1(rr(-520, -260))}px;animation-delay:-${f1(rr(0, 6))}s;animation-duration:${f1(rr(5, 9))}s"></div>`; }
  add(`<div id="dust" class="abs" style="inset:0">${dust}</div>`, () => track('#dust', 'opacity', [[0, 0, LIN], [1, .75, LIN], [S0('pause'), .75, LIN], [S0('pause') + .2, 0, LIN], [S0('celebrate'), 0, LIN], [S0('celebrate') + 1, .75, LIN], [TOTAL - .4, .75, LIN], [TOTAL, 0]]));
  // light leaks on selected cuts
  ['gods_diwali', 'tarakasur', 'cities_tilt', 'chariot', 'agni', 'celebrate', 'venue', 'arrival', 'dev_deep', 'diya'].forEach(n => {
    const i = id('lk'), r = rr(520, 820), t = S0(n);
    add(`<div class="leak" id="${i}" style="left:${f1(rr(-300, 600))}px;top:${f1(rr(-200, 1300))}px;width:${f1(r * 2)}px;height:${f1(r * 2)}px"></div>`, () => track('#' + i, 'opacity', [[t - .2, 0, LIN], [t + .12, .6, 'ease-out'], [t + .9, 0]]));
  });

  // ---------- HOOK ----------
  cap('Diwali is over…', Q('1.0'), Q('1.1') - .1, 1300, 62);
  cap('But do you *know?*', Q('1.1'), S1('diwali_over') + .05, 1300, 62);
  scrim('scC', S0('gods_diwali'), S1('gods_diwali'));
  big(`<div class="kick" style="margin-bottom:22px">Hold on…</div><div class="cz gold glow" style="font-size:104px;line-height:1.05">The Gods'<br>Diwali</div>`, Q('1.2'), S1('gods_diwali') + .05, 700);
  big(`<div class="it" style="font-size:60px">is still to come 👀</div>`, Q('1.2') + 1.2, S1('gods_diwali') + .05, 1000, 'rise');

  // ---------- TARAKASUR ----------
  scrim('scT', S0('tarakasur'), S1('tarakasur'));
  big(`<div class="kick">Long, long ago</div>`, Q('2.0'), S1('tarakasur'), 210, 'rise');
  big(`<div class="cz gold glow" style="font-size:118px">Tarakasur</div>`, Q('2.0') + .25, S1('tarakasur'), 270);
  big(`<div class="it" style="font-size:56px">had three sons</div>`, Q('2.1'), S1('tarakasur'), 420, 'rise');
  scrim('scB', S0('names'), S1('names'));
  lab('Son no. 1', 'Tarakaksh', '', Q('2.2'), Q('2.3') - .02);
  lab('Son no. 2', 'Kamalaksh', '', Q('2.3'), Q('2.4') - .02);
  lab('Son no. 3', 'Vidyunmali', '', Q('2.4'), S1('names'));
  scrim('scB', S0('three_cities'), S1('three_cities'));
  cap('They owned *3* *flying* *cities*', Q('2.5'), S1('three_cities'));
  scrim('scB', S0('cities_tilt'), S1('cities_tilt'));
  lab('City of Gold', 'In Heaven', '', Q('2.7'), Q('2.8') - .05);
  lab('City of Silver', 'In the Sky', '', Q('2.8'), Q('2.9') - .05);
  lab('City of Iron', 'On Earth', '', Q('2.9'), S1('cities_tilt'));

  // ---------- BOON ----------
  scrim('scT', S0('boon'), S1('boon'));
  big(`<div class="kick">And they had</div>`, Q('3.0'), S1('boon'), 220, 'rise');
  big(`<div class="cz gold glow" style="font-size:124px">A Boon</div>`, Q('3.0') + .3, S1('boon'), 285);
  // alignment graphic on the three-cities still
  const al = S0('align');
  add(`<div class="alnL" id="aln" style="top:380px;height:1060px"></div>${[420, 905, 1370].map((y, j) => `<div class="node" id="nd${j}" style="left:540px;top:${y}px"></div>`).join('')}`, () => {
    track('#aln', 'opacity', [[al + .8, 0, LIN], [al + 1.0, 1, LIN], [S1('align') - .2, 1, LIN], [S1('align'), 0]]);
    track('#aln', 'transform', [[al + .8, 'scaleY(0)', O], [al + 1.8, 'scaleY(1)']]);
    [0, 1, 2].forEach(j => { const t = al + .3 + j * .25; fade('#nd' + j, t, S1('align'), .1, .2); track('#nd' + j, 'transform', [[t, 'scale(2.4)', O], [t + .5, 'scale(1)', LIN], [t + 1.2, 'scale(1.15)', 'ease-in-out'], [t + 1.8, 'scale(1)']]); });
  });
  scrim('scT', S0('align'), S1('align'));
  cap('Once in *1,000* *years*, all 3 in *ONE* *line*', Q('3.2'), S1('align'), 170, 50);
  scrim('scB', S0('one_arrow'), S1('one_arrow'));
  cap('and only *ONE* *ARROW* could destroy them', Q('3.3'), S1('one_arrow'));

  // ---------- 3 / 3 / 1 ----------
  const kin = (num, word, a, b) => big(`<div class="cz white" style="font-size:300px;line-height:.9"><span class="gold glow" style="display:inline-block;padding:0 20px">${num}</span></div><div class="cz white" style="font-size:118px">${word}</div>`, a, b, 640, 'slam');
  kin('3', 'Brothers', S0('brothers'), S1('brothers'));
  kin('3', 'Cities', S0('cities3'), S1('cities3'));
  kin('1', 'Arrow', S0('arrow1'), S1('arrow1'));
  big(`<span class="stamp">Impossible</span>`, Q('5.0') + .1, S1('impossible'), 820, 'slam');
  scrim('scC', S0('unless'), S1('unless'));
  big(`<div class="it" style="font-size:84px">Unless…<br>you are</div>`, Q('5.1'), S1('unless') + .05, 780, 'rise');

  // ---------- CHARIOT ----------
  scrim('scT', S0('chariot'), S1('chariot'));
  big(`<div class="kick">Then came</div>`, Q('6.0'), S1('chariot'), 200, 'rise');
  big(`<div class="cz gold glow" style="font-size:84px;line-height:1.1">History's<br>Biggest Chariot</div>`, Q('6.0') + .3, S1('chariot'), 262);
  scrim('scB', S0('chariot_list'), S1('vishnu'));
  buildList([['🌍', 'Earth', 'the Chariot', '6.1'], ['☀️', 'Sun & Moon', 'the Wheels', '6.2'], ['🪷', 'Brahma Ji', 'Charioteer', '6.3'],
             ['⛰️', 'Mount Meru', 'the Bow', '6.4'], ['🐍', 'Vasuki Naag', 'Bowstring', '6.5'], ['🏹', 'Vishnu Ji', 'the Arrow', '6.6']], S1('vishnu'));
  scrim('scB', S0('agni'), S1('agni'));
  card('Agni Dev', 'Agni Dev', 'sat right on the arrow’s tip 🔥', Q('6.7') + .1, S1('agni'));

  // ---------- MAHADEV ----------
  scrim('scT', S0('aligned'), S1('aligned'));
  cap('When all 3 cities came in *ONE* *line*…', Q('7.0'), S1('aligned'), 200, 50);
  const p = S0('pause');
  add(`<div id="dip"></div>${[0, 1, 2].map(j => `<div class="pulse" id="pl${j}" style="left:340px;top:760px;width:400px;height:400px"></div>`).join('')}`, () => {
    track('#dip', 'opacity', [[S1('unless') - .45, 0, 'ease-in'], [S1('unless') - .02, 1, LIN], [S1('unless') + .05, 0, LIN], [p - .1, 0, LIN], [p + .05, 1, LIN], [S1('pause') - .02, 1, LIN], [S1('pause'), 0]]);
    [0, 1, 2].forEach(j => { const a = p + .1 + j * .42; track('#pl' + j, 'opacity', [[a, 0, LIN], [a + .05, .85, LIN], [a + .8, 0]]); track('#pl' + j, 'transform', [[a, 'scale(.4)', O], [a + .8, 'scale(2.3)']]); });
  });
  scrim('scB', S0('mahadev'), S1('mahadev'));
  lab('Then', 'Mahadev 🔱', 'lifted his bow', Q('7.1') + .05, Q('7.2') - .1);
  cap('…and fired just *ONE* *arrow*', Q('7.2'), S1('mahadev'));
  add(`<div id="flash"></div>`, () => {
    const bt = S0('blast');
    track('#flash', 'opacity', [[S0('mahadev') - .02, 0, LIN], [S0('mahadev'), .95, 'ease-out'], [S0('mahadev') + .45, 0, LIN], [XPL - .05, 0, 'ease-out'], [XPL + .12, .9, 'ease-in'], [XPL + .9, 0]]);
  });
  scrim('scC', XPL + .3, S1('tripurari'));
  big(`<div class="kick">That's why he is called</div>`, XPL + .45, S1('tripurari'), 690, 'rise');
  big(`<div class="cz gold glow" style="font-size:150px">Tripurari</div>`, Math.max(XPL + .6, Q('7.4') + .3), S1('tripurari'), 770);
  orn(950, Math.max(XPL + 1.0, Q('7.4') + .7), S1('tripurari'));
  big(`<div class="it" style="font-size:62px">Destroyer of the<br>Three Cities</div>`, Q('7.5'), S1('tripurari'), 1000, 'rise');

  // ---------- CELEBRATION ----------
  scrim('scB', S0('celebrate'), S1('celebrate'));
  cap('A victory this big? Time to *CELEBRATE!* 🎉', Q('8.0'), S1('celebrate'));
  scrim('scB', S0('venue'), S1('venue'));
  lab('Venue', 'Kashi', 'the city of Mahadev', Q('8.2'), Q('8.5') - .1);
  lab('Date', 'Kartik Purnima', 'the full-moon night', Q('8.5'), S1('venue'), 1300, 64);
  scrim('scB', S0('chandra'), S1('agni_diyas'));
  lab('Moonlight by', 'Chandra Dev 🌕', '', Q('8.7'), S1('chandra'));
  lab('Lakhs of diyas by', 'Agni Dev 🔥', '', Q('8.8'), S1('agni_diyas'));
  scrim('scB', S0('vayu'), S1('vayu'));
  card('Vayu dev', 'Vayu Dev', '“Not one diya goes out tonight.” 🙏', Q('8.9') + .1, S1('vayu'));
  scrim('scB', S0('vimaan'), S1('vimaan'));
  cap('So many gods came…', Q('9.0'), Q('9.2') - .1);
  big(`<div class="sign"><span class="p">P</span><span class="t"><div class="a">VIP VIMAAN</div><div class="b">PARKING FULL</div></span></div>`, Q('9.2'), S1('vimaan'), 1270, 'slam');

  // ---------- ENDING ----------
  scrim('scB', S0('arrival'), S1('arrival'));
  cap('On this night, the *gods* *themselves* come down to the ghats of *Kashi*', Q('10.1'), S1('arrival'), 1250, 48);
  scrim('scT', S0('dev_deep'), S1('dev_deep'));
  big(`<div class="kick">That's why it's called</div>`, Q('10.2'), S1('dev_deep'), 190, 'rise');
  big(`<div class="cz gold glow" style="font-size:132px;line-height:1.02">Dev<br>Deepawali</div>`, Q('10.2') + .5, S1('dev_deep'), 250);
  big(`<div class="it" style="font-size:58px">the Diwali of the Gods</div>`, Q('10.3'), S1('dev_deep'), 540, 'rise');
  scrim('scB', S0('purnima'), S1('nanak'));
  lab('Right after Diwali', 'Kartik Purnima 🌕', '', Q('10.4'), S1('purnima'), 1300, 64);
  lab('Same day', 'Guru Nanak Jayanti', '🙏', Q('10.6'), S1('nanak'), 1300, 58);
  scrim('scC', S0('diya'), S1('diya'));
  big(`<div class="date"><div class="m">NOVEMBER</div><div class="d">24</div><div class="w">TUESDAY</div></div>`, Q('10.7'), S1('diya') + .05, 560, 'slam');
  big(`<div class="it" style="font-size:66px">Light one diya too 🪔</div>`, Q('10.8'), S1('diya') + .05, 1010, 'rise');

  // ---------- END CARD ----------
  const e0 = S0('endcard'), E9 = TOTAL + 1;
  big(`<div class="it gold glow" style="font-size:104px">Har Har Mahadev</div>`, e0 + .2, E9, 380);
  orn(525, e0 + .6, E9);
  big(`<div class="kick">Comment below</div><div class="cz white" style="font-size:64px;line-height:1.2;margin-top:18px">Which god would<br>YOU be? 👇</div>`, e0 + .8, E9, 640, 'rise');
  const avs = [['Narad Muni', 'Narad'], ['Indra Dev', 'Indra'], ['Agni Dev', 'Agni'], ['Vayu dev', 'Vayu'], ['Chandra Dev', 'Chandra'], ['Nandi', 'Nandi']];
  add(`<div class="abs" style="left:40px;top:940px;width:900px;display:flex;justify-content:space-between">${avs.map(([f, n], j) => `<div id="av${j}" style="width:140px;text-align:center;opacity:0"><div class="ring" style="width:136px;height:136px;padding:5px"><div style="background-image:${IMG(f)}"></div></div><div class="kick" style="font-size:19px;letter-spacing:.2em;margin-top:12px">${n}</div></div>`).join('')}</div>`, () => {
    avs.forEach((_, j) => { const a = e0 + 1.2 + j * .1; fade('#av' + j, a, E9, .25, .1); track('#av' + j, 'transform', [[a, 'translateY(40px) scale(.6)', B], [a + .55, 'translateY(0px) scale(1)']]); });
  });
  big(`<div class="kick" style="font-size:20px;opacity:.85">Katha: as told in the Shiv Purana</div>`, e0 + 1.8, E9, 1240, 'rise');

  $('#stage').innerHTML = H;
  A.forEach(f => f());
}

window.seek = t => { const ms = t * 1000; document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms; }); };
Promise.all([document.fonts.ready, ...['900 80px Cinzel', '700 80px Cinzel', 'italic 700 60px "Cormorant Garamond"', '800 52px Montserrat', '900 40px Montserrat', '700 27px Montserrat'].map(f => document.fonts.load(f).catch(() => 0)),
  ...['Agni Dev', 'Vayu dev', 'Nandi', 'Narad Muni', 'Indra Dev', 'Chandra Dev'].map(n => new Promise(r => { const i = new Image(); i.onload = i.onerror = r; i.src = `../Images/${n}.png`; }))])
  .then(() => { build(); window.READY = true; });
