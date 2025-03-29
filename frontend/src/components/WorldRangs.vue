<template>
    <div class="world-rangs">
      <h2>⭐ Топы мира ⭐</h2>
  
      <div class="leaderboard-container">
        <!-- Блок "Богачи" -->
        <div class="leaderboard">
          <h3>💰 Богачи</h3>
          <div class="switch-buttons">
            <button @click="activeCategory = 'coins'; activePeriod = 'week'">Неделя</button>
            <button @click="activeCategory = 'coins'; activePeriod = 'month'">Месяц</button>
          </div>
          <ul>
            <li v-for="(player, index) in leaderboard" :key="player.id">
              {{ index + 1 }} - {{ player.username }} ({{ player.coins }} монет)
            </li>
          </ul>
        </div>
  
        <!-- Блок "Боги" -->
        <div class="leaderboard">
          <h3>🏆 Боги</h3>
          <div class="switch-buttons">
            <button @click="activeCategory = 'levels'; activePeriod = 'week'">Неделя</button>
            <button @click="activeCategory = 'levels'; activePeriod = 'month'">Месяц</button>
          </div>
          <ul>
            <li v-for="(player, index) in leaderboard" :key="player.id">
              {{ index + 1 }} - {{ player.username }} (Ур. {{ player.level }})
            </li>
          </ul>
        </div>
      </div>
  
      <p class="coming-soon">Остальные топ-блоки со статистикой скоро!</p>
    </div>
  </template>

<style lang="scss">.world-rangs {
    text-align: center;
    color: #fff;
  
    .leaderboard-container {
      display: flex;
      justify-content: center;
      gap: 2rem;
    }
  
    .leaderboard {
      background: rgba(0, 0, 0, 0.5);
      padding: 1rem;
      border-radius: 10px;
      width: 300px;
  
      h3 {
        margin-bottom: 0.5rem;
      }
  
      .switch-buttons {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        
        button {
          background: #444;
          border: none;
          padding: 0.5rem;
          cursor: pointer;
          transition: 0.2s;
  
          &:hover {
            background: #666;
          }
        }
      }
  
      ul {
        list-style: none;
        padding: 0;
        margin-top: 1rem;
  
        li {
          padding: 0.5rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
      }
    }
  
    .coming-soon {
      margin-top: 2rem;
      font-size: 1.2rem;
      opacity: 0.8;
    }
  }
  </style>