import { defineStore } from 'pinia'
import api from "@/utils/axios"

const state = () => ({
  clans: [],
  myClans: [],
  clanStats: {},
  searchQuery: '',
  sortBy: 'level',
})

const getters = {
  filteredClans(state) {
    let filtered = state.clans.filter(clan =>
      clan.name.toLowerCase().includes(state.searchQuery.toLowerCase())
    )

    if (state.sortBy === "level") {
      filtered.sort((a, b) => b.level - a.level)
    } else if (state.sortBy === "newest") {
      filtered.reverse() // TODO: заменить на sort по created_at
    }

    return filtered
  },

  hasClans(state) {
    return state.myClans.length > 0
  }
}

const actions = {
  async fetchClans() {
    try {
      const res = await api.get("/clans/")
      this.clans = res.data
    } catch (e) {
      console.error("Ошибка загрузки кланов:", e)
    }
  },

  async fetchMyClans() {
    try {
      const res = await api.get("/clans/my")
      this.myClans = res.data
    } catch (e) {
      console.error("Ошибка загрузки моих кланов:", e)
    }
  },

  async fetchClanStats() {
    try {
      const res = await api.get('/clans/stats')
      this.clanStats = res.data
    } catch (e) {
      console.error("Ошибка загрузки статистики кланов:", e)
    }
  },

  getAvatar(filename) {
    return filename
      ? `${import.meta.env.VITE_STATIC_URL}/static/clan_avatars/${filename}`
      : "/img/default_clan_avatar.png"
  }
}

export const useClansStore = defineStore('clans', {
  state,
  getters,
  actions
})



