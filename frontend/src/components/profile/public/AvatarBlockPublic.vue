<template>
  <div v-if="profile" class="avatar-block">
    <h1>{{ profile.username || "Омежка" }}</h1>
    <div class="avatar-progress-container">
      <svg class="xp-ring" viewBox="0 0 140 140">
        <circle class="bg" cx="70" cy="70" r="64" />
        <circle
          class="fg"
          cx="70"
          cy="70"
          r="64"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="xpOffset"
        />
      </svg>

      <div class="avatar-upload">
        <img :src="computedAvatar" alt="Аватар" class="avatar" />
      </div>
    </div>

    <div class="player-info">
      <!-- заменим player на profile -->
<div class="info-row"><span class="label">Уровень: </span><span>{{ profile.level || 1 }}</span></div>
<div class="info-row"><span class="label">Звание: </span><span>{{ profile.user_type || "Без титула" }}</span></div>
<div class="info-row"><span class="label">Раса: </span><span>{{ profile.race?.display_name || "Неизвестно" }}</span></div>
<div class="info-row"><span class="label">Пол: </span><span>{{ genderLabel(profile.gender) }}</span></div>
<div class="info-row"><span class="label">ДР: </span><span>{{ formatDate(profile.birthdate, true) }}</span></div>
<div class="info-row"><span class="label">В игре: </span><span>с {{ formatDate(profile.registrationDate) }}</span></div>

      <div
        v-if="!isOwner && friendStatus !== null"
        class="friend-button"
      >
        <button
          class="btn-friend"
          :class="statusClass"
          :disabled="friendStatus === 'pending'"
          @click="handleFriendAction"
        >
          {{ friendButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue"
import { usePlayerStore } from "@/store/player"
import { usePublicFriendsStore } from "@/store/publicFriends"

const props = defineProps({
  profile: {
    type: Object,
    required: true
  }
})

const { player } = usePlayerStore()
const friendsStore = usePublicFriendsStore() // 💡 без этого будет undefined

const isOwner = computed(() => player?.id === props.profile?.id)

const friendStatus = ref(null)

const defaultAvatar = "https://localhost:5002/api/profile/avatars/default_avatar.png"

const computedAvatar = computed(() => {
  const avatar = props.profile?.avatar
  if (avatar?.startsWith("/api/profile/avatars")) {
    return `https://localhost:5002${avatar}?t=${Date.now()}`
  }
  return defaultAvatar
})

const radius = 64
const circumference = 2 * Math.PI * radius

const xpPercent = computed(() => {
  if (!props.profile?.xp || !props.profile?.nextLevelXp) return 0
  return (props.profile.xp / props.profile.nextLevelXp) * 100
})

const xpOffset = computed(() => {
  return circumference - (circumference * xpPercent.value) / 100
})

function formatDate(isoString) {
  if (!isoString) return "Не указано"
  const date = new Date(isoString)
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric"
  })
}

function genderLabel(gender) {
  switch (gender) {
    case "MALE":
      return "Мужской"
    case "FEMALE":
      return "Женский"
    case "UNKNOWN":
      return "Не указан"
    default:
      return gender || "Неизвестно"
  }
}

const friendButtonText = computed(() => {
  switch (friendStatus.value) {
    case "none":
      return "Добавить в друзья"
    case "pending":
      return "Запрос отправлен"
    case "accepted":
      return "Удалить из друзей"
    default:
      return ""
  }
})

const statusClass = computed(() => {
  return {
    pending: friendStatus.value === "pending",
    accepted: friendStatus.value === "accepted",
    none: friendStatus.value === "none"
  }
})

async function fetchFriendStatus() {
  if (isOwner.value) return
  if (!props.profile?.id) return
  friendStatus.value = await friendsStore.checkStatus(props.profile.id)
}

async function handleFriendAction() {
  try {
    const id = props.profile?.id
    if (!id) return

    if (friendStatus.value === "none") {
      await friendsStore.sendRequest(id)
      friendStatus.value = "pending"
    } else if (friendStatus.value === "accepted") {
      await friendsStore.removeFriend(id)
      friendStatus.value = "none"
    }
  } catch (err) {
    console.error("❌ Ошибка действия с другом:", err)
  }
}

async function fetchPublicProfile() {
  try {
    const { data } = await axios.get(`/player/public/${playerId.value}`)
    profile.value = data
  } catch (err) {
    console.error("❌ Ошибка загрузки профиля:", err)
  }
}

onMounted(() => {
  fetchPublicProfile()
})

onMounted(() => {
  fetchFriendStatus()
})
</script>



  
  <style scoped>
.avatar-block {
  max-width: 600px;
  flex-direction: column;
  backdrop-filter: blur(7px);
  background: rgba(38, 32, 39, 0.48);
  border: 1px solid #2e2c2c;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: white;
}

.avatar-progress-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.xp-ring {
  position: absolute;
  width: 230px;
  height: 230px;
  top: -16px;
  left: -16px;
  transform: rotate(-90deg);
  z-index: 50;
}

.xp-ring .bg {
  fill: none;
  stroke: rgba(48, 40, 53, 0.356);
  stroke-width: 8;
  z-index: 50;
}

.xp-ring .fg {
  fill: none;
  stroke: #00ffc3;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.4s ease;
  z-index: 50;
}

.avatar-upload {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  transition: opacity 0.2s ease-in-out;
  cursor: pointer;
}

.avatar:hover {
  opacity: 0.7;
}

.avatar:hover + .edit-icon {
  opacity: 1;
}

.avatar-block h1 {
  font-size: 1.7rem;
  padding-top: 1px;
  font-weight: bold;
  color: #ffffff;
  font-family: 'JetBrains Mono', monospace;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-info p {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  color: white;
}

.label {
  color: #00ffc3;
  font-weight: 600;
}

.friend-button {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}
.btn-friend {
  padding: 6px 14px;
  font-weight: bold;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-friend.none {
  background-color: #50a050;
  color: white;
}
.btn-friend.accepted {
  background-color: #d45252;
  color: white;
}
.btn-friend.pending {
  background-color: #aaa;
  color: #eee;
  cursor: default;
}

  </style>
  
  