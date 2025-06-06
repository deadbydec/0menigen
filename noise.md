✅ 1. Через background-image с готовым шумом (png/webp):
Самый стабильный способ —
генерируешь в Affinity / Photopea / генераторе (можно даже https://csshero.org/mesher/) и сохраняешь, например:

scss
Копировать
Редактировать
body {
  background-image: 
    url('/assets/noise.png'), 
    linear-gradient(#ccc, #ccc); // ← или твой фон подложкой
  background-blend-mode: overlay; // 👈 или multiply, soft-light
  background-size: cover;
}
Шум поверх цвета = красиво, матово, глубоко.

🧪 2. Через CSS-градиент-хаки (ограниченно):
Можно сделать псевдошум из повторяющихся точек:

scss
Копировать
Редактировать
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: 
    radial-gradient(#0000000d 1px, transparent 1px);
  background-size: 2px 2px;
  opacity: 0.08;
  z-index: 999;
}
⚠️ Это не настоящий шум, но визуально похож — пиксельная сетка.

🧨 3. SVG-шум (inline или base64):
Можно вставить SVG-фильтр (если хочешь шум как маску):

css
Копировать
Редактировать
filter: url('#noiseFilter');
Но это либо через feTurbulence, либо через canvas, что уже не SCSS напрямую, а JS+SVG.