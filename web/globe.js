// Interactive 3D globe: land dot-matrix, animated trade-route arcs, 3D cargo ships with wakes,
// value columns on hubs, real-time day/night terminator, chokepoint what-if zones and orbiting satellites.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export const RISK_COLORS = { LOW: '#2fe39a', MEDIUM: '#ffc845', HIGH: '#ff8a3d', CRITICAL: '#ff3d71', UNKNOWN: '#8898b8' };
export const STATUS_COLORS = { 'In Transit': '#38e1ff', Delayed: '#ff3d71', Pending: '#ffc845', Delivered: '#8898b8' };

/** Maritime chokepoints used by the what-if simulator. `radius` is the exclusion zone in degrees of arc. */
export const CHOKEPOINTS = [
  { id: 'suez', name: 'Suez Canal', lat: 30.0, lon: 32.55, radius: 5, via: ['Suez Canal'], note: '~12% of global trade' },
  { id: 'bab', name: 'Bab-el-Mandeb', lat: 12.6, lon: 43.4, radius: 5, via: ['Red Sea'], note: 'Red Sea gateway' },
  { id: 'hormuz', name: 'Strait of Hormuz', lat: 26.5, lon: 56.3, radius: 5, via: [], note: '~20% of oil flows' },
  { id: 'malacca', name: 'Strait of Malacca', lat: 2.5, lon: 101.0, radius: 6, via: ['Bay of Bengal'], note: 'Busiest strait by volume' },
  { id: 'taiwan', name: 'Taiwan Strait', lat: 24.0, lon: 119.5, radius: 5, via: [], note: 'East Asia feeder lanes' },
  { id: 'panama', name: 'Panama Canal', lat: 9.1, lon: -79.7, radius: 5, via: ['Gulf of Mexico'], note: 'Atlantic–Pacific link' },
  { id: 'cape', name: 'Cape of Good Hope', lat: -35.5, lon: 19.0, radius: 6, via: ['Cape of Good Hope'], note: 'Suez diversion route' },
  { id: 'channel', name: 'English Channel', lat: 50.4, lon: 0.6, radius: 4, via: [], note: 'North Europe approach' },
];

const D2R = Math.PI / 180;
const R = 1;

export function latLonToVec3(lat, lon, r = R) {
  const phi = (90 - lat) * D2R, th = (lon + 180) * D2R;
  return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(th), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(th));
}

/** Approximate sub-solar point for a date (ignores the equation of time — fine for a visual terminator). */
export function sunLatLon(date) {
  const start = Date.UTC(date.getUTCFullYear(), 0, 0);
  const doy = (date.getTime() - start) / 864e5;
  const decl = -23.44 * Math.cos((2 * Math.PI / 365) * (doy + 10));
  const hours = date.getUTCHours() + date.getUTCMinutes() / 60;
  const lon = ((12 - hours) * 15 + 540) % 360 - 180;
  return { lat: decl, lon };
}

function glowTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255,255,255,1)');
  grad.addColorStop(0.25, 'rgba(255,255,255,.55)');
  grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

function dotTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 32;
  const g = c.getContext('2d');
  g.fillStyle = '#fff'; g.beginPath(); g.arc(16, 16, 14, 0, Math.PI * 2); g.fill();
  return new THREE.CanvasTexture(c);
}

/** Smooth arc over the sphere through every waypoint, lifted by a single global altitude bump. */
function buildArcPoints(path) {
  const vs = path.map(([lat, lon]) => latLonToVec3(lat, lon));
  const segAngles = vs.slice(1).map((v, i) => vs[i].angleTo(v));
  const total = segAngles.reduce((a, b) => a + b, 0) || 1e-6;
  const H = Math.min(0.34, total * 0.13) + 0.025;
  const pts = [];
  let acc = 0;
  segAngles.forEach((ang, i) => {
    const n = Math.max(10, Math.ceil(ang * 48));
    for (let k = i === 0 ? 0 : 1; k <= n; k++) {
      const t = k / n;
      const v = new THREE.Vector3().copy(vs[i]).lerp(vs[i + 1], t).normalize();
      const T = (acc + ang * t) / total;
      pts.push(v.multiplyScalar(R + 0.004 + H * Math.sin(Math.PI * T)));
    }
    acc += ang;
  });
  return pts;
}

const arcVertex = /* glsl */`
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const arcFragment = /* glsl */`
  uniform vec3 uColor; uniform float uTime; uniform float uOffset; uniform float uDim;
  varying vec2 vUv;
  void main() {
    float d = fract(vUv.x * 2.0 - uTime * 0.22 + uOffset);
    float pulse = smoothstep(0.0, 0.12, d) * smoothstep(0.3, 0.12, d);
    float a = (0.22 + pulse * 0.95) * uDim;
    gl_FragColor = vec4(uColor * (0.75 + pulse * 0.9), a);
  }`;

const atmoVertex = /* glsl */`
  varying vec3 vNormal; varying vec3 vView;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vNormal = normalize(normalMatrix * normal); vView = normalize(-mv.xyz);
    gl_Position = projectionMatrix * mv;
  }`;
const atmoFragment = /* glsl */`
  uniform vec3 uColor; uniform float uPower; uniform float uStrength; uniform float uBack;
  varying vec3 vNormal; varying vec3 vView;
  void main() {
    float f = uBack > 0.5 ? pow(max(0.0, 0.72 - dot(vNormal, vView)), uPower)
                          : pow(1.0 - max(0.0, dot(vNormal, vView)), uPower);
    gl_FragColor = vec4(uColor, 1.0) * f * uStrength;
  }`;

// Night-side shading with a warm glow along the terminator.
const nightVertex = /* glsl */`
  varying vec3 vN;
  void main() { vN = normalize((modelMatrix * vec4(normal, 0.0)).xyz); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const nightFragment = /* glsl */`
  uniform vec3 uSun; varying vec3 vN;
  void main() {
    float d = dot(normalize(vN), uSun);
    float night = smoothstep(0.06, -0.2, d) * 0.5;
    float term = exp(-pow(d * 11.0, 2.0)) * 0.24;
    vec3 col = mix(vec3(0.0, 0.01, 0.035), vec3(1.0, 0.55, 0.25), term / (night + term + 1e-4));
    gl_FragColor = vec4(col, night + term);
  }`;

export function createGlobe(container, { onSelect, onHover, onAutoRotateChange } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.01, 100);
  const HOME = { lat: 28, lon: 40, dist: window.innerWidth < 820 ? 3.6 : 4.1 };
  camera.position.copy(latLonToVec3(HOME.lat, HOME.lon, HOME.dist));

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.dampingFactor = 0.06;
  controls.enablePan = false; controls.minDistance = 1.45; controls.maxDistance = 5.5;
  controls.rotateSpeed = 0.55; controls.zoomSpeed = 0.7;
  controls.autoRotate = true; controls.autoRotateSpeed = 0.35;

  scene.add(new THREE.AmbientLight(0x6688cc, 0.55));
  const sun = new THREE.DirectionalLight(0xbfd6ff, 1.1); sun.position.set(-3, 2, 4); scene.add(sun);

  // Starfield (two depths, slowly twinkling)
  const stars = [];
  for (const [n, size, op] of [[1600, 0.055, 0.5], [500, 0.11, 0.8]]) {
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const v = new THREE.Vector3().randomDirection().multiplyScalar(18 + Math.random() * 20);
      pos.set([v.x, v.y, v.z], i * 3);
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const p = new THREE.Points(g, new THREE.PointsMaterial({ color: 0x8fb4ff, size, transparent: true, opacity: op, depthWrite: false }));
    p.userData.base = op; scene.add(p); stars.push(p);
  }

  const world = new THREE.Group(); scene.add(world);

  // Ocean sphere + atmosphere
  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(R * 0.995, 96, 96),
    new THREE.MeshPhongMaterial({ color: 0x07142e, emissive: 0x030a1c, shininess: 18, specular: 0x1d3a7a }));
  world.add(earth);
  const rim = new THREE.Mesh(new THREE.SphereGeometry(R * 1.001, 96, 96), new THREE.ShaderMaterial({
    vertexShader: atmoVertex, fragmentShader: atmoFragment, transparent: true, depthWrite: false,
    blending: THREE.AdditiveBlending,
    uniforms: { uColor: { value: new THREE.Color('#3b7bff') }, uPower: { value: 3.2 }, uStrength: { value: 0.9 }, uBack: { value: 0 } } }));
  world.add(rim);
  const halo = new THREE.Mesh(new THREE.SphereGeometry(R * 1.16, 64, 64), new THREE.ShaderMaterial({
    vertexShader: atmoVertex, fragmentShader: atmoFragment, transparent: true, depthWrite: false,
    side: THREE.BackSide, blending: THREE.AdditiveBlending,
    uniforms: { uColor: { value: new THREE.Color('#2f8bff') }, uPower: { value: 4.0 }, uStrength: { value: 1.05 }, uBack: { value: 1 } } }));
  world.add(halo);

  // Graticule
  {
    const mat = new THREE.LineBasicMaterial({ color: 0x2a4a8a, transparent: true, opacity: 0.18 });
    for (let lat = -60; lat <= 60; lat += 30) {
      const pts = []; for (let lon = -180; lon <= 180; lon += 4) pts.push(latLonToVec3(lat, lon, R * 1.0005));
      world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
    }
    for (let lon = -180; lon < 180; lon += 30) {
      const pts = []; for (let lat = -90; lat <= 90; lat += 4) pts.push(latLonToVec3(lat, lon, R * 1.0005));
      world.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
    }
  }

  // Day / night overlay
  const sunDir = new THREE.Vector3();
  const nightMat = new THREE.ShaderMaterial({ vertexShader: nightVertex, fragmentShader: nightFragment,
    transparent: true, depthWrite: false, uniforms: { uSun: { value: sunDir } } });
  const night = new THREE.Mesh(new THREE.SphereGeometry(R * 1.0028, 96, 96), nightMat);
  night.renderOrder = 2;
  world.add(night);
  let timeOffsetDays = 0;
  function updateSun() {
    const s = sunLatLon(new Date(Date.now() + timeOffsetDays * 864e5));
    sunDir.copy(latLonToVec3(s.lat, s.lon, 1)).normalize();
    sun.position.copy(sunDir).multiplyScalar(5);
  }
  updateSun();

  const GLOW = glowTexture();
  // Data layers are rebuilt by setData(); static layers live for the lifetime of the globe.
  const layers = { routes: new THREE.Group(), shipments: new THREE.Group(), events: new THREE.Group(), hubs: new THREE.Group(), columns: new THREE.Group() };
  const staticLayers = { chokepoints: new THREE.Group(), satellites: new THREE.Group(), daynight: night };
  Object.values(layers).forEach(g => { g.renderOrder = 5; world.add(g); });
  staticLayers.chokepoints.renderOrder = 6; world.add(staticLayers.chokepoints);
  scene.add(staticLayers.satellites);

  // Selection marker
  const marker = new THREE.Mesh(new THREE.RingGeometry(0.035, 0.042, 48),
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9, side: THREE.DoubleSide, depthWrite: false }));
  marker.visible = false; marker.renderOrder = 7; world.add(marker);
  let markerTarget = null;

  const routeCurves = new Map();
  const arcs = new Map();          // routeId -> { mat, data }
  const shipmentObjs = new Map();  // shipmentId -> ship group
  const pickables = [];
  const eventRings = [];
  const columns = [];
  let riskById = {};
  let affectedRoutes = new Set();
  let focusRouteId = null;

  // ── Satellites (decorative) ──
  const satellites = [];
  {
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xdfe8ff, metalness: 0.8, roughness: 0.3, emissive: 0x223355 });
    const panelMat = new THREE.MeshStandardMaterial({ color: 0x2a5cff, metalness: 0.4, roughness: 0.4, emissive: 0x0d2a88, side: THREE.DoubleSide });
    [[1.42, 52, 0.16, 0], [1.6, -28, 0.11, 2.1], [1.3, 97, 0.2, 4.2]].forEach(([r, incl, speed, phase]) => {
      const pivot = new THREE.Group();
      pivot.rotation.set(incl * D2R, phase, 0.3 * phase);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(r, 0.0012, 4, 180),
        new THREE.MeshBasicMaterial({ color: 0x38e1ff, transparent: true, opacity: 0.12, depthWrite: false }));
      ring.rotation.x = Math.PI / 2; pivot.add(ring);
      const sat = new THREE.Group();
      const body = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.018, 0.026), bodyMat);
      const pL = new THREE.Mesh(new THREE.PlaneGeometry(0.05, 0.016), panelMat); pL.position.x = -0.036;
      const pR = pL.clone(); pR.position.x = 0.036;
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: 0x9fdcff, transparent: true, opacity: 0.6, depthWrite: false, blending: THREE.AdditiveBlending }));
      glow.scale.setScalar(0.07);
      sat.add(body, pL, pR, glow);
      pivot.add(sat);
      staticLayers.satellites.add(pivot);
      satellites.push({ sat, r, speed, phase });
    });
  }

  // ── Chokepoints ──
  const chokeObjs = new Map();
  CHOKEPOINTS.forEach(cp => {
    const n = latLonToVec3(cp.lat, cp.lon, 1).normalize();
    const grp = new THREE.Group();
    grp.position.copy(n.clone().multiplyScalar(R * 1.003));
    grp.lookAt(n.clone().multiplyScalar(2));
    const color = new THREE.Color('#ffd76b');
    const zoneR = Math.tan(cp.radius * D2R);
    const zone = new THREE.Mesh(new THREE.CircleGeometry(zoneR, 48),
      new THREE.MeshBasicMaterial({ color: RISK_COLORS.CRITICAL, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false }));
    const ring = new THREE.Mesh(new THREE.RingGeometry(0.018, 0.022, 4),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85, side: THREE.DoubleSide, depthWrite: false }));
    ring.rotation.z = Math.PI / 4;
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.0012, 0.0012, 0.04, 6),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.6 }));
    stem.rotation.x = Math.PI / 2; stem.position.z = 0.02;
    const gem = new THREE.Mesh(new THREE.OctahedronGeometry(0.011),
      new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.6, metalness: 0.5, roughness: 0.25 }));
    gem.position.z = 0.046;
    gem.userData = { kind: 'chokepoint', data: cp };
    grp.add(zone, ring, stem, gem);
    staticLayers.chokepoints.add(grp);
    pickables.push(gem);
    chokeObjs.set(cp.id, { grp, zone, ring, stem, gem, closed: false, normal: n });
  });

  async function loadLand() {
    try {
      const [{ geoPath, geoEquirectangular }, topojson] = await Promise.all([import('d3-geo'), import('topojson-client')]);
      const res = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-110m.json');
      const topo = await res.json();
      const land = topojson.feature(topo, topo.objects.land);
      const W = 1440, H = 720;
      const c = document.createElement('canvas'); c.width = W; c.height = H;
      const g = c.getContext('2d', { willReadFrequently: true });
      const proj = geoEquirectangular().scale(W / (2 * Math.PI)).translate([W / 2, H / 2]);
      g.fillStyle = '#fff'; g.beginPath(); geoPath(proj, g)(land); g.fill();
      const px = g.getImageData(0, 0, W, H).data;
      const positions = [], colors = [];
      const step = 0.62;
      const cA = new THREE.Color('#2a63ff'), cB = new THREE.Color('#5fe3ff');
      for (let lat = -84; lat <= 84; lat += step) {
        const ring = Math.max(1, Math.floor(Math.cos(lat * D2R) * 360 / step));
        for (let i = 0; i < ring; i++) {
          const lon = -180 + (i / ring) * 360;
          const x = Math.floor((lon + 180) / 360 * W), y = Math.floor((90 - lat) / 180 * H);
          if (px[(y * W + x) * 4 + 3] > 128) {
            const v = latLonToVec3(lat, lon, R * 1.002);
            positions.push(v.x, v.y, v.z);
            const col = cA.clone().lerp(cB, (lat + 84) / 168 * 0.7 + Math.random() * 0.3);
            colors.push(col.r, col.g, col.b);
          }
        }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      const pts = new THREE.Points(geo, new THREE.PointsMaterial({
        size: 0.0105, map: dotTexture(), vertexColors: true, transparent: true, alphaTest: 0.3, opacity: 0.95, depthWrite: false }));
      pts.renderOrder = 1;
      world.add(pts);
    } catch (e) {
      console.warn('Land data unavailable; rendering ocean-only globe.', e);
    }
  }

  function clearLayer(g) {
    while (g.children.length) {
      const o = g.children.pop();
      o.traverse?.(n => { n.geometry?.dispose?.(); if (n.material && n.material !== marker.material) n.material.dispose?.(); });
    }
  }

  // A small container ship: hull (nose along +Z), stacked containers and a bridge; up is +Y.
  const HULL_GEO = (() => {
    const shape = new THREE.Shape();
    shape.moveTo(-0.006, -0.013); shape.lineTo(0.006, -0.013); shape.lineTo(0.006, 0.006);
    shape.quadraticCurveTo(0.006, 0.012, 0, 0.017); shape.quadraticCurveTo(-0.006, 0.012, -0.006, 0.006); shape.closePath();
    const g = new THREE.ExtrudeGeometry(shape, { depth: 0.004, bevelEnabled: false });
    g.rotateX(-Math.PI / 2); // shape Y -> -Z ... flip so nose is +Z
    g.rotateY(Math.PI);
    return g;
  })();
  const BOX_GEO = new THREE.BoxGeometry(0.0095, 0.0035, 0.016);
  const BRIDGE_GEO = new THREE.BoxGeometry(0.008, 0.006, 0.004);
  const WAKE_N = 14;

  function makeShip(s, i, route) {
    const color = new THREE.Color(STATUS_COLORS[s.status] || '#38e1ff');
    const ship = new THREE.Group();
    const hullMat = new THREE.MeshStandardMaterial({ color: 0x1b2a4a, metalness: 0.5, roughness: 0.4, emissive: color, emissiveIntensity: 0.35 });
    const cargoMat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.7, metalness: 0.2, roughness: 0.5 });
    const hull = new THREE.Mesh(HULL_GEO, hullMat);
    const cargo = new THREE.Mesh(BOX_GEO, cargoMat); cargo.position.set(0, 0.0055, 0.001);
    const bridge = new THREE.Mesh(BRIDGE_GEO, hullMat); bridge.position.set(0, 0.0065, -0.0105);
    const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color, transparent: true, opacity: 0.75, depthWrite: false, blending: THREE.AdditiveBlending }));
    glow.scale.setScalar(0.07);
    ship.add(hull, cargo, bridge, glow);
    ship.scale.setScalar(1.5);

    // Wake trail behind the ship
    const wakeGeo = new THREE.BufferGeometry();
    wakeGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(WAKE_N * 3), 3));
    wakeGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(WAKE_N * 3), 3));
    const wake = new THREE.Line(wakeGeo, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    wake.frustumCulled = false;

    const ud = { kind: 'shipment', data: s, curve: routeCurves.get(s.route_id), base: s.progress ?? 0.5, phase: i * 1.7,
      glow, cargoMat, hullMat, wake, transitDays: route?.transit_days || 14, arrived: false };
    ship.userData = ud; hull.userData = ud; cargo.userData = ud;
    tintShip(ship, color);
    return ship;
  }

  function tintShip(ship, color) {
    const u = ship.userData;
    u.cargoMat.color.copy(color); u.cargoMat.emissive.copy(color);
    u.hullMat.emissive.copy(color);
    u.glow.material.color.copy(color);
    const col = u.wake.geometry.attributes.color;
    for (let k = 0; k < WAKE_N; k++) {
      const f = Math.pow(1 - k / WAKE_N, 1.6) * 0.9;
      col.setXYZ(k, color.r * f, color.g * f, color.b * f);
    }
    col.needsUpdate = true;
  }

  function setData(net) {
    Object.values(layers).forEach(clearLayer);
    routeCurves.clear(); arcs.clear(); shipmentObjs.clear(); eventRings.length = 0; columns.length = 0;
    for (let i = pickables.length - 1; i >= 0; i--) if (pickables[i].userData.kind !== 'chokepoint') pickables.splice(i, 1);
    const routeById = new Map(net.routes.map(r => [r.id, r]));

    // Routes
    net.routes.forEach((r, i) => {
      const pts = buildArcPoints(r.path);
      const curve = new THREE.CatmullRomCurve3(pts);
      routeCurves.set(r.id, curve);
      const mat = new THREE.ShaderMaterial({
        vertexShader: arcVertex, fragmentShader: arcFragment, transparent: true, depthWrite: false,
        blending: THREE.AdditiveBlending,
        uniforms: { uColor: { value: new THREE.Color(RISK_COLORS[r.risk_level] || '#38e1ff') },
          uTime: { value: 0 }, uOffset: { value: i * 0.137 }, uDim: { value: 1 } } });
      const radius = r.risk_level === 'CRITICAL' ? 0.0042 : 0.003;
      const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.min(400, pts.length * 2), radius, 6, false), mat);
      tube.userData = { kind: 'route', data: r };
      layers.routes.add(tube);
      arcs.set(r.id, { mat, data: r, samples: curve.getSpacedPoints(120).map(p => p.clone().normalize()) });
    });

    // Hubs + value columns
    const hubValue = new Map();
    net.shipments.filter(s => s.status !== 'Delivered').forEach(s => {
      hubValue.set(s.origin, (hubValue.get(s.origin) || 0) + s.value_usd);
      hubValue.set(s.destination, (hubValue.get(s.destination) || 0) + s.value_usd);
    });
    const maxValue = Math.max(1, ...hubValue.values());
    const cLow = new THREE.Color('#38e1ff'), cHigh = new THREE.Color('#a66bff');
    net.hubs.forEach((h, i) => {
      const p = latLonToVec3(h.lat, h.lon, R * 1.003);
      const up = p.clone().normalize();
      const dot = new THREE.Mesh(new THREE.SphereGeometry(0.0085, 12, 12), new THREE.MeshBasicMaterial({ color: 0xdff6ff }));
      dot.position.copy(p);
      const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.0015, 0.0015, 0.06, 6),
        new THREE.MeshBasicMaterial({ color: 0x38e1ff, transparent: true, opacity: 0.55 }));
      beam.position.copy(latLonToVec3(h.lat, h.lon, R * 1.033));
      beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), up);
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color: 0x38e1ff, transparent: true, opacity: 0.6, depthWrite: false, blending: THREE.AdditiveBlending }));
      glow.scale.setScalar(0.06); glow.position.copy(p);
      dot.userData = { kind: 'hub', data: h };
      layers.hubs.add(dot, beam, glow); pickables.push(dot);

      const v = hubValue.get(h.name) || 0;
      if (v > 0) {
        const k = Math.sqrt(v / maxValue);
        const color = cLow.clone().lerp(cHigh, k);
        const geo = new THREE.CylinderGeometry(0.011, 0.014, 1, 6); geo.translate(0, 0.5, 0);
        const col = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.55,
          transparent: true, opacity: 0.82, metalness: 0.3, roughness: 0.35 }));
        col.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 })));
        col.position.copy(p);
        col.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), up);
        col.scale.set(1, 0.0001, 1);
        col.userData = { kind: 'hub', data: { ...h, value_usd: v }, h: 0.025 + k * 0.15, delay: 0.4 + i * 0.05, born: null };
        layers.columns.add(col); columns.push(col); pickables.push(col);
      }
    });

    // Shipments
    net.shipments.forEach((s, i) => {
      if (!routeCurves.get(s.route_id)) return;
      const ship = makeShip(s, i, routeById.get(s.route_id));
      layers.shipments.add(ship, ship.userData.wake);
      ship.children.slice(0, 2).forEach(c => pickables.push(c));
      shipmentObjs.set(s.id, ship);
    });

    // Geo events
    net.events.forEach(ev => {
      const color = new THREE.Color(RISK_COLORS[ev.severity] || '#ffc845');
      const n = latLonToVec3(ev.lat, ev.lon, 1).normalize();
      const grp = new THREE.Group();
      grp.position.copy(n.clone().multiplyScalar(R * 1.004));
      grp.lookAt(n.clone().multiplyScalar(2));
      for (let k = 0; k < 2; k++) {
        const ring = new THREE.Mesh(new THREE.RingGeometry(0.03, 0.036, 48),
          new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.8, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending }));
        ring.userData.phase = k * 0.5;
        grp.add(ring); eventRings.push(ring);
      }
      const core = new THREE.Mesh(new THREE.CircleGeometry(0.014, 24),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95, side: THREE.DoubleSide, depthWrite: false }));
      core.userData = { kind: 'event', data: ev };
      grp.add(core); pickables.push(core);
      layers.events.add(grp);
    });
    applyArcState();
  }

  /** Recompute route and ship colours from risk scan, closures and focus. */
  function applyArcState() {
    const closures = affectedRoutes.size > 0;
    arcs.forEach(({ mat, data }, id) => {
      const hit = affectedRoutes.has(id);
      mat.uniforms.uColor.value.set(hit ? RISK_COLORS.CRITICAL : (RISK_COLORS[data.risk_level] || '#38e1ff'));
      mat.uniforms.uDim.value = focusRouteId ? (id === focusRouteId ? 1.7 : 0.22) : closures ? (hit ? 1.6 : 0.28) : 1;
    });
    shipmentObjs.forEach((ship, id) => {
      const u = ship.userData;
      const hit = affectedRoutes.has(u.data.route_id);
      const label = hit ? 'CRITICAL' : riskById[id];
      const c = new THREE.Color(label ? RISK_COLORS[label] : (STATUS_COLORS[u.data.status] || '#38e1ff'));
      tintShip(ship, c);
      u.glow.scale.setScalar(label === 'CRITICAL' ? 0.12 : label === 'HIGH' ? 0.095 : 0.07);
    });
  }

  function setShipmentRisk(map) { riskById = map || {}; applyArcState(); }

  /** Close (or reopen) chokepoints; returns the ids of the routes that pass through any closed one. */
  function setClosures(ids) {
    const closed = new Set(ids);
    chokeObjs.forEach((o, id) => {
      o.closed = closed.has(id);
      const c = new THREE.Color(o.closed ? RISK_COLORS.CRITICAL : '#ffd76b');
      o.gem.material.color.copy(c); o.gem.material.emissive.copy(c);
      o.ring.material.color.copy(c); o.stem.material.color.copy(c);
    });
    affectedRoutes = new Set();
    arcs.forEach(({ data, samples }, rid) => {
      for (const cp of CHOKEPOINTS) {
        if (!closed.has(cp.id)) continue;
        const via = (data.via_ports || []).map(v => String(v).trim());
        const n = chokeObjs.get(cp.id).normal;
        if (cp.via.some(v => via.includes(v)) || samples.some(p => p.angleTo(n) < cp.radius * D2R)) { affectedRoutes.add(rid); break; }
      }
    });
    applyArcState();
    return [...affectedRoutes];
  }

  function setTimeOffset(days) { timeOffsetDays = days; updateSun(); }

  // ── Camera flights ──
  let flight = null;
  function flyTo(lat, lon, dist) {
    const from = camera.position.clone();
    const d = dist ?? Math.min(from.length(), 3.0);
    const to = latLonToVec3(lat, lon, 1).normalize().multiplyScalar(d);
    flight = { from, to, t: 0 };
    setAutoRotate(false);
  }
  function setAutoRotate(on) {
    controls.autoRotate = on; onAutoRotateChange?.(on);
  }
  function vecToLatLon(v) {
    const p = v.clone().normalize();
    return { lat: 90 - Math.acos(p.y) / D2R, lon: ((Math.atan2(p.z, -p.x) / D2R) - 180 + 540) % 360 - 180 };
  }
  function focusShipment(id, dist = 2.6) {
    const m = shipmentObjs.get(id); if (!m) return;
    const { lat, lon } = vecToLatLon(m.position);
    flyTo(lat, lon, dist);
    select(m);
  }
  function zoomBy(f) {
    const d = THREE.MathUtils.clamp(camera.position.length() * f, controls.minDistance, controls.maxDistance);
    const { lat, lon } = vecToLatLon(camera.position);
    const ar = controls.autoRotate;
    flyTo(lat, lon, d);
    if (ar) setAutoRotate(true);
  }
  function resetView() { flyTo(HOME.lat, HOME.lon, HOME.dist); select(null); setAutoRotate(true); }

  function select(obj) {
    markerTarget = obj;
    marker.visible = !!obj;
    const ud = obj?.userData;
    focusRouteId = ud?.kind === 'shipment' ? ud.data.route_id : null;
    applyArcState();
    onSelect?.(ud || null);
  }

  // ── Picking ──
  const ray = new THREE.Raycaster(); ray.params.Points = { threshold: 0 };
  const ndc = new THREE.Vector2();
  let down = null, hovered = null;
  function isVisible(o) {
    for (let n = o; n; n = n.parent) if (n.visible === false) return false;
    return true;
  }
  function pick(ev) {
    const rect = renderer.domElement.getBoundingClientRect();
    ndc.set(((ev.clientX - rect.left) / rect.width) * 2 - 1, -((ev.clientY - rect.top) / rect.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const visible = pickables.filter(isVisible);
    const hits = ray.intersectObjects([earth, ...visible], false);
    // also test enlarged spheres for tiny targets
    if (!hits.length || hits[0].object === earth) {
      const earthHit = hits.find(h => h.object === earth);
      let best = null, bestD = 0.035;
      visible.forEach(o => {
        const wp = o.getWorldPosition(new THREE.Vector3());
        if (earthHit && wp.distanceTo(camera.position) > earthHit.distance + 0.02) return;
        const d = ray.ray.distanceToPoint(wp) / (wp.distanceTo(camera.position) / 2.5);
        if (d < bestD) { bestD = d; best = o; }
      });
      return best;
    }
    return hits[0].object;
  }
  // Ship parts share userData with the ship group; resolve to the group so the marker tracks it.
  const resolve = o => (o?.userData.kind === 'shipment' ? shipmentObjs.get(o.userData.data.id) : o);
  renderer.domElement.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (down && Math.hypot(e.clientX - down.x, e.clientY - down.y) < 5) {
      const o = resolve(pick(e));
      select(o);
      if (o) setAutoRotate(false);
    }
    down = null;
  });
  renderer.domElement.addEventListener('pointermove', e => {
    if (e.buttons) { onHover?.(null, e); return; }
    const o = pick(e);
    if (o !== hovered) { hovered = o; renderer.domElement.style.cursor = o ? 'pointer' : ''; }
    onHover?.(o ? o.userData : null, e);
  });
  renderer.domElement.addEventListener('pointerleave', e => onHover?.(null, e));
  controls.addEventListener('start', () => { flight = null; });

  // ── Resize & loop ──
  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h, false);
    renderer.domElement.style.width = w + 'px'; renderer.domElement.style.height = h + 'px';
    camera.aspect = w / h;
    // shift the globe left on wide screens so right-hand panels don't cover it
    camera.setViewOffset(w, h, w > 1100 && document.body.dataset.view !== 'command' ? w * 0.17 : 0, 0, w, h);
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  const clock = new THREE.Clock();
  const tmp = new THREE.Vector3(), tan = new THREE.Vector3(), look = new THREE.Vector3(), wp = new THREE.Vector3();
  let sunTick = 0;
  function frame() {
    requestAnimationFrame(frame);
    if (document.hidden) return;
    const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime;

    if (flight) {
      flight.t = Math.min(1, flight.t + dt / 1.3);
      const e = 1 - Math.pow(1 - flight.t, 3);
      const dir = flight.from.clone().normalize().lerp(flight.to.clone().normalize(), e).normalize();
      camera.position.copy(dir.multiplyScalar(THREE.MathUtils.lerp(flight.from.length(), flight.to.length(), e)));
      if (flight.t >= 1) flight = null;
    }
    controls.update();

    if ((sunTick += dt) > 30) { sunTick = 0; updateSun(); }
    stars.forEach((s, i) => { s.material.opacity = s.userData.base * (0.8 + 0.2 * Math.sin(t * (0.6 + i * 0.5))); });

    arcs.forEach(({ mat }) => { mat.uniforms.uTime.value = t; });
    shipmentObjs.forEach(ship => {
      const u = ship.userData;
      const raw = u.base + timeOffsetDays / u.transitDays;
      u.arrived = timeOffsetDays > 0 && raw >= 1 && u.data.status !== 'Pending';
      ship.visible = u.wake.visible = !u.arrived && layers.shipments.visible;
      if (u.arrived) return;
      const p = Math.min(0.995, Math.max(0.005, raw + 0.004 * Math.sin(t * 0.25 + u.phase)));
      u.curve.getPointAt(p, ship.position);
      u.curve.getTangentAt(p, tan);
      ship.up.copy(ship.position).normalize();
      ship.lookAt(look.copy(ship.position).add(tan));
      u.glow.material.opacity = 0.55 + 0.25 * Math.sin(t * 3 + u.phase);
      const pos = u.wake.geometry.attributes.position;
      for (let k = 0; k < WAKE_N; k++) {
        u.curve.getPointAt(Math.max(0, p - k * 0.0045), wp);
        pos.setXYZ(k, wp.x, wp.y, wp.z);
      }
      pos.needsUpdate = true;
    });
    columns.forEach(c => {
      const u = c.userData;
      const k = Math.min(1, Math.max(0, (t - u.delay) / 1.1));
      c.scale.y = Math.max(0.0001, u.h * (1 - Math.pow(1 - k, 3)));
    });
    eventRings.forEach(r => {
      const k = ((t * 0.55 + r.userData.phase) % 1);
      r.scale.setScalar(0.6 + k * 2.2); r.material.opacity = 0.85 * (1 - k);
    });
    chokeObjs.forEach(o => {
      o.gem.rotation.z = t * 1.4; o.gem.rotation.x = t * 0.7;
      o.gem.position.z = 0.046 + 0.004 * Math.sin(t * 2);
      if (o.closed) {
        const k = (t * 0.8) % 1;
        o.zone.material.opacity = 0.16 + 0.12 * Math.sin(t * 3);
        o.ring.scale.setScalar(1 + k * 3); o.ring.material.opacity = 0.9 * (1 - k);
      } else {
        o.zone.material.opacity = 0; o.ring.scale.setScalar(1); o.ring.material.opacity = 0.85;
      }
    });
    satellites.forEach(s => {
      const a = t * s.speed + s.phase;
      s.sat.position.set(Math.cos(a) * s.r, 0, Math.sin(a) * s.r);
      s.sat.lookAt(0, 0, 0);
      s.sat.rotateZ(t * 0.2);
    });
    if (markerTarget) {
      markerTarget.getWorldPosition(tmp);
      marker.position.copy(tmp);
      marker.lookAt(camera.position);
      marker.scale.setScalar(1 + 0.15 * Math.sin(t * 4));
      marker.visible = markerTarget.visible !== false;
    }
    renderer.render(scene, camera);
  }
  frame();
  const landReady = loadLand();

  return {
    landReady, setData, setShipmentRisk, setClosures, setTimeOffset, flyTo, focusShipment, setAutoRotate, resize,
    zoomBy, resetView,
    isAutoRotating: () => controls.autoRotate,
    setLayer(name, on) {
      const l = layers[name] || staticLayers[name];
      if (l) l.visible = on;
      if (name === 'routes') layers.hubs.visible = on;
    },
    selectChokepoint(id) { const o = chokeObjs.get(id); if (o) select(o.gem); },
    clearSelection() { select(null); },
    snapshot() { return renderer.domElement.toDataURL('image/png'); },
  };
}
