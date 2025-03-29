<template>
    <div class="neon-circus">
      <!-- 🏮 Картинка локации -->
      <div class="circus-container">
        <img :src="circusImage" alt="Neon Circus" class="circus-image" />
        <div class="game-overlay">
        </div>
      </div>
  
      <!-- 🔥 Блок с играми (позже сделаем кликабельные зоны) -->
      <div class="games-section">
        <h2></h2>
      </div>
    </div>
  </template>
  
  <script setup>
  import circusImage from "@/assets/neon_circus.png"; // ✅ Загружаем картинку
  </script>
  
  <style scoped>
  /* 🔥 НЕОНОВОЕ ГЕЙМ-ЛОББИ */
  .neon-circus {
    position: relative;
    margin-top: auto;
    width: 100%;
    height: 85vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  /* 🎪 БЛОК С ЦИРКОМ */
  .circus-container {
    position: relative;
    width: 50%;
    max-width: 1200px;
  }
  
  .circus-image {
    width: 100%;
    border-radius: 30px;
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.7);
    transition: transform 0.3s ease-in-out;
  }
  
  .circus-image:hover {
    transform: scale(1.02);
  }
  
  /* 🏮 ПОЛУПРОЗРАЧНАЯ НАДПИСЬ */
  .game-overlay {
    position: absolute;
    top: 10%;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    padding: 10px 20px;
    border-radius: 10px;
    color: #ff00ff1e;
    font-size: 20px;
    font-weight: bold;
    text-shadow: 0 0 10px #ff00ff2f;
  }
  
  /* 🎰 СЕКЦИЯ С ИГРАМИ */
  .games-section {
    text-align: center;
    margin-top: 20px;
    color: white;
  }
  
  .games-section h2 {
    font-size: 24px;
    text-shadow: 0 0 10px cyan;
  }
  
  .games-section p {
    font-size: 16px;
    color: #aaa;
  }
  </style>
  