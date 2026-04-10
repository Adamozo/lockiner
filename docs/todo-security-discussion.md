# TODO — bezpieczeństwo i prywatność danych

Lista wszystkich uwag z `database-schema.dbml` do omówienia.
Status: `[ ]` = nieomówione, `[x]` = omówione/zdecydowane

---

## 1. Użytkownicy (`users`)

### 1.1 `users.name` — szyfrowanie imienia
- [x] **Decyzja:** imię/nazwisko nie jest potrzebne. Pole zamienić na `nick` — pseudonim wybrany przez użytkownika, min. 8, max. 20 znaków. Nick nie jest wrażliwy, nie wymaga szyfrowania.
- Wymagana migracja: rename kolumny `name` → `nick` + dodanie constraint długości.

### 1.2 `users.recovery_codes_hash` — co z tym?
- [x] **OK — brak akcji.** Kody są hashowane bcryptem przed zapisem (`two_factor.py: _hash_recovery_codes()`). W bazie siedzi JSON array z bcrypt hashami. Administrator nie może odtworzyć oryginalnych kodów. Dodatkowo każdy użyty kod jest od razu usuwany z listy (jednorazowe).

---

## 2. Vouchery (`vouchers`)

### 2.1 `vouchers.code` — haszowanie kodów voucherów
- [x] **Decyzja:** przejść na przechowywanie wyłącznie hasha kodu.
  - Kolumnę `code` zastąpić `code_hash` + `hash_version`
  - Kod plain text pokazywany użytkownikowi tylko raz (przy zakupie / generowaniu) lub wysyłany emailem
  - Panel admina: lista voucherów bez wartości kodu — widoczny status, daty, kto użył
  - Nowa funkcjonalność: przycisk "wyślij na email" zamiast wyświetlania kodu w UI
  - `hash_version` potrzebny na wypadek rotacji algorytmu hashującego

---

## 3. OAuth

### 3.1 `oauth_clients` — dodawanie integracji przez UI
- [x] **Decyzja:** tylko admin rejestruje klientów OAuth. Schemat tabeli wystarczający, żadnych zmian. Potrzebny jedynie panel admina z formularzem CRUD (nazwa, redirect URIs, aktywny/nieaktywny).

### 3.2 `oauth_access_tokens` — tokeny plain text
- [x] **Decyzja:** hashować tokeny SHA-256 przed zapisem do bazy.

**Jak to zaimplementować:**
- Przy wystawianiu tokena: generuj losowy token (`secrets.token_urlsafe(32)`), wyślij plain text klientowi, zapisz do bazy `hashlib.sha256(token.encode()).hexdigest()`
- Przy weryfikacji tokena: zahashuj token z requesta i szukaj po hashu w bazie — `SELECT * FROM oauth_access_tokens WHERE access_token = sha256($1)`
- To samo dla `refresh_token`
- Rename kolumn dla jasności: `access_token` → `access_token_hash`, `refresh_token` → `refresh_token_hash`
- SHA-256 wystarczy (nie bcrypt) — tokeny są losowe i długie, więc nie ma ryzyka ataku słownikowego; SHA-256 jest też znacznie szybszy przy weryfikacji

### 3.3 `oauth_authorization_codes` — kod i code_challenge
- [x] **`code` — brak akcji.** Kod jest jednorazowy i ważny ~60 sekund. Ryzyko wycieku w tym oknie czasowym jest minimalne — hashowanie byłoby overengineering bez realnej korzyści.
- [x] **`code_challenge` / `code_challenge_method` — brak akcji.** Wartości publiczne z PKCE flow, nie wymagają ochrony.

### 3.4 `oauth_device_codes` — device_code i user_code
- [x] **Decyzja:** hashować oba — `device_code` i `user_code` — SHA-256 przed zapisem do bazy.
- Implementacja: plain text zwracany użytkownikowi tylko w odpowiedzi API w momencie inicjacji flow (wyświetlany na ekranie urządzenia), w bazie zapisywany wyłącznie hash. Przy weryfikacji — zahashuj i porównaj z bazą.

---

## 4. Gospodarstwa domowe (`households`)

### 4.1 `households.name` i `households.description`
- [x] **Decyzja:** client-side encryption kluczem wyprowadzonym z hasła gospodarstwa.
  - Przy tworzeniu household użytkownik ustawia hasło — po stronie klienta PBKDF2 wyprowadza klucz AES-256, którym szyfrowane są `name` i `description` przed wysłaniem na serwer
  - Hasło nigdy nie trafia na serwer
  - Klucz trzymany w sessionStorage — użytkownik wpisuje hasło raz na sesję
  - Przy akceptacji zaproszenia nowy członek musi podać hasło (przekazywane osobiście)
  - Zmiana hasła = wyczyszczenie `name` i `description`, użytkownik ustawia od nowa (to tylko kosmetyczne dane, nie jest to problem)
  - Warning przy tworzeniu: bez hasła nie ma dostępu do nazwy i opisu

---

## 5. Finanse — kategorie (`categories`)

### 5.1 Architektura kategorii — globalnie czy per-user?
- [x] **Bug potwierdzony.** `budget_limit` w globalnej tabeli `categories` — zmiana przez jednego usera wpływa na wszystkich. Kategorie seed (Spożywcze, Transport itp.) nie mają właściciela, więc każdy user może edytować ich limit.
- **Decyzja:** usunąć `budget_limit` z tabeli `categories`, dodać kolumnę `budget_limit` do `user_categories` i `household_categories`. Każdy user/household ma własny limit per kategoria. Analitykę (`get_budget_status`) zaktualizować żeby czytała limit z junction tables.

---

## 6. Finanse — transakcje (`transactions`)

### 6.1 `transactions.description`, `.category`, `.notes` — szyfrowanie
- [x] **Decyzja:** client-side encryption kluczem DEK per-user (patrz niżej — architektura DEK).
  - `description` i `notes` — szyfrowane AES-256 DEK-iem, bez wyszukiwania full-text (usunąć tę funkcję)
  - `category` — plain text (zamknięty słownik, filtrowanie po pełnej nazwie działa normalnie)
  - `amount`, `date`, `payment_method` — plain text (nieczułe lub zamknięty słownik)

---

### Architektura DEK (Data Encryption Key) — dotyczy wszystkich szyfrowanych danych usera

Jeden DEK szyfruje wszystkie prywatne dane usera (transakcje, dziennik, leki, todo itd.).

**Flow:**
1. Przy rejestracji: generowany losowy DEK (256-bit)
2. Z hasła usera + losowej soli wyprowadzany KEK (Key Encryption Key) przez PBKDF2
3. DEK szyfrowany KEK-iem, zapisywany w `users.encrypted_dek`; sól zapisywana w `users.dek_salt`
4. Przy logowaniu: hasło → KEK → odszyfrowanie DEK → DEK trzymany w sessionStorage
5. Zmiana hasła = nowy KEK, re-szyfrowanie DEK — dane bez zmian

**Recovery key:**
- Przy rejestracji plain text DEK pokazywany userowi **jednorazowo** w UI z możliwością pobrania jako plik tekstowy
- Komunikat: "zapisz to w bezpiecznym miejscu, nie pokażemy tego ponownie"
- Jeśli user zapomni hasła: reset hasła → wpisanie zapisanego recovery key → gotowe
- Recovery key nigdy nie trafia na serwer ani do emaila
- UX analogiczny do recovery codes 2FA (już znany userowi)

---

## 7. Finanse — importy (`monthly_imports`)

### 7.1 Co dzieje się z importowanymi plikami CSV/XML?
- [x] **Import CSV niezaimplementowany do końca** — parsowanie to placeholder z TODO, żadne transakcje nie są faktycznie importowane. Do dokończenia.
- **Aktualny stan:** plik zapisywany na dysk (`/uploads/csv/UUID.csv`) na stałe, nigdy nie usuwany. Brak endpointu do pobierania, ale pliki dostępne dla każdego z dostępem do filesystemu serwera.
- **Decyzja:** przy dokończeniu implementacji — plik przetwarzany w pamięci, natychmiast usuwany po parsowaniu. W `monthly_imports` zostawić tylko metadata: oryginalna nazwa pliku, hash pliku (do wykrywania duplikatów), data, liczba transakcji. Żadnych plików na dysku.

---

## 8. Paragony (`receipts`, `receipt_images`)

### 8.1 Zdjęcia paragonów — dostęp i przechowywanie
- [x] **Krytyczny bug:** endpoint `GET /api/v1/receipts/images/{filename}` nie wymaga uwierzytelnienia — każdy znający UUID pliku może pobrać dowolne zdjęcie.
- **Decyzja:** dwa mechanizmy jednocześnie:
  1. **Kontrola dostępu** — dodać `get_current_user` do endpointu + sprawdzenie ownership (czy paragon należy do usera lub jego household) przed zwróceniem pliku
  2. **Szyfrowanie plików** — zdjęcia szyfrowane DEK-iem usera przed zapisem na dysk; odszyfrowanie po stronie klienta po pobraniu. Admin serwera widzi tylko zaszyfrowane bajty.

### 8.2 `receipts.merchant` — szyfrowanie nazwy sprzedawcy
- [x] **Brak akcji.** Skoro email jest zahashowany, nick to pseudonim, a zdjęcie paragonu zaszyfrowane i chronione auth — nazwa sprzedawcy sama w sobie nie ujawnia tożsamości użytkownika. Nawet przy dostępie do bazy nie da się powiązać merchanty z konkretną osobą.

---

## 9. Dziennik (`journal_entries`, `journal_items`, `journal_reports`)

### 9.1 `journal_entries.notes` — szyfrowanie notatek
- [x] **Decyzja:** szyfrować DEK-iem usera.

### 9.2 `journal_items.content` — szyfrowanie treści dziennika
- [x] **Decyzja:** szyfrować DEK-iem usera. `category` w journal_items to zamknięty słownik — plain text, bez szyfrowania.

### 9.3 `journal_reports.data` — szyfrowanie danych raportu
- [x] **Decyzja:** szyfrować DEK-iem usera.

---

## 10. Leki (`medicines`)

### 10.1 `medicines.name` i `medicines.description` — szyfrowanie
- [x] **Decyzja:** szyfrować DEK-iem usera — `name`, `description`, `dosage`. Dane medyczne wrażliwe niezależnie od tego czy wiemy kto je bierze.

---

## 11. Todo (`todo_lists`, `todo_items`, `todo_notification_rules`)

### 11.1 `todo_lists.title` — szyfrowanie
- [x] **Brak akcji.** Tytuł listy nie wymaga szyfrowania.

### 11.2 `todo_items.title` i `.description` — szyfrowanie
- [x] **Decyzja:** szyfrować DEK-iem usera — `title` i `description`.

### 11.3 `todo_notification_rules.label` — szyfrowanie
- [x] **Brak akcji.** Etykieta reguły powiadomień nie wymaga szyfrowania.

---

## 12. Zakupy (`shopping_lists`, `shopping_list_items`)

### 12.1 `shopping_lists.name` i `.store_name` — szyfrowanie
- [x] **Brak akcji.** Nazwa listy i sklep nie ujawniają tożsamości — ten sam argument co `receipts.merchant`.

### 12.2 `shopping_list_items.name` i `.notes` — szyfrowanie
- [x] **Decyzja:** szyfrować DEK-iem usera — co konkretnie kupujesz może być wrażliwe.

### 12.3 `shopping_list_items.category` — czy można szyfrować?
- [x] **Decyzja:** szyfrować DEK-iem jeśli wolny tekst wpisywany przez usera, plain text jeśli zamknięty słownik. Do weryfikacji przy implementacji.

---

## 13. Powiadomienia (`notifications`)

### 13.1 Szyfrowanie powiadomień a wysyłka do wielu osób
- [x] **Problem zidentyfikowany:** scheduler wpisuje wrażliwe dane plain text do `notifications.body` — np. `"Time to take {medicine.name}"` lub `body = item.title`.
- **Decyzja — Opcja B:** powiadomienia wrażliwe (medicine, todo) wysyłane z generycznym tytułem i body bez treści. Po otwarciu apka pobiera właściwy rekord i odszyfrowuje DEK-iem lokalnie.
- Rozszerzyć `notification_type` o granularne typy: `medicine_reminder`, `todo_reminder`, `food_expiry`, `workout_reminder` itp. — apka wie co pobrać na podstawie typu
- Dodać kolumnę `reference_id integer NULLABLE` — ID konkretnego rekordu do pobrania (np. `medicine.id`, `todo_item.id`)
- Powiadomienia systemowe (admin broadcast, backup errors) — plain text, nie zawierają wrażliwych danych per-user

---

## 14. Backup (`backup_settings`, `household_backup_settings`)

### 14.1 Hasło do backupu i dane backupu
- [x] **OK — brak akcji.** Backup zaimplementowany solidnie — dwuwarstwowe szyfrowanie:
  1. Hasło użytkownika szyfrowane Fernetem (`ENCRYPTION_KEY` z env) → `encrypted_password` w bazie
  2. Dane backupu szyfrowane AES-256 tym hasłem → zaszyfrowany ZIP na Google Drive
- Znane ograniczenie: przejęcie serwera (env + baza) pozwala odszyfrować hasło i otworzyć backup. Decyzja: akceptowalne — auto-backup wymaga hasła po stronie serwera.
