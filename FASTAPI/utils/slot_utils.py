from models.models import WardrobeSlot

def get_enum_slot(slot_str: str) -> WardrobeSlot:
    try:
        return WardrobeSlot[slot_str]  # строго по .name
    except KeyError:
        raise ValueError(f"Слот {slot_str} не найден в WardrobeSlot")
