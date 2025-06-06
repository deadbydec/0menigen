<template>
  <div class="shop-wrapper">
    <div class="shop-page">
      <h1>{{ displayCategoryName }}</h1>
      <h2 class="slogan">{{ randomSlogan }}</h2>

      <!-- Сетка существует всегда, принудительный перерендеринг через ключ (на всякий случай) -->
      <div class="shop-grid" :class="{ pulse: wasUpdated }" :key="Date.now()">
        <!-- Скрытая кнопка для обновления магазина -->
        

        <!-- Показываем товары: фильтрация происходит прямо в v-for -->
        <div
          v-for="item in shopItems.filter(item => allowedTypesMap[category]?.includes(item.product_type))"
          :key="item.id + '-' + item.stock"
          class="shop-slot"
        >
          <img
            :src="`https://localhost:5002/static/goods/${item.image}`"
            :alt="item.name"
            @click="handleBuy(item)"
            :class="{ disabled: item.stock <= 0 }"
          />
          <div class="item-name">{{ item.name }}</div>
          <div class="item-rarity" :class="getRarityClass(item.rarity)">
            {{ item.rarity }}
          </div>
          <div class="item-price">Цена: {{ item.price }} монет</div>
          <div class="item-stock">В наличии: {{ item.stock }}</div>
          <div class="product-tooltip">
            {{ item.description }}
          </div>
        </div>

        <!-- Заглушка при отсутствии товаров -->
        <p
          v-if="shopItems.filter(item => allowedTypesMap[category]?.includes(item.product_type)).length === 0"
          class="empty-shop-message"
          style="grid-column: 1 / -1; text-align: center; font-size: 14px; color: #555;"
        >
          Товаров нет или идёт загрузка...
        </p>
      </div>
    </div>
  </div>

<button 
          @click="handleRefresh" 
          class="refresh-button"
          style="visibility: hidden; height: 0; width: 0;">
          Обновить магазин
        </button>

</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue"
import { useRoute } from "vue-router"
import { useShopStore } from "@/store/shop"

// props
const props = defineProps({ category: String })

// ✅ Локальная переменная, чтобы избежать readonly ошибок
const localCategory = ref(props.category)

// 1) Константы для отображения категорий и слоганов
const displayNames = {
  food: "Кормушка для Багнутых",
  books: "Свитки Забытой Логики",
  collectioner: "Артефактный Базар",
  drugs: "ФармаГлюк",
  tech: "ЦифроХлам",
  zoo: "Вивариум",
  cosmetic: "КосмоШоп"
}

const slogans = [
  "Каждый третий покупатель не помнит, зачем пришёл. Мы не осуждаем.",
  "Сделано из органики, глюков и частичек воспоминаний о бывшем.",
  "Пельмени, которые кричат, когда ты их ешь. Удовольствие — спорное.",
  "Говорят, если съесть три товара отсюда — ты увидишь Омнита во сне.",
  "Никто не проверял состав. Даже разработчики. Особенно разработчики.",
  "Откуси от реальности. Мы положили её в упаковку.",
  "На 87% состоят из кода и на 13% — из грусти.",
  "Данный продукт сертифицирован Федерацией Ментальных Ошибок.",
  "Некоторые товары появились здесь ещё до запуска симуляции.",
  "Мы не гарантируем безопасность. Но ты ведь не за этим пришёл, верно?",
  "Пробуй. Или не пробуй. Но они всё равно окажутся в твоём инвентаре.",
  "Разрешено к продаже в трёх измерениях и одном туалете."
]

// 2) Карта разрешённых типов для каждой категории
const allowedTypesMap = {
  food: ["еда", "напиток", "сладость"],
  books: ["книга"],
  collectioner: ["коллекционный", "сувенир", "игрушка", "наклейка"],
  drugs: ["аптека"],
  tech: ["гаджет"],
  zoo: ["существо"],
  cosmetic: ["косметический"]
}

// 3) Реактивный доступ к роуту и стору
const route = useRoute()
const category = computed(() => route.params.category || "")
const shopStore = useShopStore()

// Следим за props.category и обновляем localCategory
watch(() => props.category, (newVal) => {
  localCategory.value = newVal
  shopStore.fetchShopItems(newVal)
})

// 4) Реактивные ссылки на данные стора
const shopItems = computed(() => shopStore.shopItems)
const wasUpdated = ref(false)

// 5) Локальные computed значения
const displayCategoryName = computed(() => displayNames[localCategory.value] || "🌀 Магазин Пустоты")
const randomSlogan = computed(() => slogans[Math.floor(Math.random() * slogans.length)])

// 6) Методы для покупки и обновления
function handleBuy(item) {
  shopStore.buyProduct(item.id, item.name, localCategory.value)
}

function handleRefresh() {
  shopStore.fetchShopItems(localCategory.value)
}

// Раскраска редкости товара
function getRarityClass(rarity) {
  if (!rarity) return ""
  const r = rarity.trim().toLowerCase()
  switch (r) {
    case "обычный":     return "rarity-common"
    case "мусорный":    return "rarity-trash"
    case "редкий":      return "rarity-rare"
    case "эпический":   return "rarity-epic"
    case "легендарный": return "rarity-legendary"
    case "древний":     return "rarity-elder"
    default: return ""
  }
}

// 7) Lifecycle hooks
onMounted(() => {
  shopStore.connectSocket()
  shopStore.fetchShopItems(localCategory.value)

  // каждые 10 сек авто-refresh
  //setInterval(() => {
  //  document.querySelector('.refresh-button')?.click()
 // }, 10000)
})

// при изменении товаров — плавно перерендериваем
watch(shopItems, async () => {
  console.log("📦 Товары изменились, возможно обновление!")
  await nextTick(() => {
    wasUpdated.value = Date.now()
  })
})
</script>






<style scoped lang="scss">

.shop-wrapper {
  background:rgba(38, 32, 39, 0.48);
  overflow-y: auto;
  border: 1px solid rgb(36, 35, 37);
  margin: 0 auto;
  padding: 10px;
  border-radius: 17px;

  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;

  /* Скрываем скроллбар, но сохраняем прокрутку */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE и Edge */

  &::-webkit-scrollbar {
    display: none; /* Chrome, Safari */
  }
}


h2 {
  color:  #2e2929d2;
  font-family: 'JetBrains Mono', monospace;
  font-size: medium;

}

h1 {
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 14px;

  border-radius: 12px;
  display: inline-block;


  font-family: 'JetBrains Mono', monospace;
}

body {
  overflow-y: scroll;
  height: 100vh;
}

html {
  scroll-behavior: smooth;
}

/* Убираем дефолтные стили */
html, body {
  margin: 0;
  padding: 0;

  font-family: 'JetBrains Mono', monospace;
}

/* Контейнер магазина */
.shop-page {
  /* Снимаем лишние отступы, ставим масштаб 80% */
  margin: 0 auto;
  padding: 10px;
  transform: scale(0.8);
  
  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
}

/* Заголовок можно чуть уменьшить ещё, если нужно */
.shop-page h1 {
  margin: 0 0 15px;
  font-size: 24px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

/* Сетка товаров */
.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  max-width: 1000px;
  margin: 0 auto; /* Чтобы сетка центрировалась */
}

/* Карточка товара */
.shop-slot {
  will-change: transform;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px;
  border: 1px solid #2e2c2c;
  border-radius: 9px;
  background:linear-gradient(80deg, #cfcdceb2,rgba(197, 228, 226, 0.664));
  transition: transform 0.2s;
  text-align: center;
  overflow: hidden;

  &:hover {
    transform: scale(1.05);
  }

  img {
    width: 110px;
    height: 110px;
    object-fit: contain;
    margin-bottom: 3px;
    cursor: pointer;
  }

  /* Если нет в наличии */
  & .disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

/* Название */
.item-name {
  margin: 2px 0;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  color: #1d1919e7;
  max-width: 90%;
  word-break: break-word;
}

/* Редкость */
.item-rarity {
  margin: 2px 0;
  font-size: 12px;
  line-height: 1.2;
  font-weight: bold;
  max-width: 90%;
  word-break: break-word;
  background-color: transparent;
  border: none;
}

/* Цена и сток */
.item-price,
.item-stock {
  margin: 2px 0;
  font-size: 11px;
  line-height: 1.2;
  color: #333;
  max-width: 90%;
  word-break: break-word;
}

/* Расцветки по редкости */
.rarity-trash { color: #585858; }
.rarity-common { color: #284c5e; }
.rarity-rare { color: #278f3d; }
.rarity-epic { color: #8325ee; }
.rarity-legendary { color: rgb(230, 158, 24); }
.rarity-elder { color: rgb(143, 36, 17); }
/* и т. д. */

/* Подсказка (описание) */
.product-tooltip {
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px;
  border-radius: 8px;
  text-align: center;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  pointer-events: none;
  z-index: 10;
}

.shop-slot:hover .product-tooltip {
  opacity: 1;
}

/* Эффект пульса при обновлении */

</style>

  
