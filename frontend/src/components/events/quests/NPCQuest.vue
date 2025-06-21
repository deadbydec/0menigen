<template>
  <div class="npc-quest-wrapper">
    <div class="npc-header">
      <button class="back-button" @click="goBack">← НАЗАД</button>
      <div class="npc-name">{{ npcData?.name || "NPC" }}</div>
      <p v-if="timeLeft" class="quest-timer">⏳ Осталось: {{ timeLeft }}</p>
      <div class="npc-limit">лимит: {{ used }}/{{ limit }}</div>
    
    </div>

    <div class="npc-content">
      <div class="npc-image-block">
        <img :src="getAvatarUrl(npcData?.avatar)" alt="npc" class="npc-image" />
      
    </div>

      <div class="npc-bubble-block">
        <div class="npc-speech-bubble">
          <div class="bubble-text">{{ currentQuote }}</div>

          <!-- 🔄 Квест-предмет -->
          <div v-if="currentItem" class="bubble-item">
            Принеси мне:<img :src="getItemIcon(currentItem.image)" class="item-icon" />
            <span class="item-name">{{ currentItem.name }}</span>
          </div>
          


          <!-- 🎁 Награды -->
          <div v-if="rewardDisplay.length" class="bubble-reward">
            <div v-for="(r, i) in rewardDisplay" :key="i" class="reward-entry">
              <img v-if="r.icon" :src="getItemIcon(r.icon)" class="reward-icon" />
              <span>{{ r.text }}</span>
            </div>
          </div>
        </div>

        <!-- 🟡 ОДНА КНОПКА -->
        <!-- 🟡 Кнопка, которая корректно вызывает нужную функцию -->
<button
  class="accept-button"
  @click="handleButtonClick"
>
  {{ hasActiveQuest ? "СДАТЬ КВЕСТ" : "ВЗЯТЬ КВЕСТ" }}
</button>

      </div>
    </div>
  </div>
</template>



<script setup>
import { useRoute, useRouter } from "vue-router"
import { nextTick, onMounted, ref, computed } from "vue"
import { useQuestStore } from "@/store/questStore"
import { usePlayerStore } from "@/store/player"

const route = useRoute()
const router = useRouter()
const questStore = useQuestStore()
const playerStore = usePlayerStore()

const npcId = route.params.npcId
const npcData = ref(null)
const used = ref(0)
const limit = ref(5)
const currentQuote = ref("...")
const currentItem = ref(null)
const rewardDisplay = ref([])
const timeLeft = ref(null)
let countdownInterval = null
const isValidDate = (d) => d instanceof Date && !isNaN(d.getTime())


const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
const getAvatarUrl = (filename) => `${STATIC_BASE}/static/npcs/${filename}`
const getItemIcon = (filename) => `${STATIC_BASE}/static/goods/${filename}`

const goBack = () => router.back()

const activeQuest = computed(() =>
  questStore.activeQuests.find(q => q.npc_id === npcId && !q.completed && !q.failed)
)

const hasActiveQuest = computed(() => !!activeQuest.value)

const randomLine = (arr) => {
  if (!arr?.length) return ""
  return arr[Math.floor(Math.random() * arr.length)]
}

const handleButtonClick = () => {
  hasActiveQuest.value ? turnIn() : acceptQuest()
}

const updateCurrentItem = () => {
  const item = activeQuest.value?.item
  currentItem.value = item?.image && item?.name ? item : null
}

async function turnIn() {
  const quest = activeQuest.value ? { ...activeQuest.value } : null
  if (!quest) return

  try {
    const res = await questStore.turnInQuest(quest.id)

    if (!res || res.status !== "ok") {
      currentQuote.value = "У тебя нет нужного предмета!"
      rewardDisplay.value = []
      return
    }

    const rewardText = [
      { text: `+${res.xp} XP`, icon: null },
      { text: `+${res.coins} монет`, icon: null },
    ]

    if (res.extra) {
      for (const [cat, item] of Object.entries(res.extra)) {
        rewardText.push({ text: `🎁 ${item.name}`, icon: item.icon })
      }
    }

    rewardDisplay.value = rewardText
    currentQuote.value = "Ладно, живи. Вот твоя награда:"
    currentItem.value = null

    await questStore.fetchActiveQuests()
    await playerStore.fetchPlayer()

    used.value = questStore.activeQuests.filter(q => q.npc_id === npcId).length
  } catch (e) {
    console.warn("❌ Ошибка при сдаче:", e)
    currentQuote.value = "❌ Сбой при сдаче квеста!"
    rewardDisplay.value = []

    const icon = document.querySelector(".item-icon")
    if (icon) {
      icon.classList.add("shake")
      setTimeout(() => icon.classList.remove("shake"), 500)
    }
  }
}

function normalizeIsoDate(rawStr) {
  return rawStr.split(".")[0] + "Z"  // обрезаем .834626 и добавляем Z
}


async function startCountdown(rawExpiresAtStr) {
  if (countdownInterval) clearInterval(countdownInterval)

  const normalized = normalizeIsoDate(rawExpiresAtStr)
  const expiresAt = new Date(normalized)

  if (!(expiresAt instanceof Date) || isNaN(expiresAt.getTime())) {
    console.warn("❌ Невалидная дата после normalize:", rawExpiresAtStr)
    return
  }

  countdownInterval = setInterval(async () => {
    const now = new Date()
    const diff = expiresAt - now

    if (diff <= 0) {
      clearInterval(countdownInterval)
      timeLeft.value = null

      await questStore.fetchActiveQuests()
      await nextTick()

      const stillExists = questStore.activeQuests.some(q => q.npc_id === npcId && !q.completed && !q.failed)
      if (!stillExists) {
        currentQuote.value = "Ты профукал время. Квест провален."
        used.value = questStore.activeQuests.filter(q => q.npc_id === npcId).length
        currentItem.value = null
      }

      return
    }

    const minutes = Math.floor(diff / 1000 / 60)
    const seconds = Math.floor((diff / 1000) % 60)
    timeLeft.value = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
  }, 1000)
}



async function acceptQuest() {
  if (!npcData.value?.id || hasActiveQuest.value) return

  try {
    await questStore.acceptQuest(npcData.value.id)
    await questStore.fetchActiveQuests()

    // ⏳ Ждём nextTick, чтобы computed обновился
    await nextTick()

    used.value = questStore.activeQuests.filter(q => q.npc_id === npcData.value.id).length
    updateCurrentItem()
    rewardDisplay.value = []
    currentQuote.value = randomLine(npcData.value.flavor_lines) || "Квест взят. Удачи."

    const quest = activeQuest.value
    if (quest?.expires_at) {
      startCountdown(quest.expires_at)
    }

  } catch (e) {
    currentQuote.value = "Лимит квестов за сегодня исчерпан. Приходи завтра."
    console.error("❌ Ошибка принятия квеста:", e)
  }
}


onMounted(async () => {
  if (!questStore.npcs.length) await questStore.fetchNPCs()
  npcData.value = questStore.npcs.find(n => n.id === npcId)
  limit.value = npcData.value?.limit_per_day || 5

  await questStore.fetchActiveQuests()

  // 💥 важно дождаться обновления computed
  await nextTick()

  used.value = questStore.activeQuests.filter(q => q.npc_id === npcId).length

  if (hasActiveQuest.value) {
    updateCurrentItem()
    currentQuote.value = randomLine(npcData.value.flavor_lines) || npcData.value.quote || "..."

    const quest = activeQuest.value
    if (quest?.expires_at) {
      startCountdown(quest.expires_at)
    }

  } else {
    currentQuote.value = npcData.value?.quote || "..."
  }
})

</script>





<style scoped lang="scss">
.bubble-reward {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  color: #ffd700;
}

.reward-entry {
  display: flex;
  align-items: center;
  gap: 6px;

  .reward-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    object-fit: cover;
  }
}

.bubble-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;

  img.item-icon {
    width: 80px;
    height: 80px;
    object-fit: contain;
    border-radius: 6px;
    box-shadow: 0 0 6px rgba(0,0,0,0.4);
    z-index: 1;
  }

  .item-name {
    font-size: 14px;
    font-weight: bold;
    color: #fff;
    text-shadow: 0 0 3px #000;
  }
}

.npc-quest-wrapper {
  margin-top: 150px;
  width: 900px;
  height: 600px;
  padding: 30px;
  border-radius: 22px;
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.2);
  color: #fff;
}

.npc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;

  .back-button {
    background: transparent;
    width: 100px;
    border: 2px solid white;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    padding: 6px 12px;
    cursor: pointer;
    transition: 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  }

  .npc-name {
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 1px;
  }

  .npc-limit {
    font-size: 20px;
    opacity: 0.8;
  }
}

.npc-content {
  display: flex;
  gap: 40px;
  align-items: center;
  justify-content: center;

  .npc-image-block {
    flex-shrink: 0;

    .npc-image {
      width: 440px;
      height: auto;
      border-radius: 16px;
      object-fit: cover;
      border: 2px solid rgba(255, 255, 255, 0.2);
    }
  }

  .npc-bubble-block {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;

    .npc-speech-bubble {
      position: relative;
      padding: 60px;
      width: 300px;
      height: 100px;
      background: rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      font-size: 16px;
      line-height: 1.5;
      max-width: 400px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);

      &::before {
        content: "";
        position: absolute;
        left: -20px;
        top: 20px;
        width: 0;
        height: 0;
        border: 10px solid transparent;
        border-right-color: rgba(255, 255, 255, 0.12);
      }
    }

    .accept-button {
      padding: 10px 20px;
      background: transparent;
      border: 2px solid white;
      color: white;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
      transition: 0.2s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.15);
      }
    }
  }
}

@keyframes shake {
  0% { transform: translate(0); }
  25% { transform: translate(-4px, 2px); }
  50% { transform: translate(4px, -2px); }
  75% { transform: translate(-2px, 2px); }
  100% { transform: translate(0); }
}

.item-icon.shake {
  animation: shake 0.4s ease;
  box-shadow: 0 0 12px red;
}
</style>
