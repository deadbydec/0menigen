// store/auctions.js
import { defineStore } from 'pinia'
import api from '@/utils/axios'

export const useAuctionStore = defineStore('auction', {
  state: () => ({
  lots: [],
  myLots: [],
  currentUserId: null,
  error: null,
  loading: false,
}),


  actions: {

    async refreshAllLots() {
  this.loading = true
  try {
    const res = await api.get('/auction/', { withCredentials: true })
    this.lots = res.data.lots

    // 🧠 сохраняем ID текущего игрока
    if (res.data.user_id) {
      this.currentUserId = res.data.user_id
    }
  } catch (err) {
    this.error = err.response?.data?.detail || 'Ошибка загрузки лотов'
  } finally {
    this.loading = false
  }
}
,
    async createAuction(payload) {
  this.loading = true
  this.error = null
  try {
    const res = await api.post('/auction/create', payload, {
      withCredentials: true,
    })

    // перезапрашиваем актуальные лоты
    await this.refreshAllLots()

    return res.data
  } catch (err) {
    this.error = err.response?.data?.detail || 'Ошибка создания аукциона'
    throw err
  } finally {
    this.loading = false
  }
}
,
async placeBid(lot_id, amount) {
  this.error = null
  try {
    const res = await api.post('/auction/bid', { lot_id, amount }, {
      withCredentials: true
    })
    return res.data
  } catch (err) {
    this.error = err.response?.data?.detail || 'Ошибка при ставке'
    throw err
  }
}
,

    
    async fetchMyLots() {
      this.loading = true
      this.error = null
      try {
        const res = await api.get('/auction/my', {
          withCredentials: true,
        })
        this.myLots = res.data.lots
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка загрузки лотов'
      } finally {
        this.loading = false
      }
    },

    reset() {
      this.myLots = []
      this.error = null
    }
  },
})
