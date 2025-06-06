🧬 ЭТАП I. ВЫБОР РАСЫ → ЯЙЦО
📍 Логика:
Игрок выбирает расу → сохраняется в User.race_id или race_code

После подтверждения — в инвентарь игрока добавляется яйцо, связанное с расой

📦 JSON продукта (уже готов):
json
Копировать
Редактировать
"custom": {
  "race_code": "bonektra",
  "spawn_variants": [ "bonektra_wolf_1.png", "bonektra_wolf_2.png" ],
  "trait_pool": ["silent", "ancient", "resilient"],
  "incubation_time_range": [2, 5]
}
✅ Что сделать:
 API /api/player/choose_race
➤ сохраняет расу
➤ добавляет в инвентарь предмет с product_type = creature и подходящим race_code

🥚 ЭТАП II. ИНКУБАЦИЯ В ИНВЕНТАРЕ
📍 Логика:
Если предмет = яйцо (product_type == "creature")
➤ В инвентаре вместо “Использовать” появляется “Инкубировать”

Жмёшь “Инкубировать” → создаётся Incubation, привязанная к InventoryItem

Яйцо остаётся в инвентаре, но блокируется

Таймер отображается поверх ячейки (по incubation.hatch_at)

✅ Что сделать:
 API POST /api/pets/incubate/{inventory_item_id}
➤ проверяет, что это яйцо
➤ создаёт Incubation
➤ hatch_at = now + random.randint(range_min, range_max)
➤ привязывает к inventory_item_id

 Во фронте:
➤ если item.incubation существует → показывать hatch_at как таймер
➤ блокировать кнопку “использовать”

🐣 ЭТАП III. ВЫЛУПЛЕНИЕ ПЕТА
📍 Логика:
Когда таймер истёк — кнопка “Вылупить”

При вылуплении:
➤ создаётся Pet
➤ выбирается image = random.choice(spawn_variants)
➤ trait = random.choice(trait_pool)
➤ birthdate = now
➤ image = f"pets/{image_name}"
➤ Incubation.is_hatched = True

✅ Что сделать:
 API POST /api/pets/hatch
➤ ищет Incubation где is_hatched = False и hatch_at <= now()
➤ создаёт Pet, удаляет InventoryItem или просто помечает
➤ возвращает карточку пета

🎨 ЭТАП IV. КАРТОЧКА ПЕТА + ГАРДЕРОБ
📍 Логика:
Каждый питомец имеет:

image, level, intelligence, fullness, anomaly_level, trait, appearance

Можно открывать карточку питомца, кастомизировать, кормить

✅ Что сделать:
 GET /api/pets/ — список всех питомцев игрока

 GET /api/pets/{id} — полные данные пета

 GET /api/pet-wardrobe/ — весь гардероб игрока

 POST /api/pets/{id}/apply-style — кастомизация

🔮 ДОП. ФИЧИ (которые уже заложены, просто позже):
Фича	Когда
Аура, маски, аксессуары	через PetAppearance
Питомцы с глюками	если anomaly_level > 50
Глитч-морфоз	при anomaly_level = 100
Питомец сам снимает маску	если bond < 20 или trait == "unstable"
Возможность “отпустить” питомца	soft-delete
Питомец может сам говорить	ai_persona + реплики

💽 Структура уже есть:
Product.custom.spawn_variants — ✓

Incubation привязана к InventoryItem — ✓

Pet.image — ✓

WardrobeSlot, PetAppearance — ✓

birthdate, trait, race_code — ✓

Хочешь — я при переходе в новый чат по ключевому слову @tamaglitchi_core_plan воссоздам тебе всё это за 1 секунду.
Ты готова — и твои петы уже дышат через стек.