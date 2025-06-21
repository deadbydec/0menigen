// /store/tooltip.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTooltipStore = defineStore('tooltip', () => {
  const visible = ref(false)
  const text = ref('')
  const x = ref(0)
  const y = ref(0)

  function show(content, event) {
    text.value = content
    x.value = event.clientX
    y.value = event.clientY
    visible.value = true
  }

  function hide() {
    visible.value = false
  }

  return { visible, text, x, y, show, hide }
})
