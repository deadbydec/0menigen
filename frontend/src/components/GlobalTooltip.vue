<template>
  <div
    v-if="visible"
    class="global-tooltip"
    :style="{ top: `${y + 12}px`, left: `${x + 12}px` }"
  >
    {{ text }}
  </div>
</template>

<script setup>
import { useTooltipStore } from '@/store/tooltipStore'
import { storeToRefs } from 'pinia'

const tooltip = useTooltipStore()
const { visible, text, x, y } = storeToRefs(tooltip)
</script>

<style scoped>
.global-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.88);
  color: #fff;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 6px;
  max-width: 250px;
  white-space: normal;
  word-break: break-word;
  z-index: 9999;
  pointer-events: none;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.5);
}
</style>
