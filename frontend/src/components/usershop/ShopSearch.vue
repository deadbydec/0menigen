<template>
  <div class="search-shop-wrap">
    <h2>Поиск товаров</h2>

    <div class="search-bar">
      <input
        v-model="query"
        @input="onSearch"
        placeholder="Введите название товара..."
      />
    </div>

    <!-- РЕЗУЛЬТАТЫ -->
    <div class="results" v-if="searchResults.length">
      <h3>Результаты:</h3>
      <ul>
        <li v-for="item in searchResults" :key="item.id" class="result-item">
          <div class="item-info">
            <img 
  :src="`${STATIC_BASE}/static/goods/${item.image || 'noimage.png'}`" 
  :alt="item.product_name"
  @error="onImageError"
  class="item-img"
/>



            <div class="text-block">
              <strong class="item-name">{{ item.product_name }}</strong>
              <p class="item-details">
                Продавец: {{ item.seller }}<br />
                Цена: {{ item.price }}<br />
                Кол-во: {{ item.quantity }}
              </p>
            </div>
          </div>


          <button class="buy-btn" @click="buyItem(item)">Купить</button>

        </li>
      </ul>
    </div>

    <!-- ПУСТО: либо нет результатов, либо пустой запрос -->
    <div class="no-results" v-else>
      <p>Нет результатов для "{{ query }}".</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from "@/utils/axios";

const query = ref('')
const searchResults = ref([])
const STATIC_BASE = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
let timeout = null


function onImageError(e) {
  e.target.src = `${STATIC_BASE}/static/goods/noimage.png`
}
function onSearch() {
  // Дебаунс 300мс
  clearTimeout(timeout)
  timeout = setTimeout(async () => {
    // Если строка короче 2 символов, не ищем
    if (query.value.trim().length < 2) {
      searchResults.value = []
      return
    }
    try {
      // Кодируем запрос (пробелы, спецсимволы)
      const encoded = encodeURIComponent(query.value)
      const res = await api.get(`/playershop/search?query=${encoded}`)
      searchResults.value = (res.data.results || []).filter(item => item.quantity > 0)
    } catch (error) {
      console.error('Ошибка при поиске:', error)
      searchResults.value = []
    }
  }, 300)
}



async function buyItem(item) {
  try {
    const res = await api.post('/playershop/buy', { shop_item_id: item.id })
    alert('Товар куплен!')
    // Обновить список или обработать
  } catch (error) {
    console.error('Ошибка покупки:', error)
  }
}

</script>

<style scoped lang="scss">
.search-shop-wrap {
  border: 1px solid rgb(0, 0, 0);
  color: #fff;
  padding: 1rem;
  background-color: rgba(0, 0, 0, 0.4); // полупрозрачный фон
  backdrop-filter: blur(6px);          // лёгкий блёр
  border-radius: 8px;
  width: 600px;
  max-width:600px;
  margin: 0 auto;
  box-shadow: 0 0 15px rgba(0,0,0,0.4);

  h2 {
    margin-bottom: 1rem;
    font-size: 1.4rem;
    text-shadow: 0 1px 2px rgba(0,0,0,0.7);
  }

  .search-bar {
    margin-bottom: 1rem;
    input {
      width: 280px;
      max-width: 300px;
      padding: 0.6rem 1rem;
      border: 1px solid rgba(255,255,255,0.2);
      background-color: rgba(255,255,255,0.1);
      color: #fff;
      border-radius: 4px;
      transition: border-color 0.2s ease;

      &:focus {
        outline: none;
        border-color: rgba(255,255,255,0.4);
        background-color: rgba(255,255,255,0.15);
      }
    }
  }

  .results {
    background-color: rgba(255, 255, 255, 0.06);
    padding: 1rem;
    border-radius: 6px;
    box-shadow: inset 0 0 6px rgba(0,0,0,0.4);

    h3 {
      margin-bottom: 0.5rem;
      font-size: 1.2rem;
    }

    ul {
      list-style: none;
      margin: 0;
      padding: 0;

      .result-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.5rem 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);

        &:hover {
          background-color: transparent;
        }

        .item-info {
          display: flex;
          gap: 0.8rem;
          align-items: center;

          .item-img {
            width: 60px;
            height: auto;
            object-fit: cover;
            border-radius: 4px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 0 6px rgba(0,0,0,0.5);
          }

          .text-block {
            .item-name {
              font-size: 1rem;
              margin-bottom: 4px;
            }
            .item-details {
              font-size: 0.85rem;
              line-height: 1.4;
              opacity: 0.8;
            }
          }
        }

        .buy-btn {
          margin-left: auto;
          max-width: 100px;
          background-color: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.2);
          padding: 0.4rem 0.8rem;
          color: #fff;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.2s ease;
          &:hover {
            background-color: rgba(255,255,255,0.2);
          }
        }
      }
    }
  }

  .no-results {
    background-color: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 4px;
    text-align: center;
    font-style: italic;
  }
}
</style>


  