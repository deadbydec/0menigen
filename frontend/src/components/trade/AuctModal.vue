<template>
  <div class="create-modal">
    <div class="create-modal-content">
      <h2>Создание аукциона</h2>

      <div class="form">
        <label>
          Тип лота:
          <select v-model="form.item_type">
            <option value="item">🎁 Предмет</option>
            <option value="pet">🐾 Питомец</option>
          </select>
        </label>

        <label>
  Лот:
  <div v-if="!selectedItem">
    <button class="select-button" @click="openPicker">
      ➕ Выбрать {{ form.item_type === 'pet' ? 'питомца' : 'предмет' }}
    </button>
  </div>

  <div v-else class="selected-preview">
    <div
      v-if="form.item_type === 'pet'"
      class="mini-head-mask"
      style="margin-right: 10px"
    >
      <div class="pet-render">
        <img
          v-for="layer in orderedLayers(selectedItem.avatar_layers)"
          :key="layer.src + layer.z"
          :src="layer.src"
          class="layer"
          :class="`layer-${layer.slot}`"
          :style="{ zIndex: layer.z }"
        />
      </div>
    </div>

    <img
      v-else
      class="preview-icon"
      :src="selectedItem.icon || '/img/items/default.png'"
    />

    <span>{{ selectedItem.name }}</span>
    <button @click="clearSelected" class="off">✖</button>
  </div>
</label>
        <label>
          Валюта:
          <select v-model="form.currency">
            <option value="coins">🪙 Монеты</option>
            <option value="nullings">💠 Нуллинги</option>
          </select>
        </label>

        <label>
          Минимальная ставка:
          <input type="number" v-model="form.min_price" placeholder="1000" />
        </label>

        <label>
  Длительность:
  <select v-model="form.duration_hours">
    <option :value="0.25">🕐 15 минут</option>
    <option :value="0.5">🕐 30 минут</option>
    <option :value="1">🕐 1 час</option>
    <option :value="2">🕐 2 часа</option>
    <option :value="4">🕐 4 часа</option>
    <option :value="12">🕐 12 часов</option>
    <option :value="24">🕐 1 день</option>
  </select>
</label>


        <div class="buttons">
          <button type="submit" @click="submit" :disabled="loading">
            🚀 Создать
          </button>
          <button type="button" @click="$emit('close')">
            ❌ Отмена
          </button>
        </div>

        <div v-if="error" class="error-msg">⚠️ {{ error }}</div>
      </div>
    </div>
  </div>
  <InventoryPickerModal
  :visible="showItemPicker"
  @close="showItemPicker = false"
  @select="selectItem"
/>

<PetPickerModal
  :visible="showPetPicker"
  @close="showPetPicker = false"
  @select="onPetSelected"
/>
</template>

<script setup>
import { ref } from 'vue'
import { useAuctionStore } from '@/store/auction'
import { useToastStore } from '@/store/toast'

const store = useAuctionStore()
const selectedItem = ref(null)
const showItemPicker = ref(false)
const showPetPicker = ref(false)
import InventoryPickerModal from '@/components/trade/InventoryPickerModal.vue'
import PetPickerModal from '@/components/trade/PetPickerModal.vue'

import { useInventoryStore } from '@/store/inventory'
import { usePetsStore } from '@/store/pets'

const inventoryStore = useInventoryStore()
const toast = useToastStore()
const petsStore = usePetsStore()

const emit = defineEmits(['close'])
const MIN_PRICE_COINS = 500
const MIN_PRICE_NULLINGS = 0.10
const form = ref({
  item_type: 'item',
  item_id: null,
  currency: 'coins',
  min_price: MIN_PRICE_COINS,
  duration_hours: 0.25 // теперь минималка = 15 минут
})


const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (!form.value.item_id) {
    error.value = 'Выбери лот перед созданием'
    toast.error('Не выбран предмет или питомец')
    return
  }

  loading.value = true
  try {
    await store.createAuction(form.value) // она САМА вызывает refreshAllLots()
    toast.success('Лот успешно создан!')

    clearSelected()
    emit('close') // ❗ вот она, закрывашка модалки
  } catch (err) {
    console.error(err)
    error.value = 'Не удалось создать лот'
    toast.error('Не удалось создать лот')
  } finally {
    loading.value = false
  }
}

function openPicker() {
  if (form.value.item_type === 'item') {
    showItemPicker.value = true
  } else {
    showPetPicker.value = true
  }
}

function selectItem(item) {
  const product = item.product
  selectedItem.value = {
    id: item.id,
    name: product?.name || `Предмет #${item.id}`,
    icon: product?.image
      ? `${import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'}/static/goods/${product.image}`
      : '/static/goods/noimage.png'
  }
  form.value.item_id = item.id
  showItemPicker.value = false
  showPetPicker.value = false
}


function clearSelected() {
  selectedItem.value = null
  form.value.item_id = null
}

function orderedLayers(layers) {
  return [...(layers || [])].sort((a, b) => a.z - b.z)
}

const onPetSelected = (pet) => {
  form.value.item_type = 'pet'
  form.value.item_id = pet.id
  selectedItem.value = {
    id: pet.id,
    name: pet.name || `Питомец #${pet.id}`,
    avatar_layers: pet.avatar_layers || []
  }
  showPetPicker.value = false
}
</script>

<style scoped>

.preview-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
}

.selected-preview {
  display: flex;
  align-items: center;
  margin-top: 8px;
  gap: 6px;
}

/* для питомца */
.mini-head-mask {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background: #1f1f1f;
  position: relative;
}

.pet-render {
  position: relative;
  width: 42px;
  height: 42px;
}

.layer {
  position: absolute;
  width: 96px;
  height: 96px;
  top: -20px;
  left: -12px;
  transform: scale(1.1);
  object-fit: cover;
  pointer-events: none;
  image-rendering: pixelated;
}


.select-button {
  margin-top: 4px;
  padding: 0.4em 0.9em;
  background: linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  border: 1px solid rgb(196, 196, 196);
  border-radius: 8px;
  color: black;
  font-weight: bold;
  cursor: pointer;
}

.selected-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #202020;
  padding: 10px;
  border: 1px solid rgb(196, 196, 196);
  border-radius: 12px;
  margin-top: 6px;
}

.preview-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}


.caption {
  text-align: center;
  font-size: 0.8em;
  color: #999;
  margin-top: -0.6em;
  margin-bottom: 1.2em;
  font-style: italic;
  text-shadow: 
    0 0 2px rgb(0, 0, 0), 
    0 0 4px rgb(255, 255, 255), 
    0 0 2px rgb(0, 0, 0);
}

.create-banner {
  padding-bottom: 20px;
  padding-top: 20px;
  max-width: 70%;       
  height: auto;         
  object-fit: contain;  
  border-radius: 20px;
  display: block;
  
  margin: 4px auto;
  animation: floatY 3.5s ease-in-out infinite;
}

@keyframes floatY {
  0%   { transform: translateY(0); }
  50%  { transform: translateY(-8px); }
  100% { transform: translateY(0); }
}

.create-modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  
  justify-content: center;
  z-index: 999;
  animation: fadeInBg 0.3s ease forwards;
  background: rgba(0, 0, 0, 0.6);
}

.create-modal-content {
  background: #161616;
  border: 1px solid rgba(255, 255, 255, 0.322);
  border-radius: 12px;
  color: #fff;
  padding: 22px 26px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 0 24px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.25s ease forwards;
  text-align: left;
  font-family: 'Fira Code', monospace;
}

.off {
    width: 70px;
    background: transparent;
    position: fixed;
    right: 30px;
    margin-top: 2px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1em;
}

input[type="text"],
textarea {
  padding: 0.6em 0.8em;
  background: #222;
  border: 1px solid #555;
  border-radius: 6px;
  color: #fff;
  font-family: inherit;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5em;
  font-size: 0.9em;
}

.buttons {
  display: flex;
  justify-content: flex-end;
  gap: 1em;
}

.off {

}

button {
  padding: 0.5em 1.1em;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-family: inherit;
  transition: 0.2s ease;
  
}

button[type="submit"] {
  background:linear-gradient(20deg, rgb(5, 73, 70), rgb(13, 211, 211));
  color: rgb(24, 24, 24);
}

button[type="button"] {
  background: #333;
  color: white;
}

button:disabled {
  opacity: 0.6;
  pointer-events: none;
}

.error-msg {
  color: #ff8080;
  font-size: 0.85em;
  margin-top: -0.4em;
}
@keyframes scaleIn {
  0%   { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1);   opacity: 1; }
}
</style>