# Lockiner — kontekst debugowania (2026-03-06)

## Problem do rozwiązania

`/oauth/authorize` zwraca 404 — nginx nie routuje `/oauth/` do backendu FastAPI.

## Architektura

```
Internet → nginx (VPS) → frontend Nuxt  :3000  (docker: lockiner-frontend)
                       → backend FastAPI :8000  (docker: lockiner-backend)
```

Backend i frontend są w Dockerze, nasłuchują tylko na `127.0.0.1`.
Nginx pośredniczy jako reverse proxy.

## Co jest w backendzie

- FastAPI z routerem `/oauth/` zarejestrowanym w `backend/app/main.py`
- Endpointy: `GET /oauth/authorize`, `POST /oauth/token`, `GET /oauth/userinfo`
- Backend działa poprawnie (health check OK)

## Diagnoza

Nginx routuje `/api/` → backend (port 8000), resztę → frontend (port 3000).
Ścieżka `/oauth/` nie ma reguły — trafia do Nuxt → 404.

## Fix do zastosowania

Znaleźć nginx site config (prawdopodobnie `/etc/nginx/sites-enabled/lockiner.com`
lub `/etc/nginx/conf.d/lockiner.conf`) i dodać blok:

```nginx
location /oauth/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Po zmianie: `nginx -t && systemctl reload nginx`

## Weryfikacja po fixie

```bash
curl -s -o /dev/null -w "%{http_code}" "https://lockiner.com/oauth/userinfo"
# Oczekiwany wynik: 401 lub 403 (nie 404) — znaczy że backend odpowiada
```

## Inne potencjalne problemy

- Jeśli jest też `/oauth` bez trailing slash — dodać osobny `location = /oauth`
- Sprawdzić czy tabele OAuth istnieją w bazie:
  ```bash
  docker exec lockiner-postgres psql -U lockiner -d lockiner_db \
    -c "\dt oauth*"
  ```
- Sprawdzić czy klient `byczq-desktop` jest w tabeli `oauth_clients`:
  ```bash
  docker exec lockiner-postgres psql -U lockiner -d lockiner_db \
    -c "SELECT * FROM oauth_clients;"
  ```
  Jeśli pusta — trzeba go dodać (patrz niżej).

## Seed danych OAuth — klient byczq-desktop

Jeśli tabela `oauth_clients` jest pusta, wstaw rekord:

```bash
docker exec lockiner-postgres psql -U lockiner -d lockiner_db -c "
INSERT INTO oauth_clients (client_id, client_name, redirect_uris, is_active, created_at)
VALUES (
  'byczq-desktop',
  'Byczq Desktop',
  'http://localhost:9876/callback',
  true,
  NOW()::text
) ON CONFLICT DO NOTHING;
"
```

## Pliki kluczowe

| Plik | Rola |
|------|------|
| `backend/app/routers/oauth.py` | Endpointy OAuth (authorize, token, userinfo) |
| `backend/app/services/oauth.py` | Logika OAuth (PKCE, tokeny) |
| `backend/app/migrations/versions/fbc51d6de763_add_oauth_tables.py` | Migracja tabel OAuth |
| `backend/app/main.py` | Rejestracja routerów FastAPI |
| `docker-compose.prod.yml` | Backend :8000, Frontend :3000 |
