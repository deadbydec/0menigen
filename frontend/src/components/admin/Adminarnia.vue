<template>
  <div class="adminarnia">
    <h1>🛠 Добро пожаловать в <strong>ебаную админарню</strong>, {{ playerStore.player?.name }}.</h1>

    <div v-if="!isAdmin" class="denied">
      ⛔ У тебя нет прав. Уходи.
    </div>

    <div v-else class="content">
      <section>
        <h2>Пользователи:</h2>
        <button @click="fetchUsers" class="btn">🔄</button>
        <hr />
        
        <ul>
          <li v-for="user in users" :key="user.id">
            <strong>{{ user.username }}</strong>
            ----- {{ user.role?.display_name || "хуй" }}
            <select
  v-if="user.role?.name !== 'ADMIN'"
  @change="changeRole(user.id, $event.target.value)"
  :value="user.role?.name || ''"
>

  <option value="" disabled>Назначить роль</option>
  <option value="ADMIN">👑 Админ</option>
  <option value="MODERATOR">🛡 Модератор</option>
  <option value="TESTER">🧪 Тестер</option>
  <option value="AI">🤖 ИИ</option>
</select>
<small v-for="ip in user.last_ips" :key="ip" class="ip">🌐 {{ ip }}</small>

          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import { usePlayerStore } from "@/store/player"
import api from "@/utils/axios"

const playerStore = usePlayerStore()
const users = ref([])
const isAdmin = ref(false)

watch(() => playerStore.player, (newPlayer) => {
  if (newPlayer?.role?.name === "ADMIN") {
    isAdmin.value = true
    fetchUsers()
  }
})
async function fetchUsers() {
  try {
    const res = await api.get("/adminarnia/users")
    users.value = res.data
  } catch (err) {
    console.error("❌ Ошибка загрузки пользователей", err)
  }
}

async function changeRole(userId, newRole) {
  try {
    await api.post("/adminarnia/assign-role", {
      user_id: userId,
      role: newRole
    })
    await fetchUsers()
  } catch (err) {
    console.error("❌ Ошибка назначения роли", err)
  }
}

</script>

<style scoped>

.ip {
  display: block;
  color: #999;
  font-size: 0.8em;
  margin-left: 1em;
}


.btn {
  background: transparent;
  position:fixed;
  margin-left:70px;
  margin-top: -85px;
  width: 40px;
}

li {
  display:list-item;
  justify-content: center;
  margin-top: 30px;
  font-size: 16px;
}

.adminarnia {
  max-width: 700px;
  display:list-item;
  margin: 3rem auto;
  padding: 2rem;
  background: #121212;
  color: #f2f2f2;
  font-family: monospace;
  border-radius: 12px;
  box-shadow: 0 0 15px #0008;
}

h2 {
  font-size: 1.3rem;
  margin-bottom: 3rem;
}

h1 {
  font-size: 1.6rem;
  margin-bottom: 3rem;
}
.denied {
  background: #330000;
  padding: 1rem;
  border-left: 4px solid #cc0000;
}

ul {
  padding-left: 0;
  list-style: none;
}
li {
  margin-bottom: 0.5rem;
}
</style>

  