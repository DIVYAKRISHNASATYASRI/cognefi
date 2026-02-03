
---

## 🔐 Role Model

| Role | Description |
|----|----|
| SUPER_ADMIN | Platform-level admin (no tenant) |
| TENANT_ADMIN | Admin of a single tenant |
| USER | Regular tenant user |

> Role enforcement is handled by **Cerbos** (not inside this service).

---

## 📡 API Overview

### Health
- `GET /health`

---

### Tenants
- `GET /tenants`
- `POST /tenants`
- `PATCH /tenants/{tenant_id}`
- `PATCH /tenants/{tenant_id}/status`

---

### Users
- `GET /users`
- `GET /users?tenant_id={uuid}`
- `POST /users`
- `PATCH /users/{user_id}`
- `PATCH /users/{user_id}/status`

---

### Auth Context
- `GET /me?user_id={uuid}`

> ⚠️ In production, `user_id` will come from **JWT**, not query params.

---

## 🛡️ Soft Delete Strategy

This service **never hard-deletes** records.

| Entity | Status Values |
|----|----|
| Tenant | `active`, `suspended` |
| User | `active`, `disabled` |

This preserves:
- Audit history
- Workflow execution logs
- Compliance data

---

## 🔑 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/neondb?sslmode=require
