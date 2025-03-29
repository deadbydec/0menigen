import json
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, select, Float, ARRAY, TIMESTAMP, Date, func, JSON
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import Config
from sqlalchemy.orm import selectinload
from sqlalchemy import Enum as SqlEnum
from database import async_session, Base  # ✅ Теперь используется правильный sessionmaker!


# Асинхронный движок базы данных
engine = create_async_engine(Config.DATABASE_URL, echo=True, future=True)

# Фабрика сессий
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс моделей

UTC = timezone.utc

class GenderEnum(str, enum.Enum):
    MALE = "мужской"
    FEMALE = "женский"
    NONBINARY = "небинарный"
    UNKNOWN = "неизвестный"


# 🔥 ENUM КЛАССЫ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЙ
class UserType(str, enum.Enum):
    OMEZKA = "OMEZKA"
    OMEGAN = "OMEGAN"
    OMEGAKRUT = "OMEGAKRUT"

    def to_russian(self):
        return {
            "OMEZKA": "Омежка",
            "OMEGAN": "Омеган",
            "OMEGAKRUT": "Омегакрут",
        }[self.value]


class VipStatus(str, enum.Enum):
    NONE = "none"
    CRYPTOVOID = "cryptovoid"
    NULLOVERLORD = "nulloverlord"


# 🔥 КЛАСС ЮЗЕРА В FastAPI
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    nicknames = Column(ARRAY(String), default=[])
    password = Column(String(200), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    avatar = Column(String(200), nullable=False, default='default_avatar.png')
    bio = Column(String(500), default='Напишите о себе...')
    coins = Column(Integer, default=500)
    nullings = Column(Float, default=0.0)  # Десятичные числа, но с возможными округлениям
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    layout = Column(Text, nullable=True)
    total_playtime = Column(Float, default=0.0)
    gender = Column(SqlEnum(GenderEnum, name="gender"), default=GenderEnum.UNKNOWN, nullable=False)
    birthdate = Column(Date, nullable=True)
    user_type = Column(SqlEnum(UserType, name="user_type"), nullable=False, default=UserType.OMEZKA)
    last_ips = Column(ARRAY(INET), default=[])
    warning_count = Column(Integer, default=0)
    registration_date = Column(TIMESTAMP(timezone=True), default=func.now())
    last_login = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    vip_status = Column(SqlEnum(VipStatus, name="vip_status"), default=VipStatus.NONE, nullable=False)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=True)  # Ссылка на расу
    race = relationship("Race", backref="players")  # Связь с расой
    
    toilet_doom = relationship("ToiletDoom", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wall_posts = relationship("WallPost", back_populates="user", lazy="selectin")
    sent_gifts = relationship("PendingGift", foreign_keys="[PendingGift.sender_id]", back_populates="sender")
    received_gifts = relationship("PendingGift", foreign_keys="[PendingGift.recipient_id]", back_populates="recipient")
    game_scores = relationship("GameScore", back_populates="user")
    sent_friend_requests = relationship("Friendship", foreign_keys="[Friendship.user_id]", back_populates="user")
    received_friend_requests = relationship("Friendship", foreign_keys="[Friendship.friend_id]", back_populates="friend")
    system_messages = relationship("SystemMessage", back_populates="recipient")
    wall_posts = relationship("WallPost", back_populates="user", cascade="all, delete-orphan")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")


    def get_xp_to_next_level(self) -> int:
        return 100 + (self.level * 20)


    def add_nickname(self, new_username):
        if self.username != new_username:
            if self.nicknames is None:
                self.nicknames = []
            self.nicknames.append(self.username)
            self.username = new_username

    def add_ip(self, ip_address):
        if self.last_ips is None:
            self.last_ips = []
        if ip_address not in self.last_ips:
            self.last_ips.append(ip_address)
            if len(self.last_ips) > 5:  # Храним только последние 5 IP
                self.last_ips.pop(0)


    def __repr__(self):
        return f'<User {self.username}, Level {self.level}, XP {self.xp}>'

    async def add_xp(self, session: AsyncSession, amount: int):
        """
        Добавляем пользователю XP. Если XP превысило лимит для уровня,
        повышаем уровень и пересчитываем остаток XP.
        """
        self.xp += amount
        xp_needed = self.get_xp_to_next_level()

        while self.xp >= xp_needed:
            self.level += 1
            self.xp -= xp_needed
            xp_needed = self.get_xp_to_next_level()

        await session.commit()

# 🔥 ФУНКЦИИ ПОЛУЧЕНИЯ БД-СЕССИИ
async def get_db():
    async with async_session() as session:
        yield session


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    vibe = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_selectable = Column(Boolean, default=True)  # Можно ли выбрать на старте


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class WallPost(Base):
    __tablename__ = "wall_posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", back_populates="wall_posts")

    async def to_dict(self):
        """Конвертирует пост в JSON-объект"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    async def get_wall_posts(user_id):
        """Возвращает все посты пользователя (ASYNC)"""
        async with async_session() as session:
            result = await session.execute(
                WallPost.__table__.select().where(WallPost.user_id == user_id).order_by(WallPost.created_at.desc())
            )
            return result.scalars().all()

    @staticmethod
    async def add_wall_post(user_id, text):
        """Создаёт новый пост на стене пользователя (ASYNC)"""
        async with async_session() as session:
            new_post = WallPost(user_id=user_id, text=text)
            session.add(new_post)
            await session.commit()   


class Friendship(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    status = Column(String(20), default="pending")  # "pending" (ожидание), "accepted" (принято)

    user = relationship("User", foreign_keys=[user_id], back_populates="sent_friend_requests")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="received_friend_requests")

    @staticmethod
    async def get_friends(user_id):
        """Возвращает список друзей пользователя (ASYNC)"""
        async with async_session() as session:
            result = await session.execute(
                select(Friendship).where(Friendship.user_id == user_id, Friendship.status == "accepted")
            )
            return result.scalars().all()

    @staticmethod
    async def add_friend(user_id, friend_id):
        """Добавляет друга (ASYNC)"""
        async with async_session() as session:
            new_friendship = Friendship(user_id=user_id, friend_id=friend_id, status="pending")
            session.add(new_friendship)
            await session.commit()
            return {"message": "Запрос в друзья отправлен!"}

    @staticmethod
    async def accept_friend_request(user_id, friend_id):
        """Принимает запрос в друзья (ASYNC)"""
        async with async_session() as session:
            friendship = await session.execute(
                select(Friendship).where(Friendship.user_id == friend_id, Friendship.friend_id == user_id, Friendship.status == "pending")
            )
            friendship = friendship.scalar()
            if friendship:
                friendship.status = "accepted"
                await session.commit()
                return {"message": "Друг добавлен!"}
            return {"error": "Запрос не найден!"}

    @staticmethod
    async def remove_friend(user_id, friend_id):
        """Удаляет друга (ASYNC)"""
        async with async_session() as session:
            friendship = await session.execute(
                select(Friendship).where(
                    (Friendship.user_id == user_id, Friendship.friend_id == friend_id) |
                    (Friendship.user_id == friend_id, Friendship.friend_id == user_id)
                )
            )
            friendship = friendship.scalar()
            if friendship:
                await session.delete(friendship)
                await session.commit()
                return {"message": "Друг удалён!"}
            return {"error": "Друг не найден!"}


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    achievement_id = Column(String(50), nullable=False)  # ID из JSON-файла
    earned_at = Column(DateTime, default=datetime.now(UTC))  # Когда ачивка получена

    user = relationship("User", backref="achievements", lazy=True)

    def to_dict(self):
        """Конвертирует ачивку в JSON-формат"""
        return {
            "achievement_id": self.achievement_id,
            "earned_at": self.earned_at.isoformat(),
        }


class Leaderboard(Base):
    __tablename__ = 'leaderboard'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    category = Column(String(50), nullable=False)  # "money", "games", "pvp"
    score = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.now(UTC))

    user = relationship("User", backref="leaderboard_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username,  # Добавляем имя игрока
            "category": self.category,
            "score": self.score,
            "last_updated": self.last_updated.isoformat(),
        }


class GameScore(Base):
    __tablename__ = "game_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    game_id = Column(Integer, nullable=False)  # ID мини-игры
    score = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="game_scores")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_id": self.game_id,
            "score": self.score,
            "timestamp": self.timestamp.isoformat()
        }

        

# Модель News
class News(Base):
    __tablename__ = "news"  # ✅ Теперь SQLAlchemy знает, как называется таблица!

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<News {self.title}>"

    @staticmethod
    async def get_latest_news(limit=10):
        """Возвращает последние новости (ASYNC)"""
        async with async_session() as session:
            result = await session.execute(
                select(News).order_by(News.created_at.desc()).limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def add_news(title, content):
        """Добавляет новость (ASYNC)"""
        async with async_session() as session:
            new_news = News(title=title, content=content)
            session.add(new_news)
            await session.commit()
            return {"message": "Новость добавлена!"}


class ProductType(enum.Enum):
    food = "еда"
    drink = "напиток"
    sweet = "сладость"
    drug = "аптека"
    collectible = "коллекционный"
    cosmetic = "косметический"
    weapon = "оружие"
    resource = "ресурс"
    toy = "игрушка"
    souvenir = "сувенир"
    artifact = "артефакт"
    creature = "существо"
    book = "книга"
    tech = "гаджет"
    sticker = "наклейка"
    toilet = "туалет"


class ProductRarity(enum.Enum):
    trash = "мусорный"
    common = "обычный"
    prize = "призовой"
    rare = "редкий"
    epic = "эпический"
    legendary = "легендарный"
    special = "особый"
    unique = "уникальный"
    elder = "древний"
    vanished = "исчезнувший"
    glitched = "глитчевый"
    void = "пустотный"

    

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Цена в коинах
    image = Column(String(100), nullable=True)  # Добавляем поле для изображения
    rarity = Column(SqlEnum(ProductRarity, name="product_rarity"), nullable=False, default=ProductRarity.common)
    product_type = Column(SqlEnum(ProductType, name="product_type"), nullable=False, default=ProductType.drink)
    stock = Column(Integer, default=0)  # количество в наличии

    items = relationship('InventoryItem', back_populates='product', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}, Type: {self.product_type.value}, Rarity: {self.rarity.value}>"

class InventoryItem(Base):
    __tablename__ = "user_inventory"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())  # 🔥 Добавлено время получения предмета

    product = relationship('Product', back_populates='items')
    user = relationship("User", backref="inventory")
    gift_links = relationship("PendingGift", back_populates="item")



class PrivateMessage(Base):
    __tablename__ = 'private_message'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    subject = Column(String(200), default="")
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(UTC))
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)  # 🔥 Добавлено время прочтения

    sender = relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = relationship('User', foreign_keys=[recipient_id], backref='received_messages')


class SystemMessageType(str, enum.Enum):
    ADMIN = "admin" 

    RANDOM_EVENT = "random_event"                     
    EVENT_NEGATIVE = "event_negative"    
    EVENT_POSITIVE = "event_positive"    
    BOT = "bot"                          
    LEVEL_UP = "level_up"                
    AUCTION_RESULT = "auction_result"    
    TRADE_PROPOSAL = "trade_proposal"    
    AI_ASSISTANT = "ai_assistant"        
    
    FRIEND_REQUEST = "friend_request"    
    FRIEND_ACCEPTED = "friend_accepted"   
    FRIEND_REJECTED = "friend_rejected"
    FRIEND_CANCELLED = "friend_cancelled"
    
    NPC_EVENT = "npc_event"           
    REPUTATION = "reputation_change"     
    
    GIFT = "gift" 
    GIFT_RECEIVED = "gift_received"  
    GIFT_ACCEPTED = "gift_accepted"  
    GIFT_REJECTED = "gift_rejected"  


class SystemMessage(Base):
    __tablename__ = "system_messages"

    id = Column(Integer, primary_key=True)
    recipient_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    message_type = Column(
    SqlEnum(SystemMessageType, name="system_message_type"),
    nullable=False
)
    title = Column(String(100), default="📩 Новое событие")
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    related_id = Column(Integer, nullable=True)
    is_actioned = Column(Boolean, default=False)

    recipient = relationship("User", back_populates="system_messages")



class ForumThread(Base):
    """Таблица тем форума"""
    __tablename__ = 'forum_threads'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    posts = relationship('ForumPost', backref='thread', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "views": self.views,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "post_count": len(self.posts)
        }

class ForumPost(Base):
    """Таблица сообщений в темах форума"""
    __tablename__ = 'forum_posts'

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('forum_threads.id'), nullable=False)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    author_id = Column(Integer, ForeignKey("user.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "author": self.author,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }
    
    
    author = relationship("User", backref="forum_posts")

class PendingGift(Base):
    __tablename__ = "pending_gifts"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.id"))
    recipient_id = Column(Integer, ForeignKey("user.id"))
    item_id = Column(Integer, ForeignKey("user_inventory.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_gifts")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_gifts")
    item = relationship("InventoryItem", back_populates="gift_links")



# Модель в БД для хранения отозванных токенов
class TokenBlocklist(Base):
    __tablename__ = "token_bl"
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

# 🔥 ДОБАВЛЯЕМ ФУНКЦИЮ ДЛЯ СОЗДАНИЯ ТАБЛИЦ В БАЗЕ
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class ToiletDoom(Base):
    __tablename__ = "toilet_doom"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True)

    clean = Column(Boolean, default=True)
    last_visit = Column(DateTime, default=datetime.utcnow)
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    decor = Column(JSON, default={})  # хранит украшения
    notes = Column(Text, default="")  # произвольные метки (системные)

    user = relationship("User", back_populates="toilet_doom")

class ToiletCooldown(Base):
    __tablename__ = "toilet_cooldowns"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    next_available = Column(DateTime, nullable=False)

class ToiletVote(Base):
    __tablename__ = "toilet_votes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    vote_type = Column(String(10), nullable=False)  # 'like' or 'dislike'
    created_at = Column(DateTime, default=datetime.utcnow)

