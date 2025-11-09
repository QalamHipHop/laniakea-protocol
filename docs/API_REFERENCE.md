# 📗 LaniakeA Protocol - مرجع API

**نسخه:** v0.0.01
**آخرین به‌روزرسانی:** 2025-11-09

---

## 🚀 مقدمه

این سند، مرجع کامل API برای **LaniakeA Protocol** است. تمام endpoints، مدل‌های داده و کدهای وضعیت در اینجا مستند شده‌اند.

**URL پایه:** `http://localhost:8000/api/v1`

### احراز هویت

تمام درخواست‌ها به جز `/auth/register` و `/auth/login` نیاز به یک `Authorization` header با یک JWT token دارند:

```
Authorization: Bearer <your_jwt_token>
```

---

## 📦 مدل‌های داده

### SCDA

```json
{
  "identity": "string",
  "username": "string",
  "complexity_index": "float",
  "energy": "float",
  "tier": "integer",
  "level": "integer",
  "position_8d": "array[float]",
  "knowledge_vector": "object",
  "created_at": "string (ISO 8601)"
}
```

### Transaction

```json
{
  "transaction_id": "string",
  "sender": "string",
  "recipient": "string",
  "amount": "float",
  "timestamp": "float",
  "metadata": "object"
}
```

### Block

```json
{
  "index": "integer",
  "timestamp": "float",
  "transactions": "array[Transaction]",
  "previous_hash": "string",
  "hash": "string",
  "hypercube_coordinates": "array[float]"
}
```

---

## 🌐 Endpoints

### 🔑 احراز هویت (`/auth`)

#### `POST /auth/register`

ایجاد یک کاربر و SCDA جدید.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (201 Created):**

```json
{
  "message": "User created successfully",
  "scda_id": "string"
}
```

#### `POST /auth/login`

ورود به سیستم و دریافت JWT token.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

### 🧬 SCDA (`/scda`)

#### `GET /scda/{scda_id}`

دریافت اطلاعات یک SCDA.

**Response (200 OK):** `SCDA`

#### `GET /scda/me`

دریافت اطلاعات SCDA کاربر فعلی.

**Response (200 OK):** `SCDA`

#### `GET /scda/{scda_id}/dna`

دریافت DNA دیجیتال یک SCDA.

**Response (200 OK):**

```json
{
  "genes": "array[object]",
  "genetic_diversity": "float"
}
```

---

### 🎯 مسائل (`/problems`)

#### `GET /problems`

دریافت لیست مسائل موجود.

**Query Parameters:**
- `difficulty_min` (float, optional)
- `difficulty_max` (float, optional)
- `domain` (string, optional)

**Response (200 OK):** `array[Problem]`

#### `POST /problems/solve`

ارسال راه‌حل برای یک مسئله.

**Request Body:**

```json
{
  "problem_id": "string",
  "solution": "string"
}
```

**Response (200 OK):**

```json
{
  "message": "Solution submitted for validation",
  "validation_id": "string"
}
```

---

### 🔷 بلاکچین (`/blockchain`)

#### `GET /blockchain/blocks`

دریافت لیست بلوک‌ها.

**Response (200 OK):** `array[Block]`

#### `POST /blockchain/transactions`

ارسال یک تراکنش جدید.

**Request Body:** `Transaction`

**Response (202 Accepted):**

```json
{
  "message": "Transaction submitted to the pool",
  "transaction_id": "string"
}
```

---

### 💎 بازار دانش (`/marketplace`)

#### `GET /marketplace/tokens`

دریافت لیست توکن‌های دانش قابل معامله.

**Response (200 OK):** `array[KnowledgeToken]`

#### `POST /marketplace/buy`

خرید یک توکن دانش.

**Request Body:**

```json
{
  "token_id": "string",
  "amount": "float"
}
```

**Response (200 OK):**

```json
{
  "message": "Purchase successful",
  "transaction_id": "string"
}
```

---

### 🏛️ تمدن‌ها (`/civilizations`)

#### `POST /civilizations/create`

ایجاد یک تمدن جدید.

**Request Body:**

```json
{
  "name": "string",
  "governance_type": "string"
}
```

**Response (201 Created):** `Civilization`

#### `POST /civilizations/{civ_id}/join`

پیوستن به یک تمدن.

**Response (200 OK):**

```json
{
  "message": "Successfully joined civilization"
}
```

---

## 🔌 WebSocket API

**URL پایه:** `ws://localhost:8000/ws`

### `/ws/scda/{scda_id}`

اشتراک برای دریافت به‌روزرسانی‌های Real-time یک SCDA.

**Events (Server -> Client):**

- `scda_update`: اطلاعات SCDA به‌روز شد.
- `energy_update`: انرژی تغییر کرد.
- `complexity_update`: پیچیدگی تغییر کرد.

### `/ws/blockchain`

اشتراک برای دریافت بلوک‌های جدید.

**Events (Server -> Client):**

- `new_block`: یک بلوک جدید ماین شد.

### `/ws/metaverse`

اشتراک برای دریافت حرکات در متاورس.

**Events (Server -> Client):**

- `scda_moved`: یک SCDA حرکت کرد.

---

## 🚦 کدهای وضعیت

- `200 OK`: درخواست موفق بود.
- `201 Created`: منبع جدید با موفقیت ایجاد شد.
- `202 Accepted`: درخواست پذیرفته شد اما هنوز پردازش نشده.
- `204 No Content`: درخواست موفق بود اما محتوایی برای بازگشت وجود ندارد.
- `400 Bad Request`: درخواست نامعتبر است (e.g., JSON malformed).
- `401 Unauthorized`: احراز هویت ناموفق بود.
- `403 Forbidden`: شما اجازه دسترسی به این منبع را ندارید.
- `404 Not Found`: منبع مورد نظر یافت نشد.
- `422 Unprocessable Entity`: ورودی معتبر است اما از نظر معنایی نادرست است.
- `500 Internal Server Error`: خطای داخلی سرور.
