<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-6">
    <h1 class="text-4xl font-black mb-8 tracking-widest"></h1>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-5xl">

      <router-link to="/landfill" class="card">
        <img src="@/assets/Landfill.jpg" alt="Свалка" class="card-img" />
        <div class="card-content">
          <h2 class="card-title">Свалка</h2>
          <p class="card-description">
            Отходы жизни и выброшенные мечты – здесь хаос правит балом.
          </p>
        </div>
      </router-link>

      <router-link to="/black-market" class="card">
        <img src="@/assets/BlackMarket.jpg" alt="Чёрный рынок" class="card-img" />
        <div class="card-content">
          <h2 class="card-title">Чёрный рынок</h2>
          <p class="card-description">
            Тайные сделки и тёмные фишки для тех, кто идёт против системы.
          </p>
        </div>
      </router-link>

      <router-link to="/void-gate" class="card">
        <img src="@/assets/VoidPortal.jpg" alt="Портал в бездну" class="card-img" />
        <div class="card-content">
          <h2 class="card-title">Портал в бездну</h2>
          <p class="card-description">
            Погрузись в бездну, где логика отдыхает, а хаос витает в воздухе.
          </p>
        </div>
      </router-link>

    </div>
  </div>
</template>
  
  <script setup>
  // Никакого лишнего — роутинг через router-link. Просто чистый визуальный беспредел.
  </script>
  
  <style scoped>
  .card {
  width: 100%;
  border: 1px solid rgb(0, 0, 0);
  height: 290px;           /* Зафиксировали высоту карточки */
  max-height: 290px;
  display: block;
  background: #0000009a;
  border-radius: 0.90rem;
  overflow: hidden;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
}

/* Картинка */
.card-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

/* Контейнер под текст */
.card-content {
  padding: 0rem 1.5rem 1.8rem;
  /* убрали flex и overflow, чтобы текст не прятался и не вылезал за блок */
  height: calc(100% - 180px);
  box-sizing: border-box;  /* Чтобы учесть padding внутри высоты */
}

.card-title {
  font-size: 1.75rem;
  font-weight: 500;
  margin-bottom: 0.9rem;
  color: #ffffff;
}

.card-description {

  color: #cfcfcf;
}

h1 {
  text-shadow: 2px 2px 0 #f00, -2px -2px 0 #0ff;
}
  
  </style>
  
  
  