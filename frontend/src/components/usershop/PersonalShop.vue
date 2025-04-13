<template>
  <div class="personal-shop-wrap">
    <h2>Мой магазин</h2>

    <!-- Кнопки зависят от режима showTransactions -->
    <div class="buttons">
      <template v-if="!showTransactions">
        <!-- Кнопки для режима "Магазин" -->
        <button @click="fetchAllItems">Обновить список</button>
        <button @click="saveShopChanges">Сохранить</button>
        <button @click="publishShop">Опубликовать</button>
        <button @click="toggleTransactions">Касса</button>
      </template>
      <template v-else>
        <!-- Кнопки для режима "Касса" -->
        <button @click="withdrawMoney">Вывести монеты</button>
        <button @click="toggleTransactions">Мой магазин</button>
      </template>
    </div>

    <!-- Режим "Магазин" -->
    <div v-if="!showTransactions">
      <div class="table-container" v-if="allItems.length">
        <table class="shop-table">
          <thead>
            <tr>
              <th>Товар</th>
              <th>В инвентаре</th>
              <th>В магазине</th>
              <th>Цена</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in allItems" :key="item.product_id">
              <td class="prod-cell">
                <img 
  :src="`${STATIC_BASE}/static/goods/${item.image || 'noimage.png'}`" 
  :alt="item.product_name"
  @error="onImageError"
  class="prod-image"
/>
                <span class="prod-name">{{ item.product_name }}</span>
              </td>
              <td>{{ item.quantity_in_inventory }}</td>
              <td>
                <input
                  type="number"
                  v-model.number="item.quantity_in_shop"
                  min="0"
                  :max="item.quantity_in_shop + item.quantity_in_inventory"
                />
              </td>
              <td>
                <input
                  type="number"
                  min="0"
                  v-model.number="item.price_in_shop"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-items">
        <p>Нет предметов для отображения.</p>
      </div>
    </div>

    <!-- Режим "Касса" -->
    <div v-else>
      <h3>Касса</h3>

      <div class="cash-info">
        <p>Баланс в кассе: <strong>{{ shopBalance }}</strong> монет</p>
      </div>

      <div v-if="transactions.length" class="table-container">
        <table class="shop-table">
          <thead>
            <tr>
              <th>Товар</th>
              <th>Кол-во</th>
              <th>Сумма</th>
              <th>Покупатель</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trn in transactions" :key="trn.id">
              <td>{{ trn.product_name }}</td>
              <td>{{ trn.quantity }}</td>
              <td>{{ trn.total_price }}</td>
              <td>{{ trn.buyer_username }}</td>
              <td>{{ formatDate(trn.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="no-items">
        <p>У вас пока нет продаж.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from "@/utils/axios"

const allItems = ref([])
const showTransactions = ref(false) // режим: магазин (false) или касса (true)

// список транзакций
const transactions = ref([])
const shopBalance = ref(0) // баланс в кассе
const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

// ======================
// ЛОГИКА ТОВАРОВ
// ======================
async function fetchAllItems() {
  try {
    const res = await api.get('/playershop/my/all-items')
    allItems.value = (res.data.all_items || []).filter(item =>
  item.quantity_in_inventory > 0 || item.quantity_in_shop > 0
)

  } catch (error) {
    console.error("Ошибка загрузки:", error)
  }
}

async function saveShopChanges() {
  try {
    const payload = allItems.value.map(item => ({
      product_id: item.product_id,
      quantity_in_inventory: item.quantity_in_inventory,
      price_in_shop: item.price_in_shop,
      quantity_in_shop: item.quantity_in_shop
    }))
    const res = await api.post('/playershop/my/save', payload)
    alert(res.data.message)
    await fetchAllItems()
  } catch (error) {
    console.error("Ошибка сохранения:", error)
    if (error.response?.data?.detail) {
      alert(error.response.data.detail)
    }
  }
}

async function publishShop() {
  try {
    const res = await api.post('/playershop/publish')
    alert(res.data.message)
  } catch (error) {
    console.error('Ошибка при публикации:', error)
  }
}

// ======================
// ЛОГИКА КАССЫ
// ======================

async function toggleTransactions() {
  showTransactions.value = !showTransactions.value
  if (showTransactions.value) {
    // При включении "Касса" загружаем
    await fetchTransactions()
    await fetchBalance()
  }
}

async function fetchTransactions() {
  try {
    const res = await api.get('/playershop/my/transactions')
    transactions.value = res.data.transactions || []
  } catch (error) {
    console.error("Ошибка транзакций:", error)
  }
}

async function fetchBalance() {
  // допустим твой эндпоинт профиля /api/profile/me возвращает shop_balance
  try {
    const res = await api.get('/playershop/my/balance')
    shopBalance.value = res.data.shop_balance
  } catch (error) {
    console.error("Ошибка получения баланса:", error)
  }
}

async function withdrawMoney() {
  try {
    const res = await api.post('/playershop/withdraw')
    alert(res.data.message)
    await fetchBalance()
  } catch (error) {
    console.error("Ошибка вывода монет:", error)
    if (error.response && error.response.data.detail) {
      alert(error.response.data.detail)
    }
  }
}

// ======================
// Утил: форматируем дату
// ======================
function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

onMounted(fetchAllItems)
</script>

<style scoped lang="scss">
.personal-shop-wrap {
  border: 1px solid rgb(0, 0, 0);
  color: #fff;
  padding: 1rem;
  background-color: rgba(0, 0, 0, 0.4);  
  backdrop-filter: blur(6px);
  border-radius: 8px;
  width: 850px;
  max-width: 900px;
  margin: 0 auto;
  box-shadow: 0 0 15px rgba(0,0,0,0.4);

  h2 {
    margin-bottom: 1rem;
    font-size: 1.5rem;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 2px rgba(0,0,0,0.7);
  }

  .buttons {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;

    button {
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 0.5rem 1rem;
      cursor: pointer;
      border-radius: 4px;
      text-transform: uppercase;
      transition: background 0.2s ease;

      &:hover {
        background: rgba(255,255,255,0.2);
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

    th, td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid rgba(255,255,255,0.1);
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

    input[type="number"] {
      width: 60px;
      background-color: rgba(0,0,0,0.2);
      border: 1px solid rgba(255,255,255,0.2);
      color: #fff;
      padding: 2px 4px;
      border-radius: 4px;

      &:focus {
        outline: none;
        border-color: rgba(255,255,255,0.4);
      }
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
      border: 1px solid rgba(255,255,255,0.2);
      box-shadow: 0 0 6px rgba(0,0,0,0.5);
    }

    .prod-name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 160px;
    }
  }

  .no-items {
    background-color: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 4px;
    text-align: center;
    font-style: italic;
  }

  .cash-info {
    margin-bottom: 1rem;
  }
}
</style>



  