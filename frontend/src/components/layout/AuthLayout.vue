<script setup>
import { ref, computed } from "vue";

const mouseX = ref(0)
const mouseY = ref(0)

const parallaxStyle = computed(() => {
  const maxShift = 30
  const x = ((mouseX.value - window.innerWidth / 2) / window.innerWidth) * maxShift
  const y = ((mouseY.value - window.innerHeight / 2) / window.innerHeight) * maxShift
  return {
    transform: `translate(${x}px, ${y}px)`
  }
})

if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', (e) => {
    mouseX.value = e.clientX
    mouseY.value = e.clientY
  })
}
</script>

<template>
  <div class="bg-parallax" :style="parallaxStyle"></div>

  <div class="layout">
    <main>
      <router-view />
    </main>

    <footer>
      <p>&copy; 2025 Omenigen. Все права защищены.</p>
    </footer>
  </div>
</template>

<style lang="scss">
.bg-parallax {
  position: fixed;
  top: -50px;
  left: -50px;
  width: calc(100vw + 100px);
  height: calc(100vh + 100px);
  background: url('/images/purple_art2.png') no-repeat center center;
  background-size: 98%;
  z-index: -1;
  transition: transform 0.4s ease-out;
  pointer-events: none;
  will-change: transform;
  overflow: hidden;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-size: cover;
}

main {
  zoom: 0.9;
  flex: 1;
  padding: 30px;
  color: white;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding-top: 60px;
  padding-bottom: 40px;
}

footer {
  background-color: rgba(0, 0, 0, 0.459);
  color: white;
  padding: 6px 0;
  text-align: center;
  width: 100%;
  position: fixed;
  left: 0;
  bottom: 0;
  z-index: 1000;
  box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.2);
}
</style>
