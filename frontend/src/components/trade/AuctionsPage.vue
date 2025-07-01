<template>
  <div class="auctions-wrapper">
    <!-- 📌 фиксированный мини-блок -->
    <div class="fixed-sidebar">
      <div class="sidebar-card">
        <h2>Фильтры</h2>
        <button class="sidebar-button">Мои лоты</button>
        <button class="sidebar-button">Питомцы</button>
        <button class="sidebar-button">Предметы</button>
        <button class="sidebar-button" @click="showModal = true">Создать лот</button>
      </div>
    </div>

    <div class="auctions-page">
      <h1 class="title">Аукционы</h1>

      <div v-if="loading" class="loading">Загрузка...</div>
      <div v-else>
        <div v-if="lots.length === 0" class="empty">Пока нет лотов.</div>

        <div class="lot-list">
          <div v-for="lot in sortedLots" :key="lot.id" class="lot-card">
            <div class="lot-header">
              <span class="lot-type">{{ lot.item_type.toUpperCase() }}</span>
              <span class="lot-currency">{{ lot.currency === 'coins' ? '🪙' : '💠' }}</span>
            </div>

            <!-- 👤 имя владельца -->
            <p class="owner">Продавец: {{ lot.owner_name }}</p>

            <div class="lot-body">
              <!-- 🖼️ картинка -->
              <img v-if="lot.image" :src="lot.image" alt="item" class="lot-image" />
              <!-- 🧩 имя предмета/питомца -->
              <p class="lot-name">{{ lot.name }}</p>
              <p>
  {{ lot.current_bid ? `Текущая ставка: ${lot.current_bid} от ${lot.highest_bidder_name || '??'}` : `Ставок пока нет (от ${lot.starting_price})` }}
</p>

              <p class="expires">Истекает: {{ formatDate(lot.expires_at) }}</p>
            </div>

            <!-- 💸 поле ввода и кнопка -->
            <!-- 💸 поле ввода и кнопка -->
<div v-if="store.currentUserId !== lot.owner_id" class="bid-section">
  <input
  v-model.number="bids[lot.id]"
  :placeholder="getDefaultBid(lot)"
  class="bid-input"
  type="number"
/>

  <button class="action-button" @click="placeBid(lot)">
    Сделать ставку
  </button>
</div>

          </div>
        </div>
      </div>
    </div>

    <AuctModal v-if="showModal" @close="showModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuctionStore } from '@/store/auction'
import { usePlayerStore } from '@/store/player' // 👈 не забудь импорт!
import AuctModal from '@/components/trade/AuctModal.vue'

const store = useAuctionStore()
const playerStore = usePlayerStore()
const showModal = ref(false)
const bids = ref({}) // 🔥 ключ: lot.id, значение: ставка игрока
const base = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

const getDefaultBid = (lot) => {
  const baseBid = Math.max(lot.current_bid || 0, lot.starting_price)
  return baseBid + 500
}


// 💡 реактивный доступ к лотам из стора
const lots = computed(() =>
  store.lots.map(lot => ({
    ...lot,
    image: lot.image ? `${base}${lot.image}` : null
  }))
)

const sortedLots = computed(() =>
  [...lots.value].sort((a, b) => new Date(b.expires_at) - new Date(a.expires_at))
)

onMounted(async () => {
  await store.refreshAllLots()
})

const formatDate = (iso) => {
  const date = new Date(iso)
  return date.toLocaleString()
}

const placeBid = async (lot) => {
  const bidValue = bids.value[lot.id]
  if (!bidValue || bidValue < lot.starting_price) {
    alert(`Ставка должна быть не ниже минимальной: ${lot.starting_price}`)
    return
  }

  try {
    await store.placeBid(lot.id, bidValue)
    await store.refreshAllLots()      // ⏎ обновили лоты
    await playerStore.fetchMe()       // 💰 обновили баланс
    alert('Ставка отправлена!')       // ✅ после обновлений

    bids.value[lot.id] = null
  } catch (err) {
    alert('Ошибка при отправке ставки')
    console.error(err)
    window.__vova?.show?.() // 💀 если хочешь добавить драму
  }
}
</script>



<style lang="css">

.lot-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

.auctions-wrapper {
  display: flex;
  gap: 24px;
  color: rgb(196, 196, 196);
  padding: 24px;
}

.fixed-sidebar {
  position: fixed;
  top: 205px;
  left: 530px;
  height: fit-content;
  width: 200px;
}

.sidebar-card {
  background: #181818e7;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 18px;
  padding: 16px;
}

.sidebar-card h2 {
  font-size: 18px;
  margin-bottom: 12px;
}

.sidebar-button {
  width: 100%;
  margin-bottom: 8px;
  padding: 8px;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 18px;
  background: linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  color: rgb(196, 196, 196);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  width: 150px;
  justify-content: center;
  align-items: center;
}

.auctions-page {
  flex: 1;
}

.auctions-page {
  padding: 24px;
  background: #181818e7;
  color: rgb(196, 196, 196);
  margin-top: 160px;
  min-height: 100vh;
  width: 550px;
  border: 1px solid rgb(196, 196, 196);
  font-family: sans-serif;
  border-radius: 22px;
}

.title {
  font-size: 28px;
  margin-bottom: 20px;
  color: rgb(196, 196, 196);
}

.loading,
.empty {
  text-align: center;
  font-size: 18px;
  margin-top: 30px;
  color: rgb(196, 196, 196);
}

.lot-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lot-card {
  border: 1px solid rgb(196, 196, 196);
  border-radius: 18px;
  padding: 16px;
  background: #202020c7;
  transition: transform 0.2s;
}

.lot-card:hover {
  transform: scale(1.01);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  margin-bottom: 8px;
}

.lot-type {
  text-transform: uppercase;
  letter-spacing: 1px;
}

.lot-body p {
  margin: 4px 0;
  font-size: 15px;
}

.expires {
  font-style: italic;
  font-size: 13px;
  opacity: 0.8;
}

.action-button {
  margin-top: 10px;
  padding: 8px 14px;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 12px;
  background: linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  color: rgb(196, 196, 196);
  font-weight: 600;
  cursor: pointer;
}
</style>
