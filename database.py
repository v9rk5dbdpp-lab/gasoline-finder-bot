import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH

async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('fuel', 'groceries', 'medicine', 'other')),
                location TEXT NOT NULL,
                region TEXT,
                price TEXT,
                characteristics TEXT,
                details TEXT,
                latitude REAL,
                longitude REAL,
                photo_file_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                upvotes INTEGER DEFAULT 0,
                downvotes INTEGER DEFAULT 0
            )
        """)
        
        await db.execute("CREATE INDEX IF NOT EXISTS idx_item_region ON reports(item_name, region, is_active)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_created ON reports(created_at DESC)")

        # Таблица донатов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                amount INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_donated INTEGER DEFAULT 0,
                reports_added INTEGER DEFAULT 0,
                is_premium BOOLEAN DEFAULT 0,
                premium_until TIMESTAMP,
                last_activity TIMESTAMP
            )
        """)

        # Таблица подписок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                item_query TEXT NOT NULL,
                region TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(active, item_query, region)")

        await db.commit()
        print("✅ База данных инициализирована")


# Здесь будут другие функции (add_report, search_reports и т.д.)
# Мы добавим их на следующем шаге
# ====================== ФУНКЦИИ ДЛЯ ПОДПИСОК ======================

async def add_subscription(user_id: int, username: Optional[str], item_query: str, region: Optional[str] = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO subscriptions (user_id, username, item_query, region)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, item_query.strip().lower(), region.strip().lower() if region else None))
        await db.commit()
        return cursor.lastrowid


async def get_user_subscriptions(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM subscriptions 
            WHERE user_id = ? AND active = 1
            ORDER BY created_at DESC
        """, (user_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def deactivate_subscription(subscription_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            UPDATE subscriptions 
            SET active = 0 
            WHERE id = ? AND user_id = ?
        """, (subscription_id, user_id))
        await db.commit()
        return cursor.rowcount > 0


async def save_donation(user_id: int, username: Optional[str], amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO donations (user_id, username, amount)
            VALUES (?, ?, ?)
        """, (user_id, username, amount))
        donation_id = cursor.lastrowid

        await db.execute("""
            INSERT INTO users (user_id, username, total_donated, last_activity)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                total_donated = total_donated + ?,
                last_activity = CURRENT_TIMESTAMP
        """, (user_id, username, amount, amount))
        await db.commit()
        return donation_id


async def add_user_report_contribution(user_id: int, username: Optional[str]) -> Dict:
    from config import REPORTS_FOR_PREMIUM, PREMIUM_DAYS_REWARD

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT reports_added, is_premium, premium_until FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        current_reports = row[0] if row else 0
        new_reports = current_reports + 1

        await db.execute("""
            INSERT INTO users (user_id, username, reports_added, last_activity)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                reports_added = reports_added + 1,
                username = excluded.username,
                last_activity = CURRENT_TIMESTAMP
        """, (user_id, username, new_reports))

        premium_granted = False
        if new_reports % REPORTS_FOR_PREMIUM == 0:
            from datetime import datetime, timedelta
            new_until = (datetime.now() + timedelta(days=PREMIUM_DAYS_REWARD)).isoformat()
            await db.execute("UPDATE users SET is_premium = 1, premium_until = ? WHERE user_id = ?", (new_until, user_id))
            premium_granted = True

        await db.commit()
        return {"reports_added": new_reports, "premium_granted": premium_granted}
    
    # ====================== ОСНОВНЫЕ ФУНКЦИИ ДЛЯ ОТЧЁТОВ ======================

async def add_report(
    user_id: int,
    username: Optional[str],
    item_name: str,
    category: str,
    location: str,
    region: Optional[str] = None,
    price: Optional[str] = None,
    characteristics: Optional[str] = None,
    details: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    photo_file_id: Optional[str] = None
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO reports 
            (user_id, username, item_name, category, location, region, price, 
             characteristics, details, latitude, longitude, photo_file_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, username, item_name.strip(), category, location.strip(),
            region.strip() if region else None,
            price.strip() if price else None,
            characteristics.strip() if characteristics else None,
            details.strip() if details else None,
            latitude, longitude, photo_file_id
        ))
        await db.commit()
        return cursor.lastrowid


async def search_reports(
    item_query: str,
    region_query: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        query = """
            SELECT * FROM reports 
            WHERE is_active = 1 
            AND (item_name LIKE ? OR characteristics LIKE ?)
        """
        params = [f"%{item_query.strip()}%", f"%{item_query.strip()}%"]
        
        if region_query:
            query += " AND region LIKE ?"
            params.append(f"%{region_query.strip()}%")
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_report_by_id(report_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_last_report(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM reports 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def vote_report(report_id: int, vote_type: str) -> bool:
    if vote_type not in ('up', 'down'):
        return False
    
    column = "upvotes" if vote_type == "up" else "downvotes"
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE reports SET {column} = {column} + 1 WHERE id = ?",
            (report_id,)
        )
        await db.commit()
        return True