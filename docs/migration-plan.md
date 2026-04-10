# Plan migracji — bezpieczeństwo i refactor schematu

Ustalenia z przeglądu `database-schema.dbml`.
Migracje do wdrożenia po zakończeniu dyskusji.

---

## Architektura DEK — nowe kolumny w `users`

- Dodać kolumnę `encrypted_dek text NULLABLE` — DEK zaszyfrowany KEK-iem (wyprowadzonym z hasła przez PBKDF2)
- Dodać kolumnę `dek_salt varchar NULLABLE` — losowa sól do PBKDF2
- Nowy flow rejestracji: generowanie DEK po stronie klienta, szyfrowanie KEK-iem, wysłanie `encrypted_dek` + `dek_salt` na serwer
- Nowy flow logowania: pobranie `encrypted_dek` + `dek_salt`, odszyfrowanie DEK hasłem, trzymanie DEK w sessionStorage
- Nowy flow zmiany hasła: nowy KEK, re-szyfrowanie DEK, wysłanie nowego `encrypted_dek`
- Nowy flow odzyskiwania: reset hasła → user wpisuje recovery key (plain text DEK) → nowy KEK, nowy `encrypted_dek`
- UI: po rejestracji jednorazowy ekran z recovery key + przycisk "pobierz jako plik" (analogiczny do recovery codes 2FA)

## Zdjęcia paragonów (`receipts.image_path`, `receipt_images.image_path`)

- Backend: dodać `get_current_user` + sprawdzenie ownership do endpointu `GET /api/v1/receipts/images/{filename}` — zwracać 403 jeśli paragon nie należy do usera ani jego household
- Backend: przy zapisie zdjęcia szyfrować plik DEK-iem usera przed zapisem na dysk
- Frontend: po pobraniu zaszyfrowanego pliku odszyfrować DEK-iem z sessionStorage przed wyświetleniem
- Brak zmian w schemacie bazy — `image_path` nadal trzyma UUID filename

## Tabela `monthly_imports`

- Dodać kolumnę `file_hash varchar NULLABLE` — SHA-256 hash zaimportowanego pliku (do wykrywania duplikatów)
- Usunąć pliki z `/uploads/csv/` — żadne pliki nie powinny zostawać na dysku po imporcie
- Do dokończenia: zaimplementować parsowanie CSV w `import_csv.py` (aktualnie placeholder z TODO); plik przetwarzać w pamięci i usuwać natychmiast po parsowaniu

## Tabela `notifications`

- Dodać kolumnę `reference_id integer NULLABLE` — ID rekordu do pobrania po otwarciu powiadomienia (np. `medicine.id`, `todo_item.id`)
- Rozszerzyć `notification_type` o nowe wartości: `medicine_reminder`, `todo_reminder`, `food_expiry`, `workout_reminder` (brak zmiany schematu — to string, zmiana tylko w logice aplikacji)
- Scheduler: dla wrażliwych typów wpisywać generyczny `title` (np. "Medicine Notification") i puste `body`, ustawiać `reference_id`
- Frontend: po otwarciu powiadomienia pobrać rekord wskazany przez `reference_id` + `notification_type` i odszyfrować DEK-iem

## Tabela `shopping_list_items`

- `name`, `notes` — szyfrowane AES-256 DEK-iem po stronie klienta
- `category` — szyfrować DEK-iem jeśli wolny tekst; plain text jeśli zamknięty słownik (do weryfikacji)

## Tabela `todo_items`

- `title`, `description` — szyfrowane AES-256 DEK-iem po stronie klienta

## Tabela `medicines`

- `name`, `description`, `dosage` — szyfrowane AES-256 DEK-iem po stronie klienta

## Tabela `journal_entries`

- `notes` — szyfrowane AES-256 DEK-iem po stronie klienta

## Tabela `journal_items`

- `content` — szyfrowane AES-256 DEK-iem po stronie klienta
- `category` — plain text (zamknięty słownik)

## Tabela `journal_reports`

- `data` — szyfrowane AES-256 DEK-iem po stronie klienta

## Tabela `transactions`

- `description` i `notes` — wartości szyfrowane AES-256 DEK-iem po stronie klienta przed wysłaniem na serwer
- `category`, `amount`, `date`, `payment_method` — bez zmian (plain text)
- Usunąć wyszukiwanie full-text po `description` i `notes` z frontendu i backendu

## Tabela `categories` + `user_categories` + `household_categories`

- Usunąć kolumnę `budget_limit` z tabeli `categories`
- Dodać kolumnę `budget_limit float NULLABLE` do tabeli `user_categories`
- Dodać kolumnę `budget_limit float NULLABLE` do tabeli `household_categories`
- Backend: zaktualizować `AnalyticsService.get_budget_status()` i `get_categories_with_budget()` — czytać `budget_limit` z `user_categories` / `household_categories` zamiast z `categories`
- Backend: zaktualizować `CategoryUpdate` schema i `update_category()` — zapis limitu do junction table zamiast do `categories`
- Frontend: bez zmian w UI — zmiana tylko w tym co jest wysyłane i skąd czytane

## Tabela `households`

- Dodać kolumnę `encryption_salt varchar NOT NULL` — losowy salt generowany przy tworzeniu household, używany przez PBKDF2 po stronie klienta do wyprowadzenia klucza AES-256
- `name` i `description` będą trzymane jako zaszyfrowany tekst (base64 encrypted) zamiast plain text — brak zmiany typu kolumny, tylko zawartość będzie zaszyfrowana

## Tabela `oauth_device_codes`

- Rename `device_code` → `device_code_hash`
- Rename `user_code` → `user_code_hash`
- Zmigrować istniejące wartości: zahashować SHA-256 lub unieważnić wszystkie aktywne (bezpieczniejsze)

## Tabela `oauth_access_tokens`

- Rename `access_token` → `access_token_hash`
- Rename `refresh_token` → `refresh_token_hash`
- Zmigrować istniejące wartości: zahashować SHA-256 wszystkie aktywne tokeny (lub po prostu unieważnić wszystkie — przy migracji bezpieczniejsze)

## Tabela `vouchers`

- Rename kolumny `code` → `code_hash`
- Dodać kolumnę `hash_version varchar(20) NOT NULL DEFAULT 'bcrypt_v1'`
- Zmigrować istniejące wartości: zahashować plain text kody bcryptem, ustawić `hash_version = 'bcrypt_v1'`
- Nowa funkcjonalność (poza migracją): endpoint `POST /vouchers/{id}/send-email` — wysyła plain text kodu na wskazany adres, kod nigdy nie wraca do UI

## Tabela `users`

- Rename kolumny `name` → `nick`
- Typ: `varchar(20)`
- Dodać CHECK constraint: `length(nick) >= 8 AND length(nick) <= 20`

---

## Moduł Fitness — tłumaczenie i presety treningowe

### i18n — tłumaczenie modułu fitness

- Przetłumaczyć cały moduł fitness na polski w plikach `frontend/locales/pl.json` i `en.json`
- Dotyczy: nazwy ćwiczeń w UI, etykiety formularzy, komunikaty błędów, przyciski, statusy treningu

### Presety treningowe — nowe tabele

Nowe tabele do dodania w kolejnej migracji:

**`workout_presets`**
- `id` integer PK
- `user_id` integer FK → `users.id` CASCADE
- `name` varchar NOT NULL — nazwa presetu (np. "Mój standardowy trening")
- `created_at` varchar
- `updated_at` varchar

**`workout_preset_exercises`**
- `id` integer PK
- `preset_id` integer FK → `workout_presets.id` CASCADE
- `name` varchar NOT NULL — nazwa ćwiczenia
- `sets` integer NOT NULL
- `reps` integer NOT NULL
- `weight_kg` float NOT NULL
- `rest_seconds` integer NULLABLE
- `notes` text NULLABLE
- `position` integer NOT NULL DEFAULT 0 — kolejność ćwiczeń w presecie

**Działanie:**
- Preset to tylko szablon — nie ma statusu "ukończony", nie jest treningiem
- `POST /workouts/from-preset/{preset_id}` — tworzy nowy trening (`workouts` + `exercises` + `exercise_sets`) z danymi z presetu, wszystkie serie oznaczone jako `completed = false`
- Po załadowaniu preset użytkownik zarządza treningiem normalnie — może dodawać/usuwać ćwiczenia, zmieniać serie, powtórzenia, ciężar

