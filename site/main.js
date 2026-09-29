// Website behaviour: Three.js block-chain in the hero, anime.js for motion.
// Everything degrades gracefully: without WebGL the canvas stays empty, and
// without anime.js the content is simply shown without animation.
window.__ready = true;

const anime = window.anime;
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

// ------------------------------------------------------------ hero intro --
function intro() {
  if (!anime || reduced) return;
  anime.timeline({ easing: "easeOutExpo" })
    .add({ targets: ".hero .eyebrow", opacity: [0, 1], translateY: [12, 0], duration: 600 })
    .add({
      targets: ".hero-name .ch",
      translateY: ["105%", 0], rotate: [8, 0], opacity: [0, 1],
      duration: 1100, delay: anime.stagger(45),
    }, "-=300")
    .add({
      targets: [".hero-full", ".hero-tagline", ".hero-cta", ".stats"],
      opacity: [0, 1], translateY: [18, 0], duration: 800, delay: anime.stagger(90),
    }, "-=800")
    .add({ targets: ".hero-3d", opacity: [0, 1], scale: [0.92, 1], duration: 1200 }, 200);
}

// Typewriter over the research taglines.
function rotator() {
  const el = $(".rotator");
  if (!el || reduced) return;
  const words = JSON.parse(el.dataset.words);
  let i = 0;
  const type = (word, n = 0) => {
    el.textContent = word.slice(0, n);
    if (n < word.length) setTimeout(() => type(word, n + 1), 45);
    else setTimeout(erase, 2400);
  };
  const erase = () => {
    const t = el.textContent;
    if (t.length) { el.textContent = t.slice(0, -1); setTimeout(erase, 22); }
    else { i = (i + 1) % words.length; type(words[i]); }
  };
  setTimeout(erase, 2600);
}

// Count up the hero stats the first time they are seen.
function counters() {
  const els = $$(".count");
  if (!anime || reduced || !els.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ isIntersecting, target }) => {
      if (!isIntersecting) return;
      io.unobserve(target);
      const o = { v: 0 };
      anime({
        targets: o, v: +target.dataset.to, round: 1, duration: 1600, easing: "easeOutCubic",
        delay: 500, update: () => (target.textContent = o.v),
      });
    });
  });
  els.forEach((el) => io.observe(el));
}

// ---------------------------------------------------------------- quotes --
function quotes() {
  const figs = $$(".quote");
  const dots = $$(".quote-dots button");
  if (figs.length < 2) return;
  // Split into words once so each change can stagger them in.
  figs.forEach((f) => {
    const q = $("blockquote", f);
    q.innerHTML = q.textContent.split(" ").map((w) => `<span class="w">${w}</span>`).join(" ");
  });
  let cur = 0, timer;
  const show = (n) => {
    figs[cur].classList.remove("is-on"); dots[cur].classList.remove("is-on");
    cur = (n + figs.length) % figs.length;
    figs[cur].classList.add("is-on"); dots[cur].classList.add("is-on");
    if (anime && !reduced) {
      anime({
        targets: $$(".w", figs[cur]), opacity: [0, 1], translateY: [18, 0], filter: ["blur(4px)", "blur(0px)"],
        duration: 700, delay: anime.stagger(35), easing: "easeOutQuad",
      });
      anime({ targets: ".quote-mark", rotate: [-14, 0], scale: [0.8, 1], duration: 900, easing: "easeOutElastic(1, .6)" });
    }
  };
  const start = () => { if (!reduced) timer = setInterval(() => show(cur + 1), 7000); };
  const stop = () => clearInterval(timer);
  dots.forEach((d) => d.addEventListener("click", () => { stop(); show(+d.dataset.i); start(); }));
  const box = $(".quotes");
  box.addEventListener("mouseenter", stop);
  box.addEventListener("mouseleave", start);
  start();
}

// ------------------------------------------------------ scroll reveals ---
function reveals() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ isIntersecting, target }) => {
      if (!isIntersecting) return;
      // Stagger siblings that enter together.
      const sibs = $$(":scope > .reveal", target.parentElement);
      target.style.transitionDelay = `${Math.min(sibs.indexOf(target), 6) * 70}ms`;
      target.classList.add("is-in");
      io.unobserve(target);
    });
  }, { rootMargin: "0px 0px -8% 0px" });
  $$(".reveal").forEach((el) => io.observe(el));
}

// Highlight the nav link of the section on screen.
function navSpy() {
  const links = new Map($$(".nav nav a").map((a) => [a.getAttribute("href").slice(1), a]));
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ isIntersecting, target }) => {
      if (isIntersecting) links.forEach((a, id) => a.classList.toggle("is-active", id === target.id));
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  links.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
}

// ------------------------------------------------------ publication filter --
function filters() {
  const chips = $$(".chip");
  const pubs = $$(".pub");
  chips.forEach((chip) => chip.addEventListener("click", () => {
    const f = chip.dataset.filter;
    chips.forEach((c) => c.classList.toggle("is-on", c === chip));
    const shown = [];
    pubs.forEach((p) => {
      const on = f === "all" || p.dataset.kind === f;
      p.hidden = !on;
      if (on) { p.classList.add("is-in"); shown.push(p); }
    });
    if (anime && !reduced) {
      anime({
        targets: shown, opacity: [0, 1], translateY: [16, 0],
        duration: 550, delay: anime.stagger(60), easing: "easeOutCubic",
      });
    }
  }));
}

// -------------------------------------------------------- 3D block-chain --
async function chain() {
  const canvas = $("#chain");
  if (!canvas) return;
  let THREE;
  try { THREE = await import("three"); } catch { return; }

  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); } catch { return; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 1.6, 11.5);
  camera.lookAt(0, 0, 0);

  scene.add(new THREE.HemisphereLight(0xffffff, 0xd8cfbd, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(4, 8, 6);
  scene.add(sun);

  const ink = new THREE.Color(css("--ink"));
  const palette = ["--yellow", "--blue", "--red", "--lime", "--pink", "--orange", "--teal", "--violet"]
    .map((v) => new THREE.Color(css(v)));

  const world = new THREE.Group();
  scene.add(world);

  // Thick cartoon outline: an inflated back-face copy drawn in ink.
  const outlineMat = new THREE.MeshBasicMaterial({ color: ink, side: THREE.BackSide });
  const outlined = (geo, mat, k = 1.08) => {
    const g = new THREE.Group();
    g.add(new THREE.Mesh(geo, mat));
    const o = new THREE.Mesh(geo, outlineMat);
    o.scale.setScalar(k);
    g.add(o);
    return g;
  };

  // The chain: blocks on a tilted, wavy ring, each linked to the next.
  const N = 10, R = 3.4;
  const boxGeo = new THREE.BoxGeometry(1, 1, 1);
  const blocks = [];
  const points = [];
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2;
    const p = new THREE.Vector3(Math.cos(a) * R, Math.sin(a * 2) * 0.55, Math.sin(a) * R);
    points.push(p);
    const mat = new THREE.MeshToonMaterial({ color: palette[i % palette.length] });
    const b = outlined(boxGeo, mat, 1.1);
    b.position.copy(p);
    b.rotation.set(Math.random() * 3, Math.random() * 3, 0);
    b.userData.spin = new THREE.Vector3(0.2 + Math.random() * 0.3, 0.25 + Math.random() * 0.3, 0);
    blocks.push(b);
    world.add(b);
    // Crisp ink edges on top of the outline.
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(boxGeo), new THREE.LineBasicMaterial({ color: ink }));
    b.add(edges);
  }

  // Links (short ink cylinders between neighbouring blocks).
  const linkMat = new THREE.MeshBasicMaterial({ color: ink });
  const up = new THREE.Vector3(0, 1, 0);
  for (let i = 0; i < N; i++) {
    const a = points[i], b = points[(i + 1) % N];
    const len = a.distanceTo(b);
    const link = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, len, 8), linkMat);
    link.position.copy(a).add(b).multiplyScalar(0.5);
    link.quaternion.setFromUnitVectors(up, b.clone().sub(a).normalize());
    world.add(link);
  }

  // The shared state in the middle: a slowly turning wireframe polyhedron.
  const core = new THREE.Group();
  const coreGeo = new THREE.IcosahedronGeometry(1.35, 0);
  core.add(outlined(coreGeo, new THREE.MeshToonMaterial({ color: new THREE.Color(css("--paper")) }), 1.06));
  core.add(new THREE.LineSegments(new THREE.EdgesGeometry(coreGeo), new THREE.LineBasicMaterial({ color: ink })));
  const inner = new THREE.Mesh(new THREE.OctahedronGeometry(0.55), new THREE.MeshToonMaterial({ color: palette[0] }));
  core.add(inner);
  world.add(core);

  // Faint spokes from each block to the core (verification paths).
  const spokeGeo = new THREE.BufferGeometry().setFromPoints(points.flatMap((p) => [new THREE.Vector3(), p]));
  const spokes = new THREE.LineSegments(spokeGeo, new THREE.LineDashedMaterial({ color: ink, dashSize: 0.14, gapSize: 0.12, transparent: true, opacity: 0.35 }));
  spokes.computeLineDistances();
  world.add(spokes);

  // Packets travelling along the chain.
  const packetGeo = new THREE.SphereGeometry(0.15, 16, 12);
  const packets = Array.from({ length: 4 }, (_, k) => {
    const m = outlined(packetGeo, new THREE.MeshToonMaterial({ color: palette[(k * 3 + 2) % palette.length] }), 1.3);
    m.userData.t = k * (N / 4);
    world.add(m);
    return m;
  });

  // Floating peer nodes around the ring.
  const peerGeo = new THREE.SphereGeometry(0.07, 8, 6);
  const peerMat = new THREE.MeshBasicMaterial({ color: ink });
  for (let i = 0; i < 40; i++) {
    const m = new THREE.Mesh(peerGeo, peerMat);
    const r = 4.6 + Math.random() * 1.6, a = Math.random() * Math.PI * 2;
    m.position.set(Math.cos(a) * r, (Math.random() - 0.5) * 4.5, Math.sin(a) * r);
    world.add(m);
  }

  // ---- interaction: drag to rotate (with inertia), hover to tilt, scroll to turn.
  let yaw = 0.4, pitch = 0.32, vYaw = reduced ? 0 : 0.0025, vPitch = 0;
  let dragging = false, lastX = 0, lastY = 0, hoverX = 0, hoverY = 0;
  canvas.addEventListener("pointerdown", (ev) => {
    dragging = true; lastX = ev.clientX; lastY = ev.clientY;
    canvas.setPointerCapture(ev.pointerId);
  });
  canvas.addEventListener("pointermove", (ev) => {
    const r = canvas.getBoundingClientRect();
    hoverX = ((ev.clientX - r.left) / r.width - 0.5) * 2;
    hoverY = ((ev.clientY - r.top) / r.height - 0.5) * 2;
    if (!dragging) return;
    vYaw = (ev.clientX - lastX) * 0.006;
    vPitch = (ev.clientY - lastY) * 0.004;
    yaw += vYaw; pitch += vPitch;
    lastX = ev.clientX; lastY = ev.clientY;
  });
  const release = () => { dragging = false; };
  canvas.addEventListener("pointerup", release);
  canvas.addEventListener("pointercancel", release);
  canvas.addEventListener("pointerleave", () => { hoverX = hoverY = 0; });

  const resize = () => {
    const { width, height } = canvas.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.fov = width / height < 1.1 ? 44 : 38;
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(canvas);
  resize();

  let visible = true;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(canvas);

  const clock = new THREE.Clock();
  const tmp = new THREE.Vector3();
  const loop = () => {
    requestAnimationFrame(loop);
    if (!visible) return;
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;

    if (!dragging) {
      // Ease back towards a gentle idle spin.
      vYaw += ((reduced ? 0 : 0.0025) - vYaw) * 0.03;
      vPitch *= 0.92;
      yaw += vYaw; pitch += vPitch;
    }
    pitch = Math.max(-0.6, Math.min(1.1, pitch));
    world.rotation.y = yaw + hoverX * 0.15 + scrollY * 0.0015;
    world.rotation.x = pitch + hoverY * 0.1;

    if (!reduced) {
      blocks.forEach((b, i) => {
        b.rotation.x += b.userData.spin.x * dt;
        b.rotation.y += b.userData.spin.y * dt;
        b.position.y = points[i].y + Math.sin(t * 1.4 + i) * 0.12;
        // A "new block" pulse runs around the chain.
        const phase = ((t * 1.2 - i) % N + N) % N;
        b.scale.setScalar(1 + Math.max(0, 1 - phase) * 0.35);
      });
      core.rotation.y += dt * 0.35;
      core.rotation.x += dt * 0.15;
      inner.rotation.y -= dt * 1.2;
      packets.forEach((m) => {
        m.userData.t = (m.userData.t + dt * 0.9) % N;
        const i = Math.floor(m.userData.t), f = m.userData.t - i;
        tmp.copy(points[i]).lerp(points[(i + 1) % N], f);
        m.position.copy(tmp);
      });
    }
    renderer.render(scene, camera);
  };
  loop();
}

intro();
rotator();
counters();
quotes();
reveals();
navSpy();
filters();
chain();
