<template>
    <div v-if="!authStore.user?.race_id" class="identity-selection">
      <h2 class="title">Выбери свою сущность</h2>
    
      <div class="races">
        <div 
  v-for="race in races" 
  :key="race.code" 
  class="race-card" 
  :class="{ active: selectedRace && selectedRace.code === race.code }"
  @click="selectRace(race)"
>
  <img
    :src="race.image_url || 'https://dummyimage.com/250x250/000/fff&text=Race'"
    :alt="race.display_name"
    class="race-img"
    @error="e => e.target.src = 'https://dummyimage.com/250x250/000/fff&text=Race'" 
  />

  <div class="race-info">
    <div class="header-block">
      <h3>{{ race.display_name }}</h3>
      <p class="vibe">{{ race.vibe }}</p>
    </div>
    <p class="desc">{{ race.description }}</p>
  </div>
</div>

      </div>
      
      <div class="additional-info">
        <div class="form-group">
          <label for="gender">Пол:</label>
          <select v-model="gender" id="gender">
  <option value="MALE">Мужской</option>
  <option value="FEMALE">Женский</option>
  <option value="NONBINARY">Небинарный</option>
  <option value="UNKNOWN">Неизвестный</option>
</select>
        </div>
        
        <div class="form-group">
          <label for="birth_date">Дата рождения:</label>
          <input type="date" v-model="birthDate" id="birth_date" />
        </div>
      </div>
      
      <button 
        :disabled="!selectedRace || !gender || !birthDate" 
        @click="submitIdentity" 
        class="submit-btn">
        Я — это
      </button>
    </div>
    
    <!-- 🎭 Если сущность уже выбрана – элегантный 404 в стиле твоего мира -->
    <div v-else class="not-found">
      <div class="not-found-card">
        <h1>404</h1>
        <p>Такой страницы не существует. Или… ты уже выбрал свою сущность.</p>
        <button @click="router.push('/home')" class="return-btn">Вернуться в мир</button>
      </div>
    </div>
  </template>
    
    <script setup>
    import { ref, onMounted } from "vue";
    import { useRouter } from "vue-router";
    import { useAuthStore } from "@/store/auth";
    import api from "@/utils/axios";
    
    const router = useRouter();
    const authStore = useAuthStore();
    
    const races = ref([]);
    const selectedRace = ref(null);
    const gender = ref("мужской");
    const birthDate = ref("");
    
    const fetchRaces = async () => {
  console.log("User loaded:", authStore.user);
  try {
    const response = await api.get("/player/races");
    console.log("🎲 Полученные расы:", response.data); // 🔥 добавь это
    races.value = response.data.filter(r => r.is_selectable);
  } catch (error) {
    console.error("Ошибка загрузки рас:", error);
  }
};



    
    const selectRace = (race) => {
      selectedRace.value = race;
    };
    
    const submitIdentity = async () => {
      try {
        await api.post("/player/choose-identity", {
          race: selectedRace.value.code,
          gender: gender.value,
          birth_date: birthDate.value,
        });
        router.push("/news")
      } catch (error) {
        console.error("Ошибка при выборе сущности:", error.response?.data || error.message);
      }
    };
    
    onMounted(() => {
      if (authStore.user?.race_id) {
        router.push("/news");
      } else {
        fetchRaces();
      }
    });
    </script>
    
  <style scoped>

.identity-selection {
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE 10+ */
}

.identity-selection::-webkit-scrollbar {
  display: none; /* Chrome, Safari */
}

.header-block {
  margin-bottom: 6px;
}

.race-img {
  width: 250px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.race-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.vibe {
  font-weight: bold;
  color: #e476c9;
}

.desc {
  color: #d0d0d0;
  margin-top: 8px;
}

  /* Общий стиль для обеих веток */
  .identity-selection,
  .not-found {
    padding: 2rem;
    text-align: center;
    animation: fadeIn 0.8s ease-out;
    background: linear-gradient(135deg, #2c2c2c, #444);
    color: #fff;
    border-radius: 8px;
    max-width: 800px;
    margin: 2rem auto;
  }
  
  /* Секция выбора идентичности */
  .title {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }
  
  .races {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 0.9rem;
    
    
  }
  
  /* Стиль карточки расы */
  .race-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  background-color: rgba(30, 30, 30, 0.5);
  transition: transform 0.2s ease;
  cursor: pointer;
  text-align: left;
}
  
  .race-card:hover {
    transform: scale(1.03);
    box-shadow: 0 0 30px rgba(255, 255, 255, 0);
  }
  
  .race-card.active {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgb(6, 216, 164);
  }
  
  .race-card .vibe {
    font-weight: bold;
  color: #e476c9;
  margin-top: 2px;
  font-size: 0.95rem;
  flex-direction: column;
  }
  
  .race-card .desc {
    font-size: 0.9rem;
    color: #ccc;
    line-height: 1.5;
  font-size: 0.9rem;
  flex-direction: column;
  }
  
  .additional-info {
    margin-bottom: 1.8rem;
  }
  
  .form-group {
    margin: 1rem 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .form-group label {
    margin-bottom: 0.5rem;
  }
  
  .submit-btn {
    background: #ff4081;
    color: #fff;
    border: none;
    padding: 0.8rem 1.8rem;
    font-size: 1rem;
    border-radius: 30px;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  
  .submit-btn:disabled {
    background: #777;
    cursor: not-allowed;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: #e73370;
  }
  
  /* Секция "Not Found" */
  .not-found {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
  }
  
  .not-found-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 2rem;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    animation: popIn 0.6s ease-out;
  }
  
  .not-found h1 {
    font-size: 4rem;
    margin-bottom: 1rem;
  }
  
  .not-found p {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
  }
  
  .return-btn {
    background: #ff4081;
    color: #fff;
    border: none;
    padding: 0.8rem 1.8rem;
    font-size: 1rem;
    border-radius: 30px;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  
  .return-btn:hover {
    background: #e73370;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  @keyframes popIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  </style>
  
  

  