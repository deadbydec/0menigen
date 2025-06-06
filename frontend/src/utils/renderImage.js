// utils/renderImage.js

const STATIC = import.meta.env.VITE_STATIC_URL || 'https://localhost:5002'

export function getRenderImage(item, pet = null) {
  // 1. Попытка взять кастомный путь (по расе питомца)
  if (pet && item.custom?.render_variants) {
    const race = pet.race_code || pet.custom?.race_code
    if (race && item.custom.render_variants[race]) {
      return `${STATIC}/cosmetic/${item.custom.render_variants[race]}`
    }
  }

  // 2. Обычный кастомный путь
  if (item.custom?.image) {
    return `${STATIC}/cosmetic/${item.custom.image}`
  }

  // 3. Фоллбек на обычную иконку
  return `${STATIC}/goods/${item.image}`
}
