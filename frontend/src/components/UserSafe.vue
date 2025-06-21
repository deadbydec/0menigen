<template>
    <div class="personal-shop-wrap">
      <h2>Мой сейф</h2>
  
      <!-- Кнопки-вкладки -->
      <div class="buttons">
        <button @click="switchTab('all')">Все предметы</button>
        <button @click="switchTab('favorites')">Избранное</button>
      </div>
  
      <!-- Блок с балансом сейфа (монеты) -->
      <div class="cash-info">
        <p>Баланс сейфа: <strong>{{ vaultBalance }}</strong> монет</p>
        <div class="coin-actions">
          <div>
            <label>Внести монет:</label>
            <input type="number" v-model.number="coinsDeposit" min="1" />
            <button @click="depositCoins" class="ghost-button">Внести</button>
          </div>
          <div>
            <label>Вывести монет:</label>
            <input type="number" v-model.number="coinsWithdraw" min="1" />
            <button @click="withdrawCoins" class="ghost-button">Вывод</button>
          </div>
        </div>
      </div>
  
      <!-- Отображаем вкладку: все предметы -->
      <div v-if="showTab === 'all'">
        <div class="table-container" v-if="mergedVaultItems.length">
          <table class="shop-table">
            <thead>
              <tr>
                <th>Товар</th>
                <th>Кол-во</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in mergedVaultItems" :key="item.id">
                <td class="prod-cell">
                  <img
                    v-if="item.image"
                    :src="`${STATIC_BASE}/static/goods/${item.image || 'noimage.png'}`"
                    :alt="item.product_name"
                    @error="onImageError"
                    class="prod-image"
                  />
                  <span class="prod-name">{{ item.product_name }}</span>
                </td>
                <td>{{ item.quantity }}</td>
                <td class="actions-cell">
                  <!-- Звезда избранного -->
                  <button @click="toggleFavorite(item)" class="favorite-btn">
                    <span class="star-icon" :class="{ 'star-favorite': item.is_favorite }">
                      {{ item.is_favorite ? '★' : '☆' }}
                    </span>
                  </button>
                  <!-- Вернуть в инвентарь -->
                  <button @click="withdrawItem(item)"class="ghost-button">В инвентарь</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-items">
          <p>Сейф пуст или предметы не загружены.</p>
        </div>
      </div>
  
      <!-- Вкладка: избранные -->
      <div v-else-if="showTab === 'favorites'">
        <div class="table-container" v-if="computedFavoriteItems.length">
          <table class="shop-table">
            <thead>
              <tr>
                <th>Товар</th>
                <th>Кол-во</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in computedFavoriteItems" :key="item.id">
                <td class="prod-cell">
                  <img
                    v-if="item.image"
                    :src="`${STATIC_BASE}/static/goods/${item.image || 'noimage.png'}`"
                    :alt="item.product_name"
                    @error="onImageError"
                    class="prod-image"
                  />
                  <span class="prod-name">{{ item.product_name }}</span>
                </td>
                <td>{{ item.quantity }}</td>
                <td class="actions-cell">
                  <!-- Звезда избранного -->
                  <button @click="toggleFavorite(item)" class="favorite-btn">
                    <span class="star-icon" :class="{ 'star-favorite': item.is_favorite }">
                      {{ item.is_favorite ? '★' : '☆' }}
                    </span>
                  </button>
                  <!-- Вернуть в инвентарь -->
                  <button @click="withdrawItem(item)"class="ghost-button">В инвентарь</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-items">
          <p>Нет избранных предметов.</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import api from "@/utils/axios"
  import { usePlayerStore } from "@/store/player"
  import { useToastStore } from '@/store/toast'
  
  const toastStore = useToastStore()
  const playerStore = usePlayerStore()
  
  // Статическая база для изображений
  const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
  
  // Основные reactive-переменные
  const vaultItems = ref([])       // все предметы из сейфа
  const favoriteItems = ref([])    // избранные товары
  const vaultBalance = ref(0)      // баланс сейфа
  
  // Для вкладок
  const showTab = ref('all')
  
  // Для ввода монет
  const coinsDeposit = ref(1)
  const coinsWithdraw = ref(1)
  
  // CSRF токен
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
    return match ? match[2] : null
  }
  const csrfToken = getCookie("csrf_access_token")
  
  // ======================
  // ЛОГИКА ЗАГРУЗКИ
  // ======================
  onMounted(async () => {
    await loadVault()
    await loadFavorites()
  })
  
  async function loadVault() {
    try {
      const res = await api.get('/safe/vault')
      vaultBalance.value = res.data.vault_balance || 0
      vaultItems.value = res.data.vault_items || []
    } catch (err) {
      console.error('Ошибка загрузки сейфа:', err)
    }
  }
  
  async function loadFavorites() {
    try {
      const res = await api.get('/safe/vault/favorites')
      favoriteItems.value = res.data.favorites || []
    } catch (err) {
      console.error('Ошибка загрузки избранного:', err)
    }
  }
  
  // ======================
  // Вычисляемые свойства для объединения и фильтрации
  // ======================
  
  // Объединяем vaultItems и favoriteItems: для каждого item из сейфа проверяем, есть ли он в избранном 
  const mergedVaultItems = computed(() => {
    // Предполагаем, что для избранных в каждом элементе в favoriteItems есть product_id
    const favSet = new Set(favoriteItems.value.map(fav => fav.product_id))
    return vaultItems.value.map(item => ({
        ...item,
        is_favorite: favSet.has(item.product_id)
    }))
  })
  
  // Для вкладки "избранное" отбираем только те, где is_favorite true
  const computedFavoriteItems = computed(() =>
    mergedVaultItems.value.filter(item => item.is_favorite)
  )
  
  // ======================
  // Операции с товарами
  // ======================
  function onImageError(e) {
    e.target.src = `${STATIC_BASE}/static/goods/noimage.png`
  }
  
  async function withdrawItem(item) {
    try {
      const payload = {
        product_id: item.product_id,
        quantity: 1
      }
      const res = await api.post('/safe/vault/withdraw-item', payload)
      alert(res.data.message)
      if (showTab.value === 'favorites') {
        await loadFavorites()
      }
      await loadVault()
    } catch (error) {
      console.error('Ошибка при возврате:', error)
    }
  }
  
  const toggleFavorite = async (item) => {
    try {
      const res = await api.post('/safe/vault/favorite-toggle', {
        product_id: item.product_id
      }, {
        withCredentials: true,
        headers: { "X-CSRF-TOKEN": csrfToken }
      })
  
      toastStore.addToast(res.data.message, { type: 'success' })
      // После переключения обновляем данные
      await loadVault()
      await loadFavorites()
    } catch (err) {
      console.error("Ошибка избранного:", err)
      toastStore.addToast("Ошибка избранного", { type: 'error' })
    }
  }
  
  // ======================
  // Операции с монетами
  // ======================
  async function depositCoins() {
    if (coinsDeposit.value <= 0) {
      alert("Внесите положительное количество монет")
      return
    }
    try {
      const res = await api.post('/safe/vault/deposit-coins', {
        amount: coinsDeposit.value
      })
      alert(res.data.message)
      coinsDeposit.value = 1
      await loadVault()
      await playerStore.fetchPlayer()
    } catch (error) {
      console.error('Ошибка при внесении монет:', error)
    }
  }
  
  async function withdrawCoins() {
    if (coinsWithdraw.value <= 0) {
      alert("Укажите положительное количество монет")
      return
    }
    try {
      const res = await api.post('/safe/vault/withdraw-coins', {
        amount: coinsWithdraw.value
      })
      alert(res.data.message)
      coinsWithdraw.value = 1
      await loadVault()
      await playerStore.fetchPlayer()
    } catch (error) {
      console.error('Ошибка при выводе монет:', error)
    }
  }
  
  // Переключение вкладок
  function switchTab(tab) {
    showTab.value = tab
    if (tab === 'favorites') {
      loadFavorites()
    }
  }
  </script>
  
  <style scoped lang="scss">
  .personal-shop-wrap {
    border: 1px solid rgb(0, 0, 0);
    color: #fff;
    padding: 1rem;
    background:rgba(37, 26, 35, 0.651);
    backdrop-filter: blur(6px);
    border-radius: 8px;
    width: 850px;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.4);
  
    h2 {
      margin-bottom: 1rem;
      font-size: 1.5rem;
      letter-spacing: 0.5px;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.7);
    }
  
    .buttons {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
  
      button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #fff;
        padding: 0.5rem 1rem;
        cursor: pointer;
        border-radius: 4px;
        text-transform: uppercase;
        transition: background 0.2s ease;
  
        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      }
    }
  
    .cash-info {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 1rem;
      border-radius: 6px;
      margin-bottom: 1rem;
  
      .coin-actions {
        display: flex;
        gap: 1.5rem;
        margin-top: 0.5rem;
  
        div {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
  
        input[type="number"] {
          width: 70px;
          background-color: rgba(0, 0, 0, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #fff;
          padding: 2px 4px;
          border-radius: 4px;
  
          &:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.4);
          }
        }
      }
    }
  
    .table-container {
      overflow-x: auto;
    }
  
    .shop-table {
      width: 100%;
      border-collapse: collapse;
      background-color: rgba(255, 255, 255, 0.06);
  
      thead {
        background-color: rgba(255, 255, 255, 0.2);
      }
  
      th,
      td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        text-align: left;
      }
  
      th {
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
      }
  
      tbody tr:hover {
        background-color: rgba(255, 255, 255, 0.08);
      }
    }
  
    .actions-cell {
      display: flex;
      gap: 0.5rem;
      align-items: center;
  
      .favorite-btn {
        border: none;
        background: none;
        cursor: pointer;
        padding: 0;
        display: flex;
        align-items: center;
      }
    }
  
    .prod-cell {
      display: flex;
      align-items: center;
      gap: 0.5rem;
  
      .prod-image {
        width: 60px;
        height: auto;
        object-fit: cover;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 6px rgba(0, 0, 0, 0.5);
      }
  
      .prod-name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 160px;
      }
    }
  
    .no-items {
      background-color: rgba(255, 255, 255, 0.1);
      padding: 1rem;
      border-radius: 4px;
      text-align: center;
      font-style: italic;
    }
  }
  
  /* Иконка звезды */
  .star-icon {
    font-size: 1.2rem;
    color: #999; /* По умолчанию серая */
  }
  
  /* Если предмет в избранном */
  .star-favorite {
    color: #ffc107; /* Жёлтый */
  }

  .ghost-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 4px;
  text-transform: uppercase;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}

  </style>
  
  
  