<template>
  <div class="collect-block">
    <h2>Коллекции</h2>

    <div class="collect-placeholder">
      <p class="placeholder-text">
        ⚙ Раздел с коллекциями появится в одном из следующих обновлений.<br>
        Пока просто представь, что ты всё уже собрал.
      </p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.collect-block {
  max-width: 300px;
  border: 2px solid rgba(0, 0, 0, 0.692);
  height: 300px;
  padding: 10px;
  backdrop-filter: blur(7px);
  background: rgba(38, 32, 39, 0.48);
  border-radius: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: white;
}

.collect-block h2 {
  position: relative;
  font-size: 18px;
  text-align: left;
  color: white;
  margin-bottom: 8px;
}

.collect-block h2::after {
  content: "";
  display: block;
  width: 100%;
  height: 1px;
  background-color: white;
  opacity: 0.4;
  margin: 6px auto 0;
  border-radius: 1px;
}

.collect-placeholder {
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
  font-size: 13px;
  margin-top: 10px;
}

.placeholder-text {
  margin: 0;
  line-height: 1.4;
}
</style>
