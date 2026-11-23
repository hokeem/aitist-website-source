from pathlib import Path
p=Path('dist');s=(p/'assets/sand.js').read_text()
s=s.replace("const hero = document.querySelector('.sand-hero');", "const theme=Number(new URLSearchParams(location.search).get('theme')||0);\nconst hero = document.querySelector('.sand-hero');")
s=s.replace('(3.4 + floor(random * 4.0) * .65)', '(6.0 + floor(random * 4.0) * .5)')
s=s.replace('const sources = [0,6,2,4,6,5,0,6,4,0,6,0,4,6,0,6,4,6];','const sources = [0,6,2,4,0,6];')
a=s.index('const poses =');b=s.index('\nfunction particleData',a)
s=s[:a]+'''const layouts=[
 [[.20,.48,.20],[.48,.44,.24],[.80,.42,.20],[.65,.70,.08],[.33,.68,.07],[.88,.65,.06]],
 [[.34,.70,.19],[.42,.55,.22],[.50,.40,.24],[.60,.23,.18],[.76,.54,.07],[.22,.34,.06]],
 [[.22,.45,.19],[.50,.43,.26],[.80,.41,.19],[.40,.68,.07],[.66,.67,.07],[.65,.19,.06]],
 [[.27,.50,.22],[.73,.48,.22],[.50,.44,.30],[.50,.73,.07],[.18,.24,.06],[.84,.72,.06]],
 [[.22,.48,.21],[.50,.34,.20],[.80,.25,.18],[.76,.65,.23],[.46,.67,.08],[.18,.75,.06]],
 [[.29,.29,.17],[.67,.24,.20],[.80,.54,.18],[.57,.75,.21],[.22,.64,.19],[.49,.47,.08]]
];
const poses=layouts[theme];
''' + s[b:]
s=s.replace('const elapsed = reduced.matches ? 2.8 : (now - startTime) / 1000;', 'const elapsed = 2.8 + theme*.9;')
a=s.index('  function anchorsAt(t)');b=s.index('  function hit(e)',a)
s=s[:a]+'''  function anchorsAt(t){poses.forEach((p,i)=>{positions[i*2]=p[0];positions[i*2+1]=p[1];});}
''' +s[b:]
s=s.replace('frame = requestAnimationFrame(tick);','draw(performance.now());').replace('if (visible && !document.hidden && !reduced.matches) frame = requestAnimationFrame(tick);','if (visible && !document.hidden && !reduced.matches) draw(performance.now());')
# Unique paths and no overlaid typography. Derived from the live native stone renderer.
a=s.index('// A continuous horizontal ribbon');b=s.index('\nvec2 swirl',a)
paths=[
 'return vec2(x,.47+.07*sin(x*7.0));',
 'return vec2(.48+.17*sin(a),.5+.39*cos(a));',
 'return vec2(x,.43+.10*sin(x*9.0));',
 'return vec2(.5+.34*sin(a),.47+.25*cos(a));',
 'return vec2(x,.46+.17*sin(x*7.0));',
 'return vec2(.5+.30*sin(a),.48+.28*cos(a));']
s=s[:a]+"vec2 currentPath(float a){float x=fract(a/tau)*1.8-.4;\n${["+','.join(repr(x) for x in paths)+"][theme]}\n}\n"+s[b:]
(p/'assets/cover-stage.js').write_text(s)
(p/'cover-stage.html').write_text('<!doctype html><html><head><style>html,body{margin:0;background:#111}.sand-hero,.sand-stage{height:100vh;width:100vw;position:relative}canvas{width:100%;height:100%;display:block}</style></head><body><section class="sand-hero"><div class="sand-stage"><canvas></canvas></div></section><script src="/assets/cover-stage.js"></script></body></html>')
