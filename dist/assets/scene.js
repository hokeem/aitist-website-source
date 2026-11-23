// Zenith 3D: a sand river that pours into a GPU module and leaves as gold.
// Modes: hero (river + GPU), story (one object per step, sand orbit), cover (static research art).
import * as THREE from './vendor/three.module.min.js';

// ---------- geometry ----------
function crystalGeometry() {
  const pts = [[0, -1.5], [.42, -1.0], [.5, -.75], [.5, .8], [.4, 1.05], [0, 1.65]].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.LatheGeometry(pts, 6).toNonIndexed(); g.computeVertexNormals(); return g;
}
function slabGeometry(w = 2.2, h = 2.2, d = .16, r = .18, bev = .03) {
  const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
  const g = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: true, bevelThickness: bev, bevelSize: bev, bevelSegments: 4, curveSegments: 12 });
  g.center(); return g;
}

// ---------- textures ----------
function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
const chipMaps = () => {
  const draw = (metal) => (g, w, h) => {
    g.fillStyle = metal ? '#000' : '#131416'; g.fillRect(0, 0, w, h);
    const m = 70; g.strokeStyle = metal ? '#fff' : '#b8955a'; g.fillStyle = metal ? '#fff' : '#c9a86a';
    // pads around the edge
    for (let i = 0; i < 18; i++) { const t = m + 30 + i * ((w - 2 * m - 60) / 17); g.fillRect(t - 7, 22, 14, 34); g.fillRect(t - 7, h - 56, 14, 34); g.fillRect(22, t - 7, 34, 14); g.fillRect(w - 56, t - 7, 34, 14); }
    // traces
    g.lineWidth = 3; g.globalAlpha = metal ? 1 : .55;
    for (let i = 0; i < 18; i++) { const t = m + 30 + i * ((w - 2 * m - 60) / 17), c = w / 2, k = (t - c) * .45 + c;
      g.beginPath(); g.moveTo(t, 56); g.lineTo(t, 130); g.lineTo(k, 300); g.stroke();
      g.beginPath(); g.moveTo(t, h - 56); g.lineTo(t, h - 130); g.lineTo(k, h - 300); g.stroke();
      g.beginPath(); g.moveTo(56, t); g.lineTo(130, t); g.lineTo(300, k); g.stroke();
      g.beginPath(); g.moveTo(w - 56, t); g.lineTo(w - 130, t); g.lineTo(w - 300, k); g.stroke(); }
    g.globalAlpha = 1;
    // die
    g.fillStyle = metal ? '#888' : '#1d1e21'; g.fillRect(300, 300, w - 600, h - 600);
    g.strokeStyle = metal ? '#fff' : '#c9a86a'; g.lineWidth = 2; g.strokeRect(300, 300, w - 600, h - 600);
    g.globalAlpha = metal ? .6 : .25; for (let x = 320; x < w - 300; x += 26) { g.beginPath(); g.moveTo(x, 310); g.lineTo(x, h - 310); g.stroke(); }
  };
  return { map: canvasTex(1024, 1024, draw(false)), metal: canvasTex(1024, 1024, draw(true), false) };
};


// cap UVs of an extruded slab -> 0..1 over its footprint
function capUV(g, w, h) { const uv = g.attributes.uv, p = g.attributes.position; for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / w + .5, p.getY(i) / h + .5); }

const pcbMaps = () => {
  const W = 1840, H = 1160;
  const draw = (metal) => (g) => {
    g.fillStyle = metal ? '#000' : '#0c100e'; g.fillRect(0, 0, W, H);
    let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    if (!metal) {
      g.lineWidth = 2; g.strokeStyle = 'rgba(120,150,130,.10)';
      for (let i = 0; i < 520; i++) { let x = rnd() * W, y = rnd() * H; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 4; k++) { if (k % 2) x += (rnd() - .5) * 360; else y += (rnd() - .5) * 260; g.lineTo(x, y); } g.stroke(); }
      g.fillStyle = 'rgba(200,205,195,.35)'; g.font = '600 26px Inter, Arial'; g.fillText('ZENITH  ·  INFERENCE MODULE', 70, H - 64);
      g.fillText('SXM', W - 150, H - 64);
    }
    g.fillStyle = metal ? '#fff' : '#c9a86a';
    for (let i = 0; i < 700; i++) { const x = rnd() * W, y = rnd() * H; g.beginPath(); g.arc(x, y, 3, 0, 7); g.fill(); }
    // mounting holes
    for (const [x, y] of [[60, 60], [W - 60, 60], [60, H - 60], [W - 60, H - 60], [W / 2, 60], [W / 2, H - 60]]) { g.lineWidth = 10; g.strokeStyle = metal ? '#fff' : '#c9a86a'; g.beginPath(); g.arc(x, y, 22, 0, 7); g.stroke(); }
    // edge connector pads
    for (let i = 0; i < 64; i++) g.fillRect(300 + i * 19.5, 14, 11, 34);
    // die outline glow traces around the package
    g.strokeStyle = metal ? '#fff' : 'rgba(201,168,106,.55)'; g.lineWidth = 3;
    for (let i = 0; i < 28; i++) { const y = 300 + i * 20; g.beginPath(); g.moveTo(420, y); g.lineTo(250, y + (i - 14) * 6); g.stroke(); g.beginPath(); g.moveTo(W - 420, y); g.lineTo(W - 250, y + (i - 14) * 6); g.stroke(); }
  };
  return { map: canvasTex(W, H, draw(false)), metal: canvasTex(W, H, draw(true), false) };
};
const dieMap = () => canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#6a6c70'; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(255,255,255,.18)'; g.lineWidth = 1.5;
  for (let x = 0; x < w; x += 32) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
  for (let y = 0; y < h; y += 32) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  g.fillStyle = 'rgba(255,255,255,.06)'; for (let i = 0; i < 40; i++) g.fillRect((Math.random() * 16 | 0) * 32, (Math.random() * 16 | 0) * 32, 32, 32);
});

const GOLD = new THREE.Color('#e3b96b');
function makeGPU() {
  const root = new THREE.Group(), board = new THREE.Group(); root.add(board);
  const { map, metal } = pcbMaps();
  const pcbTop = new THREE.MeshPhysicalMaterial({ map, metalnessMap: metal, metalness: 1, roughness: .5, clearcoat: .5, clearcoatRoughness: .3, envMapIntensity: 1 });
  const pcbSide = new THREE.MeshStandardMaterial({ color: '#15130f', roughness: .6, metalness: .3 });
  const pg = slabGeometry(4.6, 2.9, .08, .14, .025); capUV(pg, 4.65, 2.95);
  const pcb = new THREE.Mesh(pg, [pcbTop, pcbSide]); board.add(pcb);
  const subMat = new THREE.MeshPhysicalMaterial({ color: '#1b1c1f', metalness: .6, roughness: .35, clearcoat: 1, clearcoatRoughness: .1, envMapIntensity: 1.1 });
  const sub = new THREE.Mesh(slabGeometry(2.2, 1.8, .04, .08, .015), subMat); sub.position.z = .1; board.add(sub);
  const frameMat = new THREE.MeshStandardMaterial({ color: '#c9a86a', metalness: 1, roughness: .25 });
  const frameShape = new THREE.Shape(); frameShape.moveTo(-1.08, -.88); frameShape.lineTo(1.08, -.88); frameShape.lineTo(1.08, .88); frameShape.lineTo(-1.08, .88); frameShape.lineTo(-1.08, -.88);
  const hole = new THREE.Path(); hole.moveTo(-1.03, -.83); hole.lineTo(-1.03, .83); hole.lineTo(1.03, .83); hole.lineTo(1.03, -.83); hole.lineTo(-1.03, -.83); frameShape.holes.push(hole);
  const frame = new THREE.Mesh(new THREE.ExtrudeGeometry(frameShape, { depth: .012, bevelEnabled: false }), frameMat); frame.position.z = .14; board.add(frame);
  const dg = slabGeometry(1.0, .92, .03, .025, .008); capUV(dg, 1.02, .94);
  const dieMat = new THREE.MeshPhysicalMaterial({ map: dieMap(), color: '#d4d7dc', metalness: 1, roughness: .2, iridescence: 1, iridescenceIOR: 1.8, iridescenceThicknessRange: [260, 760], clearcoat: 1, clearcoatRoughness: .04, envMapIntensity: 1.5 });
  const die = new THREE.Mesh(dg, dieMat); die.position.z = .155; board.add(die);
  const hbmMat = new THREE.MeshPhysicalMaterial({ color: '#2c2e33', metalness: .85, roughness: .22, clearcoat: 1, clearcoatRoughness: .08, envMapIntensity: 1.2 });
  const hg = slabGeometry(.3, .4, .04, .03, .01);
  for (const x of [-.74, .74]) for (const y of [-.44, 0, .44]) { const m = new THREE.Mesh(hg, hbmMat); m.position.set(x, y, .15); board.add(m); }
  // components: VRM rows and capacitor fields, instanced
  const compMat = new THREE.MeshStandardMaterial({ color: '#b8b4ab', metalness: 1, roughness: .3, envMapIntensity: 1.1 });
  const darkComp = new THREE.MeshStandardMaterial({ color: '#202124', metalness: .5, roughness: .4 });
  const cg = new THREE.BoxGeometry(.07, .04, .035), ig = new THREE.BoxGeometry(.16, .16, .06);
  const caps = new THREE.InstancedMesh(cg, compMat, 420), inds = new THREE.InstancedMesh(ig, darkComp, 36), M = new THREE.Matrix4();
  let n = 0;
  for (const sx of [-1, 1]) for (let r = 0; r < 14; r++) for (let c = 0; c < 15 && n < 420; c++) { M.makeTranslation(sx * (1.32 + c * .06), -1.05 + r * .16, .075); caps.setMatrixAt(n++, M); }
  let k = 0; for (const sx of [-1, 1]) for (let r = 0; r < 9; r++) for (let c = 0; c < 2; c++) { M.makeTranslation(sx * (1.3 + .55 + c * .2) + sx * .18, -1.0 + r * .25, .09); inds.setMatrixAt(k++, M); }
  caps.count = n; board.add(caps, inds);
  const base = { die: dieMat.color.clone(), hbm: hbmMat.color.clone(), sub: subMat.color.clone(), comp: compMat.color.clone() };
  root.userData = { kind: 'gpu', die,
    setGold(g) {
      dieMat.color.copy(base.die).lerp(GOLD, g); dieMat.iridescence = 1 - g; dieMat.map = g > .98 ? null : dieMat.map; dieMat.roughness = .1 + g * .08;
      hbmMat.color.copy(base.hbm).lerp(GOLD, g); hbmMat.metalness = .85 + g * .15;
      subMat.color.copy(base.sub).lerp(new THREE.Color('#4a3818'), g);
      compMat.color.copy(base.comp).lerp(GOLD, g);
      pcbTop.color.setRGB(1, 1, 1).lerp(new THREE.Color('#d9b878'), g * .55);
    } };
  return root;
}

function makeObject(kind) {
  if (kind === 'gpu' || kind === 'gpuGold') { const g = makeGPU(); if (kind === 'gpuGold') g.userData.setGold(1); g.userData.kind = kind; return g; }
  let mesh;
  if (kind === 'crystal') mesh = new THREE.Mesh(crystalGeometry(), new THREE.MeshPhysicalMaterial({ color: '#3a3630', metalness: .15, roughness: .04, clearcoat: 1, clearcoatRoughness: .02, iridescence: .75, iridescenceIOR: 1.6, iridescenceThicknessRange: [180, 620], envMapIntensity: 2.2, flatShading: true }));
  if (kind === 'chip') {
    const { map, metal } = chipMaps();
    const top = new THREE.MeshPhysicalMaterial({ map, metalnessMap: metal, metalness: 1, roughness: .32, clearcoat: 1, clearcoatRoughness: .08, envMapIntensity: 1.2 });
    const side = new THREE.MeshPhysicalMaterial({ color: '#1a1b1e', metalness: .8, roughness: .3, envMapIntensity: 1 });
    const g = slabGeometry(); capUV(g, 2.26, 2.26);
    mesh = new THREE.Mesh(g, [top, side]);
  }
  const holder = new THREE.Group(); holder.add(mesh); holder.userData.kind = kind; return holder;
}
// ---------- environment: dark studio with softboxes ----------
function studioEnv(renderer) {
  const s = new THREE.Scene();
  s.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.MeshBasicMaterial({ color: 0x0c0c0c, side: THREE.BackSide })));
  const box = (w, h, x, y, z, c) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: c, side: THREE.DoubleSide })); m.position.set(x, y, z); m.lookAt(0, 0, 0); s.add(m); };
  box(44, 18, 0, 26, 6, new THREE.Color(4.2, 4.0, 3.7));
  box(12, 34, -26, 4, 8, new THREE.Color(4.4, 4.2, 3.9));
  box(10, 30, 26, 2, -6, new THREE.Color(3.4, 3.0, 2.4));
  box(40, 30, 0, 0, 30, new THREE.Color(.5, .47, .43));
  box(30, 8, 0, -16, 14, new THREE.Color(.25, .22, .18));
  const pm = new THREE.PMREMGenerator(renderer); const t = pm.fromScene(s, .02).texture; pm.dispose(); return t;
}


// ---------- sand ----------
// river: particles travel from L, converge into the die (S), leave toward R as gold. orbit: ring around an object.
function makeSand(count, mode) {
  const g = new THREE.BufferGeometry(), seed = new Float32Array(count * 4);
  for (let i = 0; i < count * 4; i++) seed[i] = Math.random();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  g.setAttribute('seed', new THREE.BufferAttribute(seed, 4));
  const uniforms = { uTime: { value: 0 }, uPix: { value: 2 }, uMode: { value: mode === 'orbit' ? 1 : 0 }, uGold: { value: 0 },
    uL: { value: new THREE.Vector3(-8, 1, -1) }, uS: { value: new THREE.Vector3() }, uR: { value: new THREE.Vector3(8, 1, 0) },
    uW0: { value: .85 }, uW1: { value: .7 }, uSpeed: { value: .03 }, uSplit: { value: .62 } };
  const m = new THREE.ShaderMaterial({
    uniforms, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute vec4 seed; uniform float uTime,uPix,uMode,uGold,uW0,uW1,uSpeed,uSplit; uniform vec3 uL,uS,uR; varying vec3 vC; varying float vA;
      void main(){
        vec3 p; float goldK, bright = 0., a;
        vec3 sand = mix(vec3(.46,.43,.38), vec3(.92,.88,.80), fract(seed.x*97.13));
        vec3 gold = mix(vec3(.85,.58,.24), vec3(1.,.86,.52), seed.w);
        if (uMode < .5) {
          float s = fract(seed.x + uTime*uSpeed*(.75+.5*seed.w));
          vec3 c; float w;
          if (s < uSplit) {
            float q = s/uSplit, qe = mix(q, q*q*(3.-2.*q), .5);
            c = mix(uL, uS, qe);
            c.y += sin(q*5.2 - uTime*.55)*.6*(1.-q)*(1.-q);
            c.z += cos(q*3.7 - uTime*.35)*.8*(1.-q);
            w = uW0*pow(1.-q, 1.1) + .012;
            goldK = smoothstep(.82, 1., q)*.7; bright = smoothstep(.78, 1., q);
          } else {
            float q = (s-uSplit)/(1.-uSplit);
            c = mix(uS, uR, q); c.y += sin(q*3.6 + uTime*.45)*.4*q;
            w = uW1*pow(q, .85) + .012; goldK = 1.; bright = 1. - smoothstep(0., .35, q);
          }
          float strand = seed.y < .62 ? floor(seed.y/.62*7.)/7. : seed.y; float ang = strand*6.2831853 + s*9. + uTime*.35 + (seed.y < .62 ? (seed.w-.5)*.35 : 0.); float rad = seed.y < .62 ? .55 + .45*seed.z : pow(seed.z, 1.8);
          c.y += cos(ang)*rad*w; c.z += sin(ang)*rad*w*1.3; c.x += sin(ang*.7)*rad*w*.25;
          c += .025*vec3(sin(seed.w*53. + uTime*1.2), cos(seed.z*41. + uTime*1.4), sin(seed.y*37. + uTime));
          p = c;
          a = .62*(.45 + .55*(1. - rad))*clamp(w/.3, .16, 1.)*smoothstep(0., .05, s)*(1. - smoothstep(.95, 1., s));
        } else {
          float across = seed.y*2.-1.; across = sign(across)*pow(abs(across), 1.7);
          float ang = seed.x*6.2831853 + uTime*(.06 + .05*seed.z);
          float r = 2.2 + across*.24 + .05*sin(ang*5. + uTime*.5);
          p = vec3(cos(ang)*r, across*.12 + .1*sin(ang*3. + uTime*.4) + (seed.w-.5)*.06, sin(ang)*r);
          p.yz = mat2(cos(.42),-sin(.42),sin(.42),cos(.42))*p.yz;
          p.xy = mat2(cos(.18),-sin(.18),sin(.18),cos(.18))*p.xy;
          goldK = 0.; a = .5*(1. - .6*abs(across));
        }
        vC = mix(sand, gold, max(goldK, uGold)*(.6 + .4*seed.z)) * (1. + bright*1.1);
        vec4 mv = modelViewMatrix*vec4(p, 1.);
        gl_Position = projectionMatrix*mv;
        float size = uPix*(.55 + 1.5*seed.w*seed.w);
        if (seed.w > .992) { size *= 3.5; a *= .22; }
        gl_PointSize = size*(9./-mv.z);
        vA = a;
      }`,
    fragmentShader: `varying vec3 vC; varying float vA; void main(){ float d = length(gl_PointCoord - .5); float a = vA*smoothstep(.5, .12, d); if (a < .003) discard; gl_FragColor = vec4(vC*a, a); }`,
  });
  const pts = new THREE.Points(g, m); pts.frustumCulled = false; return pts;
}

// ---------- scene factory ----------
export function createScene(canvas, opts = {}) {
  const mode = opts.mode || 'hero';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: mode === 'cover', powerPreference: 'high-performance' }); } catch (e) { return null; }
  if (!renderer.getContext()) return null;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05; renderer.setClearColor(0, 0);
  const scene = new THREE.Scene(); scene.environment = studioEnv(renderer);
  const camera = new THREE.PerspectiveCamera(30, 1, .1, 100); camera.position.set(0, 0, 11);
  const key = new THREE.DirectionalLight(0xfff4e6, 1.4); key.position.set(-5, 6, 6); scene.add(key);
  const rim = new THREE.DirectionalLight(0xffe2b0, 2.2); rim.position.set(6, 2, -5); scene.add(rim);
  const small = innerWidth < 760;
  const state = { scroll: 0, step: 0, mx: 0, my: 0, visible: true, cover: opts.cover ?? 0, halfW: 5, portrait: false };
  const tmp = new THREE.Vector3(), up = new THREE.Vector3();

  let river = null, orbit = null, gpu = null, objects = [], coverCfg = null;
  const sinkOf = (o, out) => { const d = o.userData.die; if (d) { d.getWorldPosition(out); up.set(0, 0, 1).applyQuaternion(d.getWorldQuaternion(new THREE.Quaternion())); out.addScaledVector(up, .06); } else o.getWorldPosition(out); return out; };

  if (mode === 'hero') {
    river = makeSand(small ? 60000 : 150000, 'river'); scene.add(river);
    gpu = makeObject('gpu'); scene.add(gpu);
  } else if (mode === 'story') {
    orbit = makeSand(small ? 9000 : 16000, 'orbit'); scene.add(orbit);
    objects = ['crystal', 'chip', 'gpu', 'gpuGold'].map(makeObject);
    objects.forEach((o, i) => { o.scale.setScalar(i === 0 ? .9 : .001); scene.add(o); });
  } else {
    // research covers
    const C = [
      { objs: [['gpu', -2.45, .1, -.6, .82, [-.75, .4, .1]], ['gpu', 2.55, -.1, -.6, .82, [-.75, -.4, -.1]]], flow: [[-9, .9, -2], 0, 1], cam: [0, 1.6, 10.5] },
      { objs: [['crystal', 1.3, .1, .4, 1.3, [.2, .3, -.25]]], flow: [[-14, 2.2, -14], 0, [7, -.6, 2]], w0: 1.6, cam: [-.6, .8, 10.5] },
      { objs: [['gpuGold', .7, -.1, 0, 1.02, [-.8, -.3, .12]]], flow: [[-9, 1.4, -2], 0, [8, 2.2, -1]], gold: 1, cam: [0, 1.2, 10.5] },
      { objs: [['crystal', 0, 0, 0, 1.25, [0, .4, .2]]], ring: true, cam: [0, 1.0, 9.5] },
      { objs: [['chip', 0, -.1, 0, 1.3, [-1.2, .35, .3]]], ring: true, cam: [0, 1.4, 9.5] },
      { objs: [['gpu', -.4, -.1, 0, .98, [-.8, .25, -.08]]], flow: [[-9, 1.3, -2], 0, [8, 1.8, -1]], gold: 0, cam: [0, 1.2, 10.5] },
      // Apple-style tiles: object sits low, headline space on top
      { objs: [['gpu', -3.0, -1.25, -.4, .95, [-.85, .38, .08]], ['gpu', 3.1, -1.35, -.4, .95, [-.85, -.38, -.08]]], flow: [[-12, -.6, -2], 0, 1], cam: [0, 1.4, 11], look: [0, .35, 0] },
      { objs: [['crystal', .3, -.75, .6, .95, [.25, .35, -.3]]], flow: [[-10, 1.4, -12], 0, [7, -.6, 2]], w0: 1.5, cam: [-.4, .9, 11], look: [0, .4, 0] },
      { objs: [['gpuGold', 0, -.8, 0, .58, [-.95, -.32, .1]]], flow: [[-8, .1, -2], 0, [8, .9, -1]], gold: 1, cam: [0, 1.3, 11], look: [0, .3, 0] },
      { objs: [['chip', 0, -.75, 0, .85, [-1.2, .35, .3]]], ring: true, ringY: -.75, cam: [0, 1.5, 10.5], look: [0, .3, 0] },
    ];
    coverCfg = C[state.cover % C.length];
    coverCfg.objs.forEach(([k, x, y, z, s, r]) => { const o = makeObject(k); o.position.set(x, y, z); o.scale.setScalar(s); o.rotation.set(...r); scene.add(o); objects.push(o); });
    camera.position.set(...coverCfg.cam); camera.lookAt(...(coverCfg.look || [0, 0, 0]));
    scene.updateMatrixWorld(true);
    if (coverCfg.ring) { orbit = makeSand(30000, 'orbit'); orbit.material.uniforms.uPix.value = 2.2; orbit.scale.setScalar(1.15); orbit.position.y = coverCfg.ringY || 0; scene.add(orbit); }
    if (coverCfg.flow) {
      river = makeSand(140000, 'river'); scene.add(river);
      const U = river.material.uniforms, [L, si, R] = coverCfg.flow;
      U.uL.value.set(...L); sinkOf(objects[si], U.uS.value);
      if (Array.isArray(R)) U.uR.value.set(...R); else sinkOf(objects[R], U.uR.value);
      if (coverCfg.w0) U.uW0.value = coverCfg.w0;
      U.uGold.value = coverCfg.gold || 0;
    }
  }

  function resize() {
    const r = canvas.getBoundingClientRect(), w = Math.max(1, r.width), h = Math.max(1, r.height);
    const dpr = Math.min(devicePixelRatio || 1, mode === 'hero' ? 1.75 : 2);
    renderer.setPixelRatio(dpr); renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    state.halfW = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 11 * camera.aspect; state.portrait = w / h < 1;
    if (river) river.material.uniforms.uPix.value = 2.6 * dpr;
    if (orbit) orbit.material.uniforms.uPix.value = 2.2 * dpr;
  }
  resize(); addEventListener('resize', resize);
  addEventListener('pointermove', e => { state.mx = e.clientX / innerWidth - .5; state.my = e.clientY / innerHeight - .5; }, { passive: true });

  const sm = { mx: 0, my: 0, scroll: 0 };
  const sstep = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  let lastT = 0;
  function frame(t) {
    const dt = Math.min(.1, Math.max(0, t - lastT)); lastT = t; const ease = r => 1 - Math.exp(-dt * r);
    if (river) river.material.uniforms.uTime.value = t;
    if (orbit) orbit.material.uniforms.uTime.value = t;
    if (mode === 'cover') { renderer.render(scene, camera); return; }
    sm.mx += (state.mx - sm.mx) * ease(2.4); sm.my += (state.my - sm.my) * ease(2.4); sm.scroll += (state.scroll - sm.scroll) * ease(5);
    if (mode === 'hero') {
      const hw = state.halfW, por = state.portrait, U = river.material.uniforms, sc = sm.scroll;
      const gold = sstep(.06, .55, sc);
      gpu.userData.setGold(gold); U.uGold.value = gold * .85;
      if (por) { gpu.position.set(0, 2.25 + sc * .6, 0); gpu.scale.setScalar(.5); }
      else { gpu.position.set(hw * .36 + sm.mx * .3, 1.25 + Math.sin(t * .5) * .05 + sc * .25, 0); gpu.scale.setScalar(.84); }
      gpu.rotation.set(-1.02 + Math.sin(t * .35) * .03 + sm.my * .08 + sc * .25, -.28 + Math.sin(t * .22) * .05 + sm.mx * .12, .1);
      gpu.updateMatrixWorld(true);
      sinkOf(gpu, U.uS.value);
      if (por) { U.uL.value.set(-hw * 1.9, 3.6, -1.5); U.uR.value.set(hw * 1.9, 1.4, .5); U.uW0.value = .7; U.uW1.value = .45; }
      else { U.uL.value.set(-hw * 1.4, 1.4, -1.5); U.uR.value.set(hw * 1.35, 2.6, -1.2); U.uW0.value = .85 + sc * .5; U.uW1.value = .6; }
      camera.position.set(sm.mx * .6, -sm.my * .35, 11 - sc * .7); camera.lookAt(0, .55 + sc * .45, 0);
    } else {
      const k = state.step;
      // hand-off: the previous object fully leaves before the next one grows, so they never intersect
      const SIZE = { crystal: .9, chip: .74, gpu: .45, gpuGold: .45 };
      const othersOut = objects.every((o, i) => i === k || o.scale.x < .02);
      objects.forEach((o, i) => {
        const full = SIZE[o.userData.kind], target = i === k && othersOut ? full : .001;
        const s = o.scale.x + (target - o.scale.x) * ease(i === k ? 4.5 : 9), f = Math.min(1, s / full);
        o.scale.setScalar(Math.max(.001, s)); o.visible = s > .004;
        const kind = o.userData.kind, c = o.children[0];
        if (kind === 'crystal') c.rotation.set(.45 + Math.sin(t * .3) * .1 + (1 - f) * 1.5, t * .25 + (1 - f) * 3, .15);
        else (kind.startsWith('gpu') ? o : c).rotation.set((kind.startsWith('gpu') ? -.85 : -.55) + Math.sin(t * .3) * .06 + (1 - f) * 1.2, Math.sin(t * .25) * .4 + (1 - f) * 2, .1);
        o.position.y = Math.sin(t * .7) * .06;
      });
      orbit.material.uniforms.uGold.value += (k / 3 - orbit.material.uniforms.uGold.value) * ease(2);
      orbit.rotation.y = t * .02;
      camera.position.set(sm.mx * .5, .2 - sm.my * .3, 9.6); camera.lookAt(0, 0, 0);
    }
    renderer.render(scene, camera);
  }

  let raf = 0; const t0 = performance.now();
  const loop = () => { raf = requestAnimationFrame(loop); if (state.visible) frame(reduced ? 8 : (performance.now() - t0) / 1000); };
  if (mode === 'cover') frame(7 + state.cover * 2.3); else loop();
  if (mode !== 'cover' && 'IntersectionObserver' in window) new IntersectionObserver(([e]) => { state.visible = e.isIntersecting; }).observe(canvas);
  return { setScroll: v => { state.scroll = v; }, setStep: v => { state.step = v; }, renderer };
}
