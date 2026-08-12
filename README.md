# EduPlatform 🎓

**EduPlatform** — Django 6, Django REST Framework (DRF), PostgreSQL va Tailwind CSS v4 asosida yaratilgan zamonaviy, to'liq funksional onlayn ta'lim platformasi.

---

## 🌟 Asosiy Imkoniyatlar

### 👤 Foydalanuvchilar va Autentifikatsiya
- **Rollar:** Talaba (Student) va O'qituvchi (Teacher) rollari.
- **Autentifikatsiya:** Django Session hamda JWT (SimpleJWT + Djoser) autentifikatsiyasi.
- **Profil:** Foydalanuvchi profilini tahrirlash (avatar, bio, telefon raqami).
- **SMS Tasdiqlash:** Eskiz.uz API orqali 6-xonali SMS tasdiqlash kodi yuborish.

### 📚 Kurslar Boshqaruvi
- **O'qituvchi Kabineti (Dashboard):** Kurslar yaratish, tahrirlash, o'chirish va nashr qilish/qoralamaga o'tkazish (`toggle_publish`).
- **Filtrlash va Qidiruv:** Kurslar ro'yxatini kategoriya, narx va yaratilgan sana bo me'yori bo'yicha filtrlash hamda qidirish.
- **Sig'im va O'rinlar:** Maksimal talabalar soni (`max_students`) va bo'sh o'rinlarni avtomatik hisoblash.

### 📖 Darslar
- **Ko'p turli kontent:** Video darslar (video fayl yuklash yoki YouTube video havola) hamda matnli darslar.
- **Ruxsatlar (Permissions):** Darslar faqat kursga yozilgan talabalar uchun ochiq (`CourseNotFull` va student ruxsatlari).

### 💳 To'lovlar va Yozilish
- **Kursga Yozilish:** Bepul kurslarga bir birikma bilan yozilish hamda kursdan chiqish.
- **To'lov Integratsiyasi:** Payme Webhook integratsiyasi (HMAC-SHA256 imzo tekshiruvi bilan) hamda to'lov simulyatsiyasi.

### 🎨 Dizayn va Dark Mode Support
- **Tailwind CSS v4:** Zamonaviy, tez va responsive interfeys.
- **Dual-Theme:** Dark Mode va Light Mode rejimlari (foydalanuvchi tanlovi `localStorage` da saqlanadi).

### 🔗 Integratsiyalar
- **Telegram Bot:** Yangi kursga yozilish sodir bo'lganda o'qituvchiga Telegram orqali avtomatik bildirishnoma yuborish.
- **Eskiz.uz SMS:** Telefon raqamini tasdiqlash uchun SMS yuborish xizmati.
- **Email:** Kursga yozilganda tasdiqlash xabarnomasi yuborish.

### 📄 OpenAPI / Swagger Hujjatlari
- `drf-spectacular` orqali avtomatik yaratiladigan **Swagger UI** va **ReDoc** hujjatlari.

---

## 🛠 Texnologiyalar Steki

| Qatlam | Texnologiyalar |
| :--- | :--- |
| **Backend** | Python 3.14 / 3.12, Django 6.0, Django REST Framework (DRF) |
| **Baza** | PostgreSQL, SQLite (development) |
| **Auth** | SimpleJWT, Djoser, Django Auth |
| **Frontend** | Django Templates, Tailwind CSS v4, JavaScript (ES6+) |
| **API Hujjatlar** | drf-spectacular (Swagger UI, ReDoc) |
| **Konteynerlashtirish** | Docker, Docker Compose |
| **Tashqi APIlar** | Eskiz.uz (SMS), Telegram Bot API, Payme Webhook |

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Repozitoriyani klonlash
```bash
git clone https://github.com/Lazizarahmatullayeva007/EduPlatform.git
cd EduPlatform
```

### 2. Virtual muhitni yaratish va faollashtirish
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Bog'liqliklarni (Dependencies) o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Muhit o'zgaruvchilarini (`.env`) sozlash
Loyiha ildiz papkasida `.env` faylini yarating va quyidagi namuna kabi to'ldiring:

```env
SECRET_KEY=your-custom-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Baza sozlamalari
DB_NAME=eduplatform
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Telegram Bot Integratsiyasi
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Eskiz SMS Integratsiyasi
ESKIZ_EMAIL=your_eskiz_email
ESKIZ_PASSWORD=your_eskiz_password

# Payme Webhook
PAYME_WEBHOOK_SECRET=your_payme_webhook_secret
```

### 5. Bazaga migratsiyalarni qo'llash
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Admin (Superuser) yaratish
```bash
python manage.py createsuperuser
```

### 7. Loyihani ishga tushirish
```bash
python manage.py runserver
```

Loyiha brauzerda ochiladi: **`http://127.0.0.1:8000/`**

---

## 🐳 Docker bilan Ishga Tushirish

Loyihani PostgreSQL ma'lumotlar bazasi bilan birga Docker konteynerida ishga tushirish uchun:

```bash
# Konteynerlarni qurish va ishga tushirish
docker-compose up -d --build

# Migratsiyalarni bajarish
docker-compose exec web python manage.py migrate
```

---

## 🎨 Tailwind CSS'ni Kompilyatsiya Qilish

Tailwind CSS v4 klasslarini yig'ish yoki o'zgarishlarni kuzatib borish uchun:

```bash
# Bir martalik build
npm run build

# O'zgarishlarni avtomatik kuzatish (Watch mode)
npm run watch
```

---

## 📖 API Hujjatlari (Documentation)

Server ishga tushganidan so'ng API hujjatlarini ko'rish uchun:

- **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://127.0.0.1:8000/api/schema/redoc/`
- **OpenAPI Schema (JSON):** `http://127.0.0.1:8000/api/schema/`

---

## 📁 Loyiha Tuzilishi

```text
EduPlatform/
├── core/                   # Asosiy loyiha sozlamalari (settings, urls, wsgi, asgi)
├── users/                  # Foydalanuvchilar, profillar, SMS va Auth moduli
├── courses/                # Kurslar, kategoriyalar va izohlar moduli
├── lessons/                # Darslar va ta'lim kontentlari moduli
├── enrollments/            # Yozilishlar, to'lovlar, Payme webhook va Telegram bot
├── templates/              # Asosiy HTML shablonlar (base.html, home.html, login.html)
├── static/                 # Statik fayllar (CSS, JS, rasmlar)
│   ├── src/input.css       # Tailwind CSS kiritish fayli
│   └── css/output.css      # Kompilyatsiya qilingan CSS fayli
├── media/                  # Yuklangan fayllar (rasmlar, videolar)
├── Dockerfile              # Docker fayli
├── docker-compose.yml      # Docker Compose sozlamasi
├── requirements.txt        # Python bog'liqliklari ro'yxati
├── package.json            # Node.js / Tailwind CSS sozlamalari
└── manage.py               # Django boshqaruv skripti
```

---

## 📝 Litsenziya

Ushbu loyiha o'quv va amaliyot maqsadida yaratilgan. Istalgancha o'zgartirish va rivojlantirish mumkin.
