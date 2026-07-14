/*!
 * MeetingCube — jxhxxx 회전 로고 큐브 (three.js)
 * 3×3 루빅스 큐브가 스크램블 → 솔브를 반복하며, 완성되면 로고에 대각 광택이 스윕한다.
 *
 * 의존성: three.js (r1xx, 전역 THREE). cube.js 앞에서 먼저 로드할 것.
 *   <script src="cube/three.min.js"></script>
 *   <script src="cube/cube.js"></script>
 *
 * 사용법 1) 자동: 호스트에 data-meeting-cube 를 달면 DOM 준비 시 자동 마운트
 *   <div id="cube-app" data-meeting-cube data-logo="cube/logo-hero.png"></div>
 * 사용법 2) 수동:
 *   const cube = MeetingCube.mount('#cube-app', { logoUrl: 'cube/logo-hero.png' });
 *   // 나중에: cube.dispose();
 *
 * 옵션(opts):
 *   logoUrl       로고 3×3 스프라이트 경로 (기본: cube.js 옆의 logo-hero.png)
 *   pixelRatioCap 렌더 픽셀비 상한 (기본 2)
 *   spinSpeed     기본 자전 속도 rad/s (기본 0.16)
 *   scrambleDepth 한 사이클당 섞는 배치 수 (기본 3, 클수록 오래 섞임)
 */
(function (global) {
  'use strict';

  // cube.js 자신의 경로를 기억해 기본 로고를 상대경로로 찾는다(어느 페이지에서 불러도 동작).
  var SELF = document.currentScript ? document.currentScript.src : '';
  var BASE = SELF ? SELF.slice(0, SELF.lastIndexOf('/') + 1) : '';

  function resolveHost(h) {
    if (!h) return null;
    return typeof h === 'string' ? document.querySelector(h) : h;
  }

  function mount(hostArg, opts) {
    opts = opts || {};
    var host = resolveHost(hostArg);
    var THREE = global.THREE;
    if (!host || !THREE) {
      if (!THREE) console.warn('[MeetingCube] THREE 를 찾을 수 없어요. three.min.js 를 cube.js 앞에서 로드하세요.');
      return { dispose: function () {} };
    }

    var LOGO_URL = opts.logoUrl || (BASE + 'logo-hero.png');
    var PR_CAP = opts.pixelRatioCap != null ? opts.pixelRatioCap : 2;
    var SPIN = opts.spinSpeed != null ? opts.spinSpeed : 0.16;
    var SCR = opts.scrambleDepth != null ? opts.scrambleDepth : 3;

    // 색 테마 (기본: 파랑). opts.theme 로 통째로 바꿀 수 있다.
    var THEME = opts.theme || {};
    var ENV_STOPS = THEME.envStops || ['#eef2ff', '#c8d2ff', '#9aa8f0'];       // 반사 환경(림라이트 톤)
    var GLASS = THEME.glassShades || [0x3746d8, 0x4453e6, 0x303fd2, 0x4e5cf0, 0x3a49dc]; // 유리 조각 색들
    var ATTEN = THEME.attenuationColor != null ? THEME.attenuationColor : 0x141f9c;       // 유리 두께 흡수색(딥)
    var LOGO_STOPS = THEME.logoGradient || ['#3D7BFF', '#5058F0', '#7128E8']; // 로고 대각 그라데이션
    var GLOW = THEME.glowColor || '#cddcff';                                   // 완성 스윕 글로우 틴트
    var AMBIENT = THEME.ambientColor != null ? THEME.ambientColor : 0x8898d0;  // 채움광 색(파랑 큐브=페리윙클)

    var W = host.clientWidth || 460;
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
    camera.position.set(5.6, 4.4, 8.4); camera.lookAt(0, -0.1, 0);
    var sweepU = { value: -99 };   // 샤인 스윕 공유 유니폼(로고 가로 좌표 0~1)
    var _gq = new THREE.Quaternion(), _gn = new THREE.Vector3(), _gp = new THREE.Vector3();
    var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    // renderScale: 화면보다 크게 렌더해 다운스케일(슈퍼샘플링). 작은 로고 크기에서 계단현상 제거용.
    renderer.setPixelRatio(opts.renderScale != null ? opts.renderScale : Math.min(window.devicePixelRatio, PR_CAP));
    renderer.setSize(W, W);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.NoToneMapping;
    host.appendChild(renderer.domElement);

    var pmrem = new THREE.PMREMGenerator(renderer);
    var ec = document.createElement('canvas'); ec.width = 512; ec.height = 256; var eg = ec.getContext('2d');
    var grd = eg.createLinearGradient(0, 0, 0, 256);
    grd.addColorStop(0, ENV_STOPS[0]); grd.addColorStop(.5, ENV_STOPS[1]); grd.addColorStop(1, ENV_STOPS[2]);
    eg.fillStyle = grd; eg.fillRect(0, 0, 512, 256);
    var band = eg.createLinearGradient(0, 28, 0, 100);
    band.addColorStop(0, 'rgba(255,255,255,0)'); band.addColorStop(.5, 'rgba(255,255,255,.7)'); band.addColorStop(1, 'rgba(255,255,255,0)');
    eg.fillStyle = band; eg.fillRect(0, 28, 512, 72);
    var envTex = new THREE.CanvasTexture(ec); envTex.mapping = THREE.EquirectangularReflectionMapping;
    var envRT = pmrem.fromEquirectangular(envTex);
    scene.environment = envRT.texture;

    scene.add(new THREE.AmbientLight(0x8898d0, 0.5));
    var key = new THREE.DirectionalLight(0xffffff, 0.7); key.position.set(5, 8, 6); scene.add(key);
    var rim = new THREE.PointLight(0xffffff, 0.45, 30); rim.position.set(-5, 3, 6); scene.add(rim);

    var iceShades = GLASS;
    function iceMat(shade) {
      return new THREE.MeshPhysicalMaterial({ color: shade, metalness: 0, roughness: 0.14,
        transmission: 0.15, thickness: 1.5, ior: 1.34, transparent: true, opacity: 1.0,   // 투과↓: 뒷면 로고 유령 비침 제거
        attenuationColor: new THREE.Color(ATTEN), attenuationDistance: 0.8,
        clearcoat: 0.55, clearcoatRoughness: 0.24, envMapIntensity: 0.4 });   // 스펙큘러 분산(가짜 스윕 방지)
    }
    var geo = new THREE.BoxGeometry(0.94, 0.94, 0.94), S = 1.0;
    var main = new THREE.Group(); main.rotation.x = -0.32; main.rotation.z = 0.06; scene.add(main);

    var cubies = [], exFaces = [], glowMats = [], deepMats = [];
    function faceCR(nAxis, sign, gx, gy, gz) {
      // 각 면을 '바깥에서 볼 때' 로고가 조립되도록 열/행 매핑 (뒷면·바닥면은 x가 거울 반전됨)
      if (nAxis === 'z') return { col: (sign > 0 ? gx + 1 : 1 - gx), row: 1 - gy };
      if (nAxis === 'x') return { col: (sign > 0 ? 1 - gz : gz + 1), row: 1 - gy };
      return { col: (sign > 0 ? gx + 1 : 1 - gx), row: (sign > 0 ? gz + 1 : 1 - gz) };
    }
    var idx = 0;
    for (var gx = -1; gx <= 1; gx++) for (var gy = -1; gy <= 1; gy++) for (var gz = -1; gz <= 1; gz++) {
      var shade = iceShades[(idx * 7) % iceShades.length];
      var mats = [iceMat(shade), iceMat(shade), iceMat(shade), iceMat(shade), iceMat(shade), iceMat(shade)];
      var cube = new THREE.Mesh(geo, mats); cube.position.set(gx * S, gy * S, gz * S);
      cube.userData.home = cube.position.clone();   // 완성 검증용 홈 좌표
      main.add(cube); cubies.push(cube);
      var cr;
      if (gx === 1) { cr = faceCR('x', 1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'x', sign: 1, col: cr.col, row: cr.row }); }
      if (gx === -1) { cr = faceCR('x', -1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'x', sign: -1, col: cr.col, row: cr.row }); }
      if (gy === 1) { cr = faceCR('y', 1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'y', sign: 1, col: cr.col, row: cr.row }); }
      if (gy === -1) { cr = faceCR('y', -1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'y', sign: -1, col: cr.col, row: cr.row }); }
      if (gz === 1) { cr = faceCR('z', 1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'z', sign: 1, col: cr.col, row: cr.row }); }
      if (gz === -1) { cr = faceCR('z', -1, gx, gy, gz); exFaces.push({ cube: cube, axis: 'z', sign: -1, col: cr.col, row: cr.row }); }
      idx++;
    }
    var logoImg = new Image();
    logoImg.onload = function () {
      if (!alive) return;   // 로드 완료 전에 dispose 됐으면 죽은 인스턴스에 자원 생성 금지
      var sw = logoImg.width / 3, sh = logoImg.height / 3;
      var pgeo = new THREE.PlaneGeometry(0.94, 0.94);
      function place(pl, f, o) {
        if (f.axis === 'x') { pl.position.x = f.sign * o; pl.rotation.y = f.sign > 0 ? Math.PI / 2 : -Math.PI / 2; }
        else if (f.axis === 'y') { pl.position.y = f.sign * o; pl.rotation.x = f.sign > 0 ? -Math.PI / 2 : Math.PI / 2; }
        else { pl.position.z = f.sign * o; if (f.sign < 0) pl.rotation.y = Math.PI; }
      }
      function sweepShader(shader) {
        // 로고 좌표(lx,ly) 기반 15° 대각 밴드: 쨍한 코어 + 뒤따르는 은은한 글로우
        shader.uniforms.uSweep = sweepU;
        shader.fragmentShader = shader.fragmentShader
          .replace('#include <common>', '#include <common>\nuniform float uSweep;')
          .replace('#include <dithering_fragment>', '#include <dithering_fragment>\nfloat lx = (float(UCOL) + vUv.x) / 3.0;\nfloat ly = (float(UROW) + (1.0 - vUv.y)) / 3.0;\nfloat d = lx + 0.28*(ly - 0.5) - uSweep;\nfloat core = 1.0 - smoothstep(0.0, 0.13, abs(d));\nfloat glow = 1.0 - smoothstep(0.0, 0.5, abs(d + 0.08));\ngl_FragColor.a *= core * 0.75 + glow * 0.3;');
      }
      exFaces.forEach(function (f) {
        // 찐하고 쨍한 로고(버튼 블러플 톤 그라데이션으로 리컬러, 로고 전체에 대각 그라데이션)
        var cv = document.createElement('canvas'); cv.width = cv.height = 200; var g = cv.getContext('2d');
        g.drawImage(logoImg, f.col * sw, f.row * sh, sw, sh, 0, 0, 200, 200);
        g.globalCompositeOperation = 'source-in';
        var lgr = g.createLinearGradient(-f.col * 200, -f.row * 200, 600 - f.col * 200, 600 - f.row * 200);
        lgr.addColorStop(0, LOGO_STOPS[0]); lgr.addColorStop(0.5, LOGO_STOPS[1]); lgr.addColorStop(1, LOGO_STOPS[2]);
        g.fillStyle = lgr; g.fillRect(0, 0, 200, 200);
        var tex = new THREE.CanvasTexture(cv); tex.anisotropy = 4;
        tex.encoding = THREE.sRGBEncoding;   // 캔버스 색을 화면에 1:1로(washed-out 방지)
        var pmat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false });
        var pl = new THREE.Mesh(pgeo, pmat);
        place(pl, f, 0.482); f.cube.add(pl);
        deepMats.push({ mat: pmat, mesh: pl });
        // 흰 글로우(솔브 시 좌→우 스윕, 월드좌표 밴드 셰이더)
        var wc = document.createElement('canvas'); wc.width = wc.height = 200; var wg = wc.getContext('2d');
        wg.drawImage(logoImg, f.col * sw, f.row * sh, sw, sh, 0, 0, 200, 200);
        wg.globalCompositeOperation = 'source-in'; wg.fillStyle = GLOW; wg.fillRect(0, 0, 200, 200);   // 글로우 틴트
        var wtex = new THREE.CanvasTexture(wc); wtex.anisotropy = 4;
        wtex.encoding = THREE.sRGBEncoding;
        var wmat = new THREE.MeshBasicMaterial({ map: wtex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
        wmat.defines = { UCOL: f.col, UROW: f.row };
        wmat.onBeforeCompile = sweepShader;
        var wpl = new THREE.Mesh(pgeo, wmat);
        place(wpl, f, 0.485); f.cube.add(wpl);
        glowMats.push({ mat: wmat, mesh: wpl });
      });
    };
    logoImg.src = LOGO_URL;

    var AX = ['x', 'y', 'z'], moves = [], nextAt = 0.6, history = [], phase = 'scramble', solvedPause = false;
    function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
    function makeMoves(batch) {
      moves = batch.map(function (b) {
        var pv = new THREE.Group(); main.add(pv);
        var cubes = cubies.filter(function (c) { return Math.round(c.position[b.axis]) === b.coord; });
        cubes.forEach(function (c) { pv.attach(c); });
        return { pv: pv, axis: b.axis, cubes: cubes, prog: 0, target: b.dir * Math.PI / 2, speed: 0.016 + Math.random() * 0.008 };
      });
    }
    function startBatch() {
      var batch;
      if (phase === 'scramble') {
        var axis = AX[Math.floor(Math.random() * 3)], count = Math.random() < 0.5 ? 2 : 3;
        var coords = shuffle([-1, 0, 1]).slice(0, count);
        batch = coords.map(function (coord) { return { axis: axis, coord: coord, dir: (Math.random() < 0.5 ? 1 : -1) }; });
        history.push(batch);
        if (history.length >= SCR) phase = 'solve';
      } else {
        batch = history.pop().map(function (m) { return { axis: m.axis, coord: m.coord, dir: -m.dir }; });
        if (history.length === 0) { phase = 'scramble'; solvedPause = true; }
      }
      makeMoves(batch);
    }
    var _sm = new THREE.Matrix4();
    function bakeBatch() {
      moves.forEach(function (m) {
        m.cubes.forEach(function (c) {
          main.attach(c);
          c.position.set(Math.round(c.position.x), Math.round(c.position.y), Math.round(c.position.z));
          // 회전 90° 격자 스냅(부동소수 누적 방지 → 항상 정확한 상태 유지)
          _sm.makeRotationFromQuaternion(c.quaternion);
          var el = _sm.elements;
          for (var k = 0; k < 12; k++) el[k] = Math.round(el[k]);
          c.quaternion.setFromRotationMatrix(_sm);
        });
        main.remove(m.pv);
      });
      moves = [];
    }
    // 27조각 전부 홈 위치 + 정방향인지(=모든 면 로고 완성) 검증
    function isSolved() {
      for (var i = 0; i < cubies.length; i++) {
        var c = cubies[i], h = c.userData.home, q = c.quaternion;
        if (Math.round(c.position.x) !== h.x || Math.round(c.position.y) !== h.y || Math.round(c.position.z) !== h.z) return false;
        if (Math.abs(q.x) > 0.01 || Math.abs(q.y) > 0.01 || Math.abs(q.z) > 0.01) return false;
      }
      return true;
    }
    function facing(mesh) {
      mesh.getWorldQuaternion(_gq); _gn.set(0, 0, 1).applyQuaternion(_gq);
      mesh.getWorldPosition(_gp); _gp.sub(camera.position).normalize();
      return _gn.dot(_gp) < -0.03;
    }
    var t0 = performance.now(), spinY = 0, lastT = 0, holdUntil = 0, flashT = -1;
    var rafId = 0, alive = true;
    function tick(now) {
      if (!alive) return;
      var t = (now - t0) / 1000, dt = Math.min(t - lastT, 0.05); lastT = t;
      if (t >= holdUntil) spinY += dt * SPIN;   // 완성 정지 구간엔 회전도 멈춤
      main.rotation.y = spinY;
      // 뒷면 딥 로고 숨김: 유리 너머로 비치는 유령 로고 원천 제거
      for (var di = 0; di < deepMats.length; di++) deepMats[di].mat.opacity = facing(deepMats[di].mesh) ? 1 : 0;
      if (flashT >= 0) {                          // 완성 검증 후 로고별 좌→우 대각 광택 스윕
        var fe = t - flashT;
        if (fe >= 0) {
          var fp = fe / 1.8;
          if (fp < 1) {
            var ep = -(Math.cos(Math.PI * fp) - 1) / 2;   // 사인 이징(완만한 가감속)
            sweepU.value = -0.45 + ep * 1.9;    // 로고 왼쪽 밖 → 오른쪽 밖(대각 보정)
            // 카메라 쪽을 향한 면 전부 스윕(뒷면 글로우만 차단 → 유령 발광 방지)
            for (var gi = 0; gi < glowMats.length; gi++)
              glowMats[gi].mat.opacity = facing(glowMats[gi].mesh) ? 1 : 0;
          } else {
            sweepU.value = -99;
            for (var gj = 0; gj < glowMats.length; gj++) glowMats[gj].mat.opacity = 0;
            flashT = -1;
          }
        }
      }
      if (moves.length) {
        var allDone = true;
        moves.forEach(function (m) { m.prog = Math.min(m.prog + m.speed, 1); var e = m.prog * m.prog * (3 - 2 * m.prog); m.pv.rotation[m.axis] = m.target * e; if (m.prog < 1) allDone = false; });
        if (allDone) {
          bakeBatch();
          if (solvedPause) {
            solvedPause = false;
            // 자가 치유: 혹시라도 어긋났으면 홈+정방향으로 강제 복원(완성 상태 보장)
            if (!isSolved()) { cubies.forEach(function (c) { c.position.copy(c.userData.home); c.quaternion.set(0, 0, 0, 1); }); }
            holdUntil = t + 2.6; nextAt = t + 2.6; flashT = t + 0.35;
          } else { startBatch(); }
        }
      } else if (t > nextAt) { startBatch(); }
      renderer.render(scene, camera);
      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);

    function onResize() { var w = host.clientWidth || 460; renderer.setSize(w, w); }
    window.addEventListener('resize', onResize);

    function dispose() {
      alive = false;
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', onResize);
      try { if (renderer.domElement && renderer.domElement.parentNode === host) host.removeChild(renderer.domElement); } catch (e) {}
      // renderer.dispose() 는 지오메트리·머티리얼·텍스처를 해제하지 않는다 → 씬을 훑어 직접 해제(GPU 누수 방지)
      scene.traverse(function (o) {
        if (o.geometry && o.geometry.dispose) o.geometry.dispose();
        var m = o.material;
        if (m) (Array.isArray(m) ? m : [m]).forEach(function (mm) {
          if (mm && mm.map && mm.map.dispose) mm.map.dispose();
          if (mm && mm.dispose) mm.dispose();
        });
      });
      if (envTex && envTex.dispose) envTex.dispose();
      if (envRT && envRT.dispose) envRT.dispose();
      if (pmrem && pmrem.dispose) pmrem.dispose();
      if (renderer.dispose) renderer.dispose();
    }

    return { dispose: dispose, renderer: renderer, scene: scene };
  }

  function autoInit() {
    var nodes = document.querySelectorAll('[data-meeting-cube]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.__meetingCube) continue;            // 중복 마운트 방지
      el.__meetingCube = mount(el, { logoUrl: el.getAttribute('data-logo') || undefined });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', autoInit);
  else autoInit();

  global.MeetingCube = { mount: mount };
})(window);
