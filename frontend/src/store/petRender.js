// src/store/petRender.js
import { defineStore }      from 'pinia'
import { reactive, ref }    from 'vue'
import api                  from '@/utils/axios'
import { useWardrobeStore } from './wardrobe'
import { usePetsStore }     from './pets'

const STATIC      = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'
const DIR_STATIC  = `${STATIC}/static`
const DIR_COSMO   = `${DIR_STATIC}/cosmetic`



/* ───────────────────────── helpers ───────────────────────── */

/** Вернёт объект wardrobe-item по wardrobe_id */
function byRid(rid) {
  const w = useWardrobeStore()
  return w.items.find(i => i.wardrobe_id === rid)
}

/** Если rid отсутствует, берём *первый* предмет в гардеробе с таким product_id */
function byPid(pid) {
  const w = useWardrobeStore()
  return w.items.find(i => i.product_id === pid)
}


function getRenderImage(item, pet = null) {
  let custom = item.custom
  if (typeof custom === 'string') {
    try { custom = JSON.parse(custom) } catch { custom = {} }
  }

  if (pet && custom?.render_variants) {
    const race = pet.race_code || pet.custom?.race_code
    if (race && custom.render_variants[race]) {
      return `${DIR_COSMO}/${custom.render_variants[race]}`
    }
  }

  if (custom?.image) {
    return `${DIR_COSMO}/${custom.image}`
  }

  return `${DIR_STATIC}/goods/${item.image}`
}

/* ───────────────────────── store ─────────────────────────── */

export const usePetRenderStore = defineStore('petRender', () => {
  /* state */
  const appearances      = reactive({})   // { petId: [ {rid,pid,slot,instance} ] }
  const customSlotOrders = ref({})        // { petId: [ {rid,pid,instance} ] }

  /* getters */
  const getSlotOrderFor = petId => customSlotOrders.value[petId] || []

  /* ───── fetch appearance from API (поля pid без rid) ───── */
  async function fetchAppearance(petId) {
  try {
    const { data } = await api.get(`/pets/${petId}/appearance`, {
      withCredentials: true
    })

    // 🔃 appearance: { slot: [{pid, rid, instance}] } → flat: [{slot, pid, rid, instance}]
    const flat = []
    Object.entries(data?.appearance || {}).forEach(([slot, arr]) => {
      (Array.isArray(arr) ? arr : [arr]).forEach(({ pid, rid, instance }) => {
        flat.push({ slot, pid, rid, instance })
      })
    })

    // 🧱 Добавляем базовый слой
    flat.unshift({ pid: -1, rid: -1, slot: 'base', instance: 0 })

    // ✅ Сохраняем нормализованный внешний вид
    appearances[petId] = flat

    // 🧠 Порядок слоёв
    customSlotOrders.value[petId] = [
      { pid: -1, rid: -1, slot: 'base', instance: 0 },
      ...(data?.slot_order || []).map(layer => ({
        pid: layer.pid ?? -1,
        rid: layer.rid ?? null,
        slot: layer.slot ?? null,
        instance: layer.instance ?? 0
      }))
    ]

  } catch (e) {
    console.error("🐛 Ошибка загрузки внешнего вида", e)

    appearances[petId] = [
      { pid: -1, rid: -1, slot: 'base', instance: 0 }
    ]
    customSlotOrders.value[petId] = [
      { pid: -1, rid: -1, slot: 'base', instance: 0 }
    ]
  }
}



  /* ───── buildLayers → {src,z,…} для рендера ───── */
function buildLayers(pet, layers = [], slotOrder = []) {
  const result = []

  for (const layer of layers) {
    if (layer.pid === -1 && pet?.image) {
      result.push({
        ...layer,
        src: pet.image.startsWith('http') ? pet.image : `${DIR_STATIC}/${pet.image}`,
        z: slotOrder.findIndex(o => o.pid === -1 && o.slot === 'base')
      })
      continue
    }

    const item = layer.rid != null ? byRid(layer.rid) : byPid(layer.pid)
    if (!item) continue

    let custom = item.custom
    if (typeof custom === 'string') {
      try { custom = JSON.parse(custom) } catch { custom = {} }
    }

    const raw =
      custom?.[`${layer.slot}_image`] ||
      (['aura', 'companion', 'dye', 'foreground', 'background'].includes(layer.slot) ? custom?.image : null) ||
      item.image
    if (!raw) continue

    const src = getRenderImage(item, pet)


    result.push({
      rid: item.wardrobe_id,
      pid: item.product_id,
      slot: layer.slot,
      instance: layer.instance ?? 0,
      src,
      z: slotOrder.findIndex(o =>
        (o.rid ?? o.pid) === (item.wardrobe_id ?? item.product_id) &&
        (o.instance ?? 0) === (layer.instance ?? 0)
      )
    })
  }

  return result.sort((a, b) => a.z - b.z)
}


function buildLayersCustom(pet, layers = [], slotOrder = [], resolveItem) {
  const result = []

  for (const layer of layers) {
    // Сам питомец
    if (layer.pid === -1 && pet?.image) {
      result.push({
        ...layer,
        src: pet.image.startsWith('http') ? pet.image : `${DIR_STATIC}/${pet.image}`,
        z: slotOrder.findIndex(o => o.pid === -1 && o.slot === 'base')
      })
      continue
    }

    const item = resolveItem(layer)
    if (!item) continue

    let custom = item.custom
    if (typeof custom === 'string') {
      try { custom = JSON.parse(custom) } catch { custom = {} }
    }

    const raw =
      custom?.[`${layer.slot}_image`] ||
      (['aura', 'companion', 'dye', 'foreground', 'background'].includes(layer.slot) ? custom?.image : null) ||
      item.image
    if (!raw) continue

    const src = raw.startsWith('http') || raw.startsWith('/')
      ? raw
      : `${DIR_COSMO}/${raw}`

    result.push({
      rid: item.wardrobe_id,
      pid: item.product_id,
      slot: layer.slot,
      instance: layer.instance ?? 0,
      src,
      z: slotOrder.findIndex(o =>
        (o.rid ?? o.pid) === (item.wardrobe_id ?? item.product_id) &&
        (o.instance ?? 0) === (layer.instance ?? 0)
      )
    })
  }

  return result.sort((a, b) => a.z - b.z)
}


function getMiniAvatarLayersForPet(petId) {
  const pet   = usePetsStore().myPets.find(p => p.id === petId)
  const lays  = appearances[petId] || []
  const order = getSlotOrderFor(petId)

  const HEAD_SLOTS = [
    'head', 'face', 'eyes', 'accessory', 'ears', 'skin', 'neck'
  ]

  // 💡 Всегда добавляем базовый слой
  const filtered = lays.filter(l => l.slot === 'base' || HEAD_SLOTS.includes(l.slot))
  return buildLayers(pet, filtered, order)
}


  /* ───── public helpers for components ───── */
  function getLayersForPet(petId) {
    const pet   = usePetsStore().myPets.find(p => p.id === petId)
    const lays  = appearances[petId] || []
    const order = getSlotOrderFor(petId)
    return buildLayers(pet, lays, order)
  }

  /** При создании превью (например в модалке) */
  function getLayersFromPreview(pet, preview = {}, slotOrder = []) {
    const flat = []
    Object.entries(preview).forEach(([slot, arr]) => {
      (Array.isArray(arr) ? arr : [arr]).forEach((o, idx) => {
        flat.push(typeof o === 'object'
          ? { ...o, slot }
          : { rid:null, pid:o, slot, instance:idx })
      })
    })
    return buildLayers(pet, flat, slotOrder)
  }

  /* ───── slot-order utils ───── */
  function setCustomSlotOrder(petId, order) {
  customSlotOrders.value[petId] = order.map(o => ({ ...o }))


  }
  const moveSlot = dir => (petId, rid, inst = 0) => {
    const ord = [...getSlotOrderFor(petId)]
    const i   = ord.findIndex(o => (o.rid ?? -999) === rid && (o.instance ?? 0) === inst)
    const j   = i + dir
    if (i === -1 || j < 0 || j >= ord.length) return
    ;[ord[i], ord[j]] = [ord[j], ord[i]]
    setCustomSlotOrder(petId, ord)
  }
  const moveSlotUp   = moveSlot(-1)
  const moveSlotDown = moveSlot(+1)

  function resetSlotOrder(petId){ delete customSlotOrders.value[petId] }

  /* expose */
  return {
    appearances,
    fetchAppearance,
    getLayersForPet,
    getLayersFromPreview,
    getSlotOrderFor,
    setCustomSlotOrder,
    moveSlotUp,
    moveSlotDown,
    resetSlotOrder,
    buildLayers,
    buildLayersCustom,
    getRenderImage,
    getMiniAvatarLayersForPet
  }
})









