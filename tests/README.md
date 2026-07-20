# Testlar

Backend testlari `pytest` + `pytest-django` ustida ishlaydi. API testlari DRF'ning
`APITestCase` klassida, model/serializer/yordamchi funksiya testlari esa sof pytest
uslubida (fixture va `parametrize` bilan) yozilgan.

## O'rnatish

```bash
pip install -r requirements-dev.txt
```

## Ishga tushirish

```bash
# Butun to'plam + coverage (terminal, HTML va XML report)
pytest

# Coverage'siz, tezroq
pytest --no-cov

# Bitta fayl / bitta test
pytest tests/test_orders_api.py
pytest tests/test_orders_api.py::OrderAcceptAPITestCase::test_cannot_accept_twice

# Nomi bo'yicha tanlash
pytest -k "contact_unlocked"
```

`manage.py test` orqali ham ishlaydi:

```bash
python manage.py test tests --settings=config.settings_test
```

## Coverage report

`pytest` tugagach quyidagilar hosil bo'ladi:

| Fayl | Nima |
|---|---|
| `htmlcov/index.html` | HTML report — brauzerda oching |
| `coverage.xml` | CI uchun (Codecov, SonarQube va h.k.) |
| terminal | `--cov-report=term-missing` — qamrab olinmagan qatorlar |

```bash
start htmlcov/index.html      # Windows
```

Sozlamalar `.coveragerc` faylida: migratsiyalar, testlar va `wsgi/asgi` hisobdan
chiqarilgan, `branch = True` yoqilgan.

## Tuzilishi

| Fayl | Nimani tekshiradi |
|---|---|
| `factories.py` | factory-boy fabrikalari (User, MasterProfile, Workshop, Order, Review, ...) |
| `base.py` | `BaseAPITestCase` — `auth()`, `logout()`, `assertKeys()` yordamchilari |
| `../conftest.py` | pytest fixture'lari: `api_client`, `auth_client`, `customer`, `master_profile`, ... |
| `test_users_api.py` | ro'yxatdan o'tish, JWT token/refresh, `/me`, telefon tasdiqlash |
| `test_masters_api.py` | yaqin ustalar, masofa bo'yicha saralash, haversine, usta profili |
| `test_services_api.py` | kategoriyalar, usta xizmatlari, filtrlash |
| `test_orders_api.py` | buyurtma yaratish/ko'rish, accept/complete, kontakt ochilishi |
| `test_reviews_api.py` | sharh qoidalari, reyting qayta hisoblanishi |
| `test_adminpanel_api.py` | `IsAdmin` ruxsati, boshqaruv endpointlari, statistika |
| `test_serializers_unit.py` | serializer'lar HTTP qatlamisiz |

## Test bazasi

`config/settings_test.py` Postgres o'rniga xotiradagi SQLite'ni ishlatadi, shuning
uchun testlar uchun ishlab turgan Postgres yoki `.env` fayl shart emas.
