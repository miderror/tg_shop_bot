## Telegram Shop Bot

A Telegram bot for product sales with a Django admin panel, containerized with Docker.

### Key Features

*   **Telegram Bot (Aiogram 3):** Catalog, cart, orders, FAQ, YooKassa (test), subscription checks.
*   **Django Admin Panel:** Manage users, products, orders, FAQs, send mailings.
*   **Database:** PostgreSQL.
*   **Deployment:** Docker and Docker Compose.
*   **Networking:** Bot uses webhooks, requires a public URL.

### Setup and Run

1.  **Environment Variables:**
    *   Copy `admin_panel/.env.example` to `admin_panel/.env`
    *   Copy `telegram_bot/.env.example` to `telegram_bot/.env`
    *   Fill in all `YOUR_...` placeholders. **`BASE_WEBHOOK_URL` in `telegram_bot/.env` must be your public URL (e.g., from ngrok/cloudpub).**

2.  **Build & Run:**
    Navigate to the project root (`tg_shop_bot/`) and execute:
    ```bash
    docker-compose up --build -d
    ```

3.  **Access:**
    *   **Django Admin:** `http://localhost:8000/admin/` (default superuser: `admin`/`admin`).
    *   **Telegram Bot:** Ensure your public URL is active. Send `/start` to your bot.