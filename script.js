(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Hero: the 64-move plan is masked, denoised over 10 steps with a few
  // remask-and-revise events, held, and repeated three times, then rests.
  const panel = document.querySelector('.plan-panel');
  const cells = panel ? Array.from(panel.querySelectorAll('.plan i')) : [];
  if (cells.length === 64) {
    const status = panel.querySelector('[data-status]');
    const targets = cells.map(c => c.dataset.d);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'label';
    panel.querySelector('.plan-ctl').append(button);

    const SLICES = [7, 7, 7, 7, 6, 6, 6, 6, 6, 6];
    const DRAFT = 700, STEP = 420, HOLD = 2400, LOOPS = 3;
    let queue = [], loops = 0, timer = null, paused = false;

    const shuffled = () => {
      const a = cells.map((_, i) => i);
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    };
    const show = (i, d) => {
      cells[i].classList.remove('m');
      cells[i].classList.add('n');
      cells[i].dataset.d = d;
    };
    const wrong = i => String((Number(targets[i]) + 1 + Math.floor(Math.random() * 7)) % 8);

    const buildLoop = () => {
      const order = shuffled();
      const events = Array.from({ length: 11 }, () => []);
      let pos = 0;
      SLICES.forEach((n, s) => {
        const k = s + 1;
        order.slice(pos, pos + n).forEach((i, idx) => {
          const revise = k <= 5 && idx === 0;
          events[k].push(() => show(i, revise ? wrong(i) : targets[i]));
          if (revise) {
            events[k + 2].push(() => cells[i].classList.add('m'));
            events[k + 3].push(() => show(i, targets[i]));
          }
        });
        pos += n;
      });
      const frames = [[() => {
        cells.forEach(c => c.classList.add('m'));
        status.textContent = 'drafting';
      }, DRAFT]];
      for (let k = 1; k <= 10; k++) {
        frames.push([() => {
          cells.forEach(c => c.classList.remove('n'));
          events[k].forEach(fn => fn());
          status.textContent = 'denoise ' + String(k).padStart(2, '0') + '/10';
        }, STEP]);
      }
      frames.push([() => cells.forEach(c => c.classList.remove('n')), HOLD]);
      return frames;
    };

    const run = () => {
      if (!queue.length) {
        loops += 1;
        if (loops >= LOOPS) { timer = null; button.textContent = 'replay'; return; }
        queue = buildLoop();
      }
      const [fn, delay] = queue.shift();
      fn();
      timer = setTimeout(run, delay);
    };
    const start = () => {
      loops = 0;
      paused = false;
      queue = buildLoop();
      button.textContent = 'pause';
      run();
    };
    button.addEventListener('click', () => {
      if (timer === null && !paused) { start(); return; }
      paused = !paused;
      button.textContent = paused ? 'play' : 'pause';
      if (paused) { clearTimeout(timer); timer = null; } else run();
    });
    if (document.hidden) document.addEventListener('visibilitychange', start, { once: true });
    else start();
  }
})();
