<template>
  <div class="page-inner">
  <div class="shop-wrapper">
    <div class="shop-page">
      <h1>Свалка</h1>
      <img
      :src="landfillImage"
      class="shop-banner"
      alt="Баннер магазина"
    />
      <h2 class="slogan">Где баги отдыхают, а мусор готовит революцию.</h2>
      <p class="daily-limit">
        Подобрано со свалки: {{ landfill.limitInfo.used }} / {{ landfill.limitInfo.max }}
      </p>

      <div class="shop-scroll-area">
        <div class="shop-grid">
          <div
            v-for="item in landfill.landfillItems"
            :key="item.id"
            class="shop-slot"
            @click="openModal(item)"
          >
            <img :src="`https://localhost:5002/static/goods/${item.image}`" :alt="item.name" />
            <div class="item-name">{{ item.name }}</div>
            <div class="item-rarity" :class="getRarityClass(item.rarity)">
              {{ item.rarity }}
            </div>
            <div class="product-tooltip">{{ item.description }}</div>
          </div>

          <p v-if="landfill.landfillItems.length === 0" class="empty-shop-message">
            Пока что на свалке пусто... но баги не дремлют.
          </p>
        </div>
      </div>
    </div>
  </div></div>

  <!-- 🌑 Модалка подбора предмета -->
  <Teleport to="body">
    <LandfillPickupModal
      :visible="showModal"
      :item="selectedItem"
      @close="closeModal"
    />
  </Teleport>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useLandfillStore } from '@/store/landfill'
import LandfillPickupModal from './LandfillPickupModal.vue'

const landfill = useLandfillStore()
const selectedItem = ref(null)
const showModal = ref(false)

const landfillImage = '/images/landfill118.png'  // или путь куда ты положил баннер


function openModal(item) {
  selectedItem.value = item
  showModal.value = true
}

function closeModal() {
  selectedItem.value = null
  showModal.value = false
}

function getRarityClass(rarity) {
  if (!rarity) return ''
  const r = rarity.trim().toLowerCase()
  switch (r) {
    case 'обычный': return 'rarity-common'
    case 'мусорный': return 'rarity-trash'
    case 'редкий': return 'rarity-rare'
    case 'эпический': return 'rarity-epic'
    case 'легендарный': return 'rarity-legendary'
    case 'древний': return 'rarity-elder'
    default: return ''
  }
}

onMounted(() => {
  landfill.fetchItems()
  landfill.fetchLimit()
})
</script>


<style scoped lang="scss">


.shop-banner {
  background: url('/images/landfill118.png');
  max-width: 50%;       
  height: auto;         
  object-fit: contain;  
  border-radius: 20px;
  display: block;
  margin: 4px auto;
}

.daily-limit {
  font-size: 13px;
  margin-bottom: 12px;
  color: #ddd;
}


.shop-scroll-area {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px;
  margin-top: 10px;
}

.shop-wrapper {
  background: #181818e7;
  overflow-y: auto;
  border: 1px solid rgb(196, 196, 196);
  margin: 0 auto;
  max-width: 1000px;
  min-height: 100vh;
  padding-top: 80px;
  padding: 0px;
  border-radius: 22px;
  transform-origin: top center;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  scrollbar-width: none;
  -ms-overflow-style: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

.shop-page {
  margin: 0 auto;
  padding: 40px 10px 10px;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
}

h1 {
  text-shadow: 2px 2px 0 #f00, -2px -2px 0 #0ff;
  margin-top: 24px;
  font-size: 24px;
  padding: 6px 18px;
}

h2.slogan {
  margin: 6px 0 10px;
  font-size: 14px;
  font-weight: normal;
  color: #cfcfcf;
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

.shop-slot {
  will-change: transform;
  position: relative;
  font-family: 'JetBrains Mono', monospace;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px;
  border: 1px solid #2e2c2c;
  border-radius: 9px;
  background: transparent;
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

  & .disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.item-name {
  margin: 2px 0;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  color: #1d1919e7;
  max-width: 90%;
  word-break: break-word;
}

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

.item-price,
.item-stock {
  margin: 2px 0;
  font-size: 11px;
  line-height: 1.2;
  color: #333;
  max-width: 90%;
  word-break: break-word;
}

.rarity-trash { color: #585858; }
.rarity-common { color: #215b79; }
.rarity-rare { color: #278f3d; }
.rarity-epic { color: #8325ee; }
.rarity-legendary { color: rgb(230, 158, 24); }
.rarity-elder { color: rgb(143, 36, 17); }

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
</style>


  