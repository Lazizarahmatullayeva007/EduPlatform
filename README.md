# EduPlatform 🎓

Zamonaviy onlayn ta'lim platformasi — Django va Django REST Framework asosida qurilgan, kurslar, darslar, to'lovlar va SMS/Email integratsiyasini o'z ichiga oladi.

## 📋 Loyiha haqida

EduPlatform — o'qituvchilarga kurslar yaratish, darslar qo'shish imkonini beruvchi, talabalarga esa kurslarni topib, yozilib, o'rganish imkonini beruvchi to'liq funksional ta'lim platformasi.

## ✨ Asosiy imkoniyatlar

### Foydalanuvchilar
- Ro'yxatdan o'tish, login (rol: talaba / o'qituvchi)
- Profil sahifasi (rasm, bio, telefon raqami)
- SMS orqali telefon raqamini tasdiqlash

### Kurslar
- Kurslar yaratish, tahrirlash, o'chirish (o'qituvchi)
- Nashr qilish / qoralamaga qaytarish
- Filtrlash, qidiruv, saralash (narx, kategoriya bo'yicha)
- Sig'im (max_students) va bo'sh o'rinlarni avtomatik hisoblash

### Darslar
- Video (fayl yuklash yoki YouTube havolasi) va matn turidagi darslar
- Video davomiyligini avtomatik aniqlash
- Faqat kursga yozilgan talabalar uchun ochiq

### To'lov va yozilish
- Bepul va pullik kurslar
- To'lov simulyatsiyasi (Payme integratsiyasiga tayyor, HMAC imzo bilan himoyalangan)
- Kursga yozilish / chiqish

### Integratsiyalar
- **Telegram** — yangi yozilish haqida o'qituvchiga avtomatik xabar (Django Signals orqali)
- **Email** — kursga yozilganda HTML formatdagi xush kelibsiz emaili
- **SMS (Eskiz.uz)** — telefon raqamini tasdiqlash kodi

### API
- To'liq DRF API (JWT autentifikatsiya, Djoser)
- Swagger / Redoc orqali interaktiv hujjatlar

### Sifat va xavfsizlik
- Avtomatik testlar (`python manage.py test`)
- GitHub Actions orqali CI (har bir push'da testlar avtomatik ishga tushadi)
- Custom permission'lar, HMAC webhook imzosi, rate-limit'ga tayyor tuzilma

## 🛠 Texnologiyalar

- **Backend:** Django 6, Django REST Framework
- **Baza:** PostgreSQL
- **Autentifikatsiya:** JWT (SimpleJWT + Djoser)
- **Frontend:** Django Templates + Tailwind CSS
- **Boshqa:** Celery-ga tayyor tuzilma, Docker (Dockerfile, docker-compose.yml), Gunicorn + Whitenoise (production uchun)

## 🚀 O'rnatish

### 1. Repositoryni yuklab oling
```bash
git clone https://github.com/Lazizarahmatullayeva007/EduPlatform.git
cd EduPlatform
```

### 2. Virtual muhit yarating va faollashtiring
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux
```

### 3. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 4. `.env` faylini yarating

Loyiha papkasida `.env` nomli fayl yarating va quyidagilarni to'ldiring:

```env
DB_NAME=eduplatform
DB_USER=eduplatform_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=your-secret-key
DEBUG=True

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

ESKIZ_EMAIL=
ESKIZ_PASSWORD=

PAYME_WEBHOOK_SECRET=dev-secret-key-change-in-production

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Migratsiyalarni bajaring
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Superuser yarating (ixtiyoriy)
```bash
python manage.py createsuperuser
```

### 7. Serverni ishga tushiring
```bash
python manage.py runserver
```

Sayt: `http://127.0.0.1:8000/`

### 8. (Ixtiyoriy) Tailwind CSS'ni kuzatish rejimida ishga tushiring
```bash
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
```

## 📚 API hujjatlari

Server ishga tushgandan so'ng:
- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- Redoc: `http://127.0.0.1:8000/api/schema/redoc/`

## 🧪 Testlarni ishga tushirish

```bash
python manage.py test
```

## 📁 Loyiha tuzilishi
