
<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue"
import { useRoute } from "vue-router"
import { useShopStore } from "@/store/shop"
const shopImage = computed(() => `/images/shops/${localCategory.value}.png`)
import coinIcon from "@/assets/icons/coin.png";
// props
const props = defineProps({ category: String })

// ✅ Локальная переменная, чтобы избежать readonly ошибок
const localCategory = ref(props.category)


// 1) Константы для отображения категорий и слоганов
const displayNames = {
  food: "Гастрономий",
  books: "Свитки Забытой Логики",
  collectioner: "Артефактный Базар",
  drugs: "Фармаглюк",
  tech: "Техстор",
  zoo: "Вивариум",
  cosmetic: "Космошоп"
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


//const wrapperMarginTop = computed(() => {
//  const count = shopItems.value.filter(item =>
//    allowedTypesMap[localCategory.value]?.includes(item.product_type)
//  ).length

//  if (count > 75) return "3300px"
//  if (count > 70) return "3100px"
//  if (count > 65) return "2900px"
//  if (count > 60) return "2700px"
//  if (count > 55) return "2500px"
//  if (count > 50) return "2300px"
//  if (count > 45) return "2100px"
//  if (count > 40) return "1900px"
//  if (count > 35) return "1700px"
//  if (count > 30) return "1500px"
//  if (count > 25) return "1300px"
//  if (count > 20) return "1100px"
//  if (count > 15) return "900px"
//  if (count > 10) return "700px"
//  if (count > 5) return "500px"
//  return "100px" // 🔥 Когда товаров мало — увеличиваем отступ, но НЕ через padding
//})


// 7) Lifecycle hooks
onMounted(() => {
  shopStore.connectSocket()
  shopStore.fetchShopItems(localCategory.value)

  // каждые 10 сек авто-refresh
  setInterval(() => {
    document.querySelector('.refresh-button')?.click()
 }, 20000)
})

// при изменении товаров — плавно перерендериваем


</script>


<template>
  <div class="page-inner">
    <div class="shop-wrapper" :style="{ marginTop: wrapperMarginTop }">
      <div ref="scrollAnchor"></div>

      <h1 :style="{ marginTop }">{{ displayCategoryName }}</h1>

      <img
        :src="shopImage"
        class="shop-banner"
        alt="Баннер магазина"
      />

      <h2 class="slogan">{{ randomSlogan }}</h2>

      <div class="shop-scroll-area">
        <div class="shop-grid" :class="{ pulse: wasUpdated }" :key="Date.now()">
          <div
            v-for="item in shopItems.filter(item => allowedTypesMap[category]?.includes(item.product_type))"
            :key="item.id + '-' + item.stock"
            class="shop-slot"
          >
            <!-- 📦 КАРТОЧКА ТОВАРА -->
            <img
              :src="`https://localhost:5002/static/goods/${item.image}`"
              :alt="item.name"
              @click="handleBuy(item)"
              :class="{ disabled: item.stock <= 0 }"
            />

            <!-- 🏷️ ТЕКСТ ПОД КАРТОЧКОЙ -->
            <div class="item-caption">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-price">
                Цена: {{ item.price }}
                <img :src="coinIcon" alt="💰" class="emoji-icon" style="width: 1.2em; height: 1.2em;" />
              </div>
              <div class="item-stock">В стоке: {{ item.stock }}</div>
              <div class="product-tooltip">{{ item.description }}</div>
            </div>
          </div>

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
      style="visibility: hidden; height: 0; width: 0;"
    >
      Обновить магазин
    </button>
  </div>
</template>




<style lang="scss">

.item-caption {
  margin-top: 8px;
  color: #ddd;
  font-size: 13px;
  text-align: center;

  .item-name {
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 4px;
    color: #fafafa;
  }

  .item-price,
  .item-stock {
    font-size: 12px;
    margin-bottom: 3px;
    color: #aaa;
  }

  .product-tooltip {
    font-size: 11px;
    color: #888;
    margin-top: 4px;
    word-wrap: break-word;
  }
}

.emoji-icon {
  width: 2.0em;
  height: 2.0em;
  vertical-align: -0.2em;
  margin-right: 4px;
  display: inline-block;
}

.shop-banner {
  max-width: 50%;       
  height: auto;         
  object-fit: contain;  
  border-radius: 20px;
  border: 1px solid rgb(196, 196, 196);
  box-shadow: 8 8px 12px rgba(0, 0, 0, 0.4);
  display: block;
  margin: 4px auto;
}

.shop-wrapper {
  background: #142752e7;
  border: 1px solid rgb(196, 196, 196);
  max-width: 1300px;
  padding: 0px 20px 20px;
  border-radius: 22px;
  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
}

h2.slogan {
  margin: 25px 0px 25px;
  font-size: 14px;
  font-weight: normal;
  text-align: center;
  font-size: 0.8em;
  color: #cccccc;
  font-style: italic;
  text-shadow: 
    0 0 3px rgba(255, 255, 255, 0.678);
}

/* Заголовок можно чуть уменьшить ещё, если нужно */
h1 {
  margin: 30px 20px 30px;
  font-size: 24px;
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 14px;
  border-radius: 12px;
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
}

/* Сетка товаров */
.shop-grid {
  display: grid;
  width: 800px;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.5rem;
  justify-content: center;
}


/* Карточка товара */
.shop-slot {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid #555;
  border-radius: 14px;
  padding: 8px;
  text-align: center;
  position: relative;

  img {
    width: 100px;
    height: 100px;
    object-fit: contain;
    cursor: pointer;
    transition: transform 0.3s ease;

    &.disabled {
      opacity: 0.4;
      pointer-events: none;
    }

    &:hover {
      transform: scale(1.05);
    }
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
.rarity-common { color: #215b79; }
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

  
