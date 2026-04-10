# Analiza danych wrażliwych — prywatność użytkowników

> Wygenerowano na podstawie migracji Alembic (001–023).
> Data przeglądu: 2026-03-23

---

## Dane już zabezpieczone

| Tabela | Kolumna | Metoda |
|--------|---------|--------|
| `users` | `email_hash` | hash (jednodrożny) |
| `users` | `password_hash` | hash (bcrypt) |
| `users` | `totp_secret_encrypted` | szyfrowanie symetryczne |
| `users` | `recovery_codes_hash` | hash |
| `user_api_keys` | `encrypted_key` | szyfrowanie symetryczne |

---

## Krytyczne — niezabezpieczone, wymagają szyfrowania

### Finanse i paragony

| Tabela | Kolumna | Dlaczego wrażliwe |
|--------|---------|-------------------|
| `transactions` | `description` (Text) | tytuły przelewów bankowych — mogą zawierać pełne opisy jak nazwy aptek, klinik, sklepów |
| `transactions` | `notes` | notatki użytkownika do transakcji |
| `receipts` | `merchant` | nazwa sklepu/sprzedawcy |
| `receipts` | `items_json` | lista produktów z paragonu — rdzeń problemu prywatności |
| `receipts` | `raw_ocr_response` | surowy wynik OCR — może zawierać pełną treść paragonu |
| `food_pending_import_items` | `original_name` | oryginalne nazwy produktów importowane z paragonu |
| `food_pending_import_items` | `ai_suggested_name` | sugestia AI — może ujawniać kontekst produktu |

### Dziennik osobisty

| Tabela | Kolumna | Dlaczego wrażliwe |
|--------|---------|-------------------|
| `journal_items` | `content` | treść wpisów dziennika — najbardziej prywatne dane w całej aplikacji |
| `journal_entries` | `notes` | dodatkowe notatki do wpisu |
| `journal_entries` | `mood_score` | dane zdrowia psychicznego |
| `journal_reports` | `data` | zagregowane dane dziennika (JSON) |

### Leki i suplementy

| Tabela | Kolumna | Dlaczego wrażliwe |
|--------|---------|-------------------|
| `medicines` | `name` | nazwa leku pośrednio ujawnia diagnozę |
| `medicines` | `description` | opis/wskazania leku |
| `medicines` | `dosage` | dawkowanie |

### Dane ciała i zdrowia

| Tabela | Kolumna | Dlaczego wrażliwe |
|--------|---------|-------------------|
| `weight_entries` | `weight_kg` | masa ciała |
| `weight_entries` | `body_fat_percentage` | procent tkanki tłuszczowej |
| `weight_entries` | `notes` | notatki do pomiaru |
| `body_measurement_entries` | `bicep_cm`, `waist_cm`, `thigh_cm`, `calf_cm`, `chest_cm` | dokładne wymiary ciała |
| `body_measurement_entries` | `notes` | notatki do pomiaru |
| `user_body_profiles` | `height_cm` | wzrost użytkownika |
| `food_consumption_log` | `notes`, `meal_type` | co i kiedy jedzą |
| `food_consumption_log` | `calories`, `protein`, `carbohydrates`, `fat` | dane żywieniowe |
| `food_consumption_log` | `product_name`, `off_product_code` | konkretne produkty spożywcze |

---

## Średnia wrażliwość

| Tabela | Kolumna | Uwaga |
|--------|---------|-------|
| `users` | `name` | prawdziwe imię/nazwisko — plain text mimo że email jest zahashowany |
| `todo_items` | `title`, `description` | zadania mogą ujawniać rutynę życiową i problemy osobiste |
| `shopping_list_items` | `name`, `notes` | lista zakupów — podobny problem jak `items_json` w paragonach |
| `shopping_lists` | `name`, `store_name`, `notes` | metadata list zakupów |
| `workouts` | `notes` | notatki treningowe |
| `exercises` | `notes` | notatki do ćwiczeń |
| `meditation_sessions` | `notes` | prywatne notatki medytacji |
| `food_inventory` | `notes` | notatki do produktów w lodówce/spiżarni |

---

## Rekomendacje techniczne

### Hashing vs szyfrowanie

- **Hashing** (bcrypt, SHA-256) — tylko dla danych, których nie trzeba odczytać z powrotem (email, hasło). Nieodwracalne.
- **Szyfrowanie symetryczne** (AES-256-GCM / Fernet) — dla wszystkich pól, które użytkownik musi zobaczyć. Klucz szyfrowania trzymany oddzielnie od bazy.

### Priorytet wdrożenia

**Faza 1 — najwyższy priorytet:**
1. `transactions.description` — tytuły transakcji bankowych
2. `receipts.items_json` + `raw_ocr_response` — produkty z paragonów
3. `journal_items.content` + `journal_entries.notes` — treść dziennika
4. `medicines.name` + `medicines.description` — nazwy leków

**Faza 2:**
5. `food_consumption_log` — historia spożycia
6. `body_measurement_entries` + `weight_entries` — dane biometryczne
7. `food_pending_import_items.original_name`

**Faza 3:**
8. `todo_items.title` + `description`
9. `shopping_list_items.name`
10. `users.name`

### Uwagi implementacyjne

- Szyfrowanie powinno odbywać się na poziomie **warstwy serwisowej** (przed zapisem do repozytorium), nie w bazie danych.
- Pola szyfrowane nie mogą być używane w klauzulach `WHERE` / `ORDER BY` bezpośrednio — wymaga przemyślenia strategii wyszukiwania (np. osobne zahashowane tokeny do wyszukiwania).
- Dane zagregowane / statystyczne (np. sumy transakcji per kategoria) mogą pozostać niezaszyfrowane jeśli nie zawierają treści identyfikujących.
- Rozważyć `pgcrypto` lub szyfrowanie po stronie aplikacji (preferowane — klucz nigdy nie trafia do bazy).
