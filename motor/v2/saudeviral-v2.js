/* saudeviral — primitivos de dados para o runtime do explicavideo v2 (V2.P), no mesmo contrato:
   fn(box, shot, ctx) com tempos já em segundos relativos à cena; tudo em c.tl (GSAP, seek-safe).
   Área útil x 90–1420, y 170–900 (direita = avatar + PARA LEVAR; embaixo = legenda e fonte). */
(function () {
  const { h, esc, rich, fs } = V2.util;
  const def = (v, d) => (v == null || Number.isNaN(v) ? d : v);
  const fmt = (v, dec) => v.toLocaleString('pt-BR', { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });

  // capa — quadro 0 cheio (hook com "capa": true): data, linhas grandes, subtítulo e a fileira de rostos/miniaturas.
  // Nasce visível em t=0 (o v2 trata o 1º shot "hook" em @start como capa pronta).
  const hookV2 = V2.P.hook;
  V2.P.hook = function (box, s, c) {
    if (!s.capa) return hookV2(box, s, c);
    if (s.src) { const im = h(box, 'div', 'fv-capbg', `background-image:url("${s.src}")`); c.tl.fromTo(im, { scale: 1.04 }, { scale: 1.12, duration: Math.max(1, c.T1), ease: 'none', immediateRender: true }, 0); }
    const w = h(box, 'div', 'fv-capa', '', `${s.data ? `<div class="dt">${esc(s.data)}</div>` : ''}${(s.linhas || []).map((l) =>
      `<div class="ln" style="font-size:${l.size || 120}px;color:${l.cor || '#eef3ff'}">${rich(l.text)}</div>`).join('')}${s.sub ? `<div class="sb">${rich(s.sub)}</div>` : ''}
      <div class="rostos">${(s.fotos || []).map((f) => `<div style="background-image:url('${f}')"></div>`).join('')}</div>`);
    c.tl.set(w, { opacity: 1 }, 0);
  };

  // ficha — quem falou: miniatura do vídeo + ranking + nome + canal/data
  V2.P.ficha = function (box, s, c) {
    const t = def(s.at, c.T0 + 0.05);
    const im = h(box, 'div', 'fv-thumb', `background-image:url("${s.foto}")`);
    const tx = h(box, 'div', 'fv-ftx', '', `<div class="rk">${esc(s.rk || '')}</div><div class="nm" style="font-size:${fs(s.nome, 92, 60, 10, 26)}px">${esc(s.nome)}</div><div class="cn">${rich(s.canal || '')}</div>`);
    c.tl.fromTo(im, { opacity: 0, x: -80, scale: 0.94 }, { opacity: 1, x: 0, scale: 1, duration: 0.6, ease: 'power3.out' }, t);
    c.tl.fromTo(im, { backgroundSize: '100%' }, { backgroundSize: '112%', duration: Math.max(1, c.T1 - t), ease: 'none' }, t);
    c.tl.fromTo(tx, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, t + 0.25);
  };

  // numero — número gigante com contador em pt-BR (206.900), seta e legenda
  V2.P.numero = function (box, s, c) {
    const t = def(s.at, c.T0 + 0.05), st = { v: Number(s.de) || 0 }, cor = s.cor || '#eef3ff';
    const k = h(box, 'div', 'fv-nk', '', esc(s.k || ''));
    const nn = h(box, 'div', 'fv-nn', `color:${cor}`);
    const seta = s.seta ? `<span class="seta" style="color:${s.seta === '▲' ? 'var(--mint)' : 'var(--rose)'}">${s.seta}</span>` : '';
    c.render(() => { nn.innerHTML = `${s.pre ? `<i>${esc(s.pre)}</i>` : ''}${fmt(st.v, s.dec)}${s.unid ? `<small>${esc(s.unid)}</small>` : ''}${seta}`; });
    c.fade(k, t);
    c.tl.fromTo(nn, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.45, ease: 'back.out(1.8)' }, t);
    c.tl.fromTo(st, { v: Number(s.de) || 0 }, { v: Number(s.ate) || 0, duration: s.dur || 1.6, ease: 'power2.out' }, t);
    if (s.l) { const l = h(box, 'div', 'fv-nl', '', rich(s.l)); c.rise(l, def(s.l_at, t + 0.8), 20); }
  };

  // citacao — trecho literal de quem falou (aspas, autor, data); fonte sempre visível
  V2.P.citacao = function (box, s, c) {
    const t = def(s.at, c.T0 + 0.05);
    const card = h(box, 'div', 'fv-cit', '', `<div class="k">${esc(s.k || 'O QUE ELE DISSE')}</div><div class="q" style="font-size:${fs(s.q, 54, 34, 50, 230)}px">${rich(s.q)}</div><div class="w">${esc(s.w || '')}</div>`);
    c.tl.fromTo(card, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.55, ease: 'power3.out' }, t);
    c.tl.fromTo(card.querySelector('.q'), { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: Math.min(2.5, Math.max(0.8, (c.T1 - t) * 0.4)), ease: 'none' }, t + 0.3);
  };

  // grafico — linha desenhada aos poucos, com rótulo e ponto final
  V2.P.grafico = function (box, s, c) {
    const t = def(s.at, c.T0 + 0.1), S = s.serie || [0, 1], W = 1250, H = 460, cor = s.cor || '#3ef0a0';
    const mn = Math.min(...S), mx = Math.max(...S);
    const pts = S.map((v, i) => [i / Math.max(1, S.length - 1) * W, H - (v - mn) / (mx - mn || 1) * H * 0.9 - 10]);
    const d = 'M' + pts.map((p) => p.map((x) => x.toFixed(1)).join(',')).join(' L');
    const wrap = h(box, 'div', 'fv-graf', '', `<div class="rot">${rich(s.rotulo || '')}</div><svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible">
      <path class="ln" d="${d}" fill="none" stroke="${cor}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round" style="filter:drop-shadow(0 0 14px ${cor})"/>
      <circle class="pt" cx="${pts[pts.length - 1][0]}" cy="${pts[pts.length - 1][1]}" r="15" fill="#fff" stroke="${cor}" stroke-width="7"/></svg>`);
    const ln = wrap.querySelector('.ln'), L = ln.getTotalLength();
    ln.style.strokeDasharray = L;
    c.fade(wrap, t);
    c.tl.fromTo(ln, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: s.dur || 2.2, ease: 'power1.inOut' }, t + 0.2);
    c.tl.fromTo(wrap.querySelector('.pt'), { opacity: 0, scale: 0, transformOrigin: '50% 50%' }, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(3)' }, t + 0.2 + (s.dur || 2.2));
  };

  // carimbo — POLÊMICA / ALERTA batendo por cima do shot anterior (use "keep": true)
  V2.P.carimbo = function (box, s, c) {
    const t = def(s.at, c.T0 + 0.05), cor = s.cor || 'var(--rose)';
    const k = h(box, 'div', 'fv-carimbo', `color:${cor};border-color:${cor}`, esc(s.txt || 'POLÊMICA'));
    c.tl.fromTo(k, { opacity: 0, scale: 2.4, rotation: -9 }, { opacity: 1, scale: 1, rotation: -9, duration: 0.3, ease: 'power4.in' }, t);
    c.tl.fromTo(k, { x: 0 }, { x: 6, duration: 0.05, yoyo: true, repeat: 3 }, t + 0.3);
  };
})();
