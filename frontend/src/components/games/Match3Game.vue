<template>
  <div>
  <button class="close-btn" @click="$emit('close')">×</button>
    <div ref="phaserContainer" class="match3-wrapper"></div>
    <!-- Кнопка сохранения -->
    <div class="score-actions">
      <button @click="saveResult" class="save-btn">Сохранить результат</button>
    </div>
  </div>
  </template>
  
  <script setup>
  import Phaser from 'phaser'
  import { ref, onMounted } from 'vue'
  import { useToastStore } from '@/store/toast' 
  import api from '@/utils/axios'
  
  /** 
   * Эти 2 переменные (currentScore, currentCombos) 
   * — реактивны, чтобы записывать результат игры 
   * и потом отправлять на бэк. 
   */
  const currentScore = ref(0)
  const currentCombos = ref(0)
  
  const toastStore = useToastStore()
  const phaserContainer = ref(null)
  
  /** 
   * Функция сохранения (связывает текущие очки/комбо с бэком).
   */
  async function saveResult() {
    const score = currentScore.value
    const combos = currentCombos.value
  
    // Конвертация: 100 очков = 5 монет, XP ~ score/20
    const coinsEarned = Math.floor(score / 100) * 5
    const xpEarned = Math.floor(score / 20)
  
    try {
      const response = await api.post('/games/match3/submit', {
        score,
        combos,
        coins_earned: coinsEarned,
        xp_earned: xpEarned
      }, {
        withCredentials: true
      })
  
      const data = response.data
      
      if (data.coins_gained > 0) {
      toastStore.addToast(
        `🎉 ${data.message} +${data.coins_gained} монет, +${data.xp_gained} XP`,
        { type: 'success', duration: 5000 }
      )
    } else {
      // ⏳ Расчёт оставшегося времени
      const now = new Date()
      const nextDay = new Date()
      nextDay.setHours(0, 0, 0, 0)
      nextDay.setDate(nextDay.getDate() + 1)

      const diff = nextDay - now
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff / (1000 * 60)) % 60)

      toastStore.addToast(
        `☠ ${data.message}\n🕒 До следующей награды: ${hours}ч ${minutes}м`,
        { type: 'warning', duration: 5000 }
      )
    }

  } catch (err) {
    console.error('Ошибка сохранения:', err)
    toastStore.addToast('Не удалось сохранить результат', {
      type: 'error',
      duration: 3000
    })
  }
}
  
  // Параметры доски
  const CELL_SIZE = 64
  const ROWS = 8
  const COLS = 8
  
  // Типы камней
  const cellTypes = ['null', 'bug', 'glitch', 'cringe', 'ping', 'void']
  
  // Пути к ассетам
  const texturePaths = {
    null: new URL('@/assets/match3/null.png', import.meta.url).href,
    bug: new URL('@/assets/match3/bug.png', import.meta.url).href,
    glitch: new URL('@/assets/match3/glitch.png', import.meta.url).href,
    cringe: new URL('@/assets/match3/cringe.png', import.meta.url).href,
    ping: new URL('@/assets/match3/ping.png', import.meta.url).href,
    void: new URL('@/assets/match3/void.png', import.meta.url).href,
    dot: new URL('@/assets/match3/dot.png', import.meta.url).href
  }
  
  let board = []
  let selectedCell = null
  let scoreText = null  // Показывает счёт на сцене
  
  onMounted(() => {
    const config = {
      type: Phaser.AUTO,
      width: COLS * CELL_SIZE,
      height: ROWS * CELL_SIZE + 50, // место для отображения счёта
      parent: phaserContainer.value,
      transparent: true,
      scene: {
        preload,
        create,
        update
      }
    }
    new Phaser.Game(config)
  })
  
  /** Загрузка ассетов Phaser */
  function preload() {
    for (const [key, path] of Object.entries(texturePaths)) {
      this.load.image(key, path)
    }
  }
  
  /** Инициализация сцены */
  function create() {
    // Текст счёта внизу
    scoreText = this.add.text(10, ROWS * CELL_SIZE + 10, 'Счёт: 0', {
      font: '20px Arial',
      fill: '#fff'
    })
  
    initBoard(this)
  
    // Клики по камням
    this.input.on('gameobjectdown', (pointer, gameObject) => {
      handleClick(this, gameObject)
    })
  }
  
  function update() {
    // тут можно что-то делать каждый кадр, если надо
  }
  
  /** Создаёт начальную доску */
  function initBoard(scene) {
    board = []
    for (let y = 0; y < ROWS; y++) {
      const row = []
      for (let x = 0; x < COLS; x++) {
        const type = Phaser.Utils.Array.GetRandom(cellTypes)
        const sprite = createCellSprite(scene, x, y, type)
        row.push({ x, y, type, sprite })
      }
      board.push(row)
    }
  }
  
  /** Создаёт один камень (спрайт) */
  function createCellSprite(scene, x, y, type) {
    const sprite = scene.add.sprite(
      x * CELL_SIZE + CELL_SIZE/2,
      y * CELL_SIZE + CELL_SIZE/2,
      type
    )
    sprite.setDisplaySize(CELL_SIZE - 4, CELL_SIZE - 4)
    sprite.setInteractive()
  
    sprite.setData('x', x)
    sprite.setData('y', y)
    sprite.setData('type', type)
  
    return sprite
  }
  
  /** Обработка кликов по фишкам */
  function handleClick(scene, sprite) {
    const x = sprite.getData('x')
    const y = sprite.getData('y')
    const cell = board[y][x]
    if (!cell) return
  
    if (!selectedCell) {
      // выделяем первую фишку
      selectedCell = cell
      cell.sprite.setAlpha(0.5)
    } else {
      // смотрим вторую
      const dx = Math.abs(cell.x - selectedCell.x)
      const dy = Math.abs(cell.y - selectedCell.y)
  
      if ((dx === 1 && dy === 0) || (dx === 0 && dy === 1)) {
        // соседние — свап
        swapCells(cell, selectedCell)
  
        // проверяем матчи
        const matched = findMatches()
        if (matched.length > 0) {
          selectedCell.sprite.setAlpha(1)
          selectedCell = null
          resolveMatches(scene)
        } else {
          // откат
          swapCells(cell, selectedCell)
          selectedCell.sprite.setAlpha(1)
          selectedCell = null
        }
      } else {
        // не соседние — перевыбор
        selectedCell.sprite.setAlpha(1)
        selectedCell = cell
        cell.sprite.setAlpha(0.5)
      }
    }
  }
  
  /** Меняем в board + анимируем */
  function swapCells(c1, c2) {
    const tempType = c1.type
    c1.type = c2.type
    c2.type = tempType
  
    const tempSprite = c1.sprite
    c1.sprite = c2.sprite
    c2.sprite = tempSprite
  
    const x1 = c1.x, y1 = c1.y
    const x2 = c2.x, y2 = c2.y
  
    c1.sprite.setData('x', x1)
    c1.sprite.setData('y', y1)
    c1.sprite.setData('type', c1.type)
  
    c2.sprite.setData('x', x2)
    c2.sprite.setData('y', y2)
    c2.sprite.setData('type', c2.type)
  
    tweenSwap(c1.sprite, x1, y1)
    tweenSwap(c2.sprite, x2, y2)
  }
  
  function tweenSwap(sprite, x, y) {
    sprite.scene.tweens.add({
      targets: sprite,
      x: x * CELL_SIZE + CELL_SIZE/2,
      y: y * CELL_SIZE + CELL_SIZE/2,
      duration: 150
    })
  }
  
  /** Ищем все совпадения >=3 */
  function findMatches() {
    const matches = new Set()
  
    // Горизонтали
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS - 2; x++) {
        const t1 = board[y][x].type
        const t2 = board[y][x+1].type
        const t3 = board[y][x+2].type
        if (t1 && t1 === t2 && t2 === t3) {
          matches.add(board[y][x])
          matches.add(board[y][x+1])
          matches.add(board[y][x+2])
        }
      }
    }
  
    // Вертикали
    for (let x = 0; x < COLS; x++) {
      for (let y = 0; y < ROWS - 2; y++) {
        const t1 = board[y][x].type
        const t2 = board[y+1][x].type
        const t3 = board[y+2][x].type
        if (t1 && t1 === t2 && t2 === t3) {
          matches.add(board[y][x])
          matches.add(board[y+1][x])
          matches.add(board[y+2][x])
        }
      }
    }
    return Array.from(matches)
  }
  
  /** 
   * Сжигаем совпадения, добавляем очки, 
   * +1 к combo (т.к. это новая волна) 
   */
  function resolveMatches(scene) {
    const matched = findMatches()
    if (!matched.length) return
  
    // каждая волна матчей = +1 к combo
    currentCombos.value++
  
    // добавляем очки
    currentScore.value += matched.length * 10
    scoreText.setText(`Счёт: ${currentScore.value}`)
  
    let animationsLeft = matched.length
  
    for (const cell of matched) {
      // маленький эффект вспышки
      const fire = scene.add.sprite(cell.sprite.x, cell.sprite.y, 'dot')
      fire.setAlpha(0.9)
      fire.setScale(1.2)
  
      scene.tweens.add({
        targets: fire,
        alpha: 0,
        scale: 0,
        duration: 300,
        onComplete: () => fire.destroy()
      })
  
      // анимация исчезновения
      scene.tweens.add({
        targets: cell.sprite,
        alpha: 0,
        scaleX: 0,
        scaleY: 0,
        duration: 250,
        onComplete: () => {
          cell.sprite.destroy()
          cell.type = null
          cell.sprite = null
          animationsLeft--
  
          // когда все исчезли
          if (animationsLeft === 0) {
            scene.time.delayedCall(150, () => {
              dropCells(scene)
              scene.time.delayedCall(300, () => {
                fillEmpty(scene)
                scene.time.delayedCall(300, () => {
                  // рекурсивно если дальше матчи
                  resolveMatches(scene)
                })
              })
            })
          }
        }
      })
    }
  }
  
  /** Опускаем фишки в пустоты */
  function dropCells(scene) {
    for (let x = 0; x < COLS; x++) {
      for (let y = ROWS - 1; y >= 0; y--) {
        if (!board[y][x].type) {
          for (let k = y - 1; k >= 0; k--) {
            if (board[k][x].type) {
              board[y][x].type = board[k][x].type
              board[y][x].sprite = board[k][x].sprite
  
              board[y][x].sprite.setData('x', x)
              board[y][x].sprite.setData('y', y)
  
              scene.tweens.add({
                targets: board[y][x].sprite,
                x: x * CELL_SIZE + CELL_SIZE/2,
                y: y * CELL_SIZE + CELL_SIZE/2,
                duration: 200
              })
  
              board[k][x].type = null
              board[k][x].sprite = null
              break
            }
          }
        }
      }
    }
  }
  
  /** Заполняем пустые клетки */
  function fillEmpty(scene) {
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        if (!board[y][x].type) {
          const newType = Phaser.Utils.Array.GetRandom(cellTypes)
          const newSprite = createCellSprite(scene, x, y, newType)
          board[y][x].type = newType
          board[y][x].sprite = newSprite
  
          // анимация появления сверху
          newSprite.y = -CELL_SIZE
          scene.tweens.add({
            targets: newSprite,
            y: y * CELL_SIZE + CELL_SIZE/2,
            duration: 200
          })
        }
      }
    }
  }
  </script>
  
  <style scoped>

.close-btn {
  position: absolute;
  top: 1px;
  right: -90px;
  font-size: 24px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  z-index: 10;
}

  .match3-wrapper {
    margin-top: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .score-actions {
    margin-top: 20px;
  }
  
  .save-btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }
  .save-btn:hover {
    background-color: #0056b3;
  }
  </style>
  
  
  
  
  
  
  
  
  