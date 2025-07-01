<template>
  <div class="test-block clan-block">
    <h2>🚀 Создать свой клан</h2>

    <p>
      Мечтаешь построить империю, где ты — лидер? Теперь ты можешь создать свой собственный клан и пригласить в него других Омежек.
    </p>

    <ul class="conditions">
      <li>🔹 Достигни <strong>100 уровня</strong> <em>или</em></li>
      <li>🔸 Активируй <strong>VIP-подписку</strong> любого уровня</li>
    </ul>

    <div class="actions">
      <button 
        v-if="canCreateClan" 
        class="create-btn" 
        @click="showModal = true"
      >
        ✨ Создать клан
      </button>

      <div v-else class="locked-msg">
        🛑 Условия не выполнены. Ты пока не можешь создать клан.
      </div>
    </div>
    <CreateModal :visible="showModal" @close="showModal = false" />
  </div>
  
</template>

<script setup>
import { ref, computed } from "vue"
import { storeToRefs } from "pinia"
import { usePlayerStore } from "@/store/player"
import CreateModal from "@/components/clans/CreateModal.vue" // путь по факту
// или '@/modals/CreateModal.vue' — проверь свой

const { player } = storeToRefs(usePlayerStore())

const showModal = ref(false)

const canCreateClan = computed(() => {
  if (!player.value) return false
  return player.value.level >= 100 || !!player.value.vip_subscription
})
</script>


<style scoped>
.test-block {
  background:rgba(38, 32, 39, 0.74);
  border: 1px solid #444;
  border-radius: 12px;
  padding: 1.5em;
  margin-bottom: 0em;
  text-align: left;
}
.conditions {
  margin-top: 0.5em;
  margin-bottom: 1em;
  padding-left: 1.2em;
}
.create-btn {
  background:linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  color: rgb(219, 219, 219);
  padding: 0.6em 1.2em;
  margin-left: 180px;
  width: 180px;
  font-weight: bold;
  border-radius: 8px;
}
.locked-msg {
  opacity: 0.6;
  font-style: italic;
}
</style>
