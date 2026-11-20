# ⏰ External Scheduler Setup & Production Hardening Guide (Free & Verified)

> **Goal**: Eliminate GitHub Actions' cron dropping/delay weakness and ensure 100% reliable daily triggers with a Telegram heartbeat, zero token expiry, and full YouTube 2025/2026 AI disclosure compliance.

---

## Method 1: Cloudflare Worker Cron Trigger (Recommended — 100% Free)

Cloudflare Workers provide **100,000 free requests per day** and execute cron schedules with zero jitter or drops.

### Step 1: Create a GitHub Fine-Grained Personal Access Token (PAT)
1. Go to GitHub: **Settings** $\rightarrow$ **Developer Settings** $\rightarrow$ **Personal Access Tokens** $\rightarrow$ **Fine-grained tokens**.
2. Click **Generate new token**:
   - **Name**: `Cloudflare-Worker-Story-Trigger`
   - **Repository access**: *Only select repositories* $\rightarrow$ `Chiru9030/Automation`.
   - **Permissions**: *Actions* $\rightarrow$ **Read and write**.
3. Click **Generate token** and copy the `github_pat_...` string.

### Step 2: Deploy Cloudflare Worker
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) and go to **Workers & Pages**.
2. Click **Create Application** $\rightarrow$ **Create Worker** $\rightarrow$ Name it `story-pipeline-trigger` $\rightarrow$ Click **Deploy**.
3. Click **Edit code** and paste the contents of [`scripts/cloudflare_cron_trigger.js`](./cloudflare_cron_trigger.js).
4. Go to **Settings** $\rightarrow$ **Variables & Secrets**:
   - Add Secret `GITHUB_PAT`: `<your_github_pat_token>`
   - Add Variable `GITHUB_REPO`: `Chiru9030/Automation`
   - Add Variable `TELEGRAM_BOT_TOKEN`: `<your_bot_token>` (optional)
   - Add Variable `TELEGRAM_CHAT_ID`: `<your_chat_id>` (optional)
5. Go to **Settings** $\rightarrow$ **Triggers**:
   - Under **Cron Triggers**, click **Add Cron Trigger**.
   - Set to: `0 14 * * *` (Daily at 14:00 UTC / 9:00 AM EST / 7:30 PM IST).
6. Click **Save**. Done!

---

## Method 2: cron-job.org (Alternative — 100% GUI, Zero Code)

If you prefer a pure visual dashboard without deploying a Worker:

1. Create a free account at [cron-job.org](https://cron-job.org).
2. Click **Create Cronjob**:
   - **Title**: `Daily Story Video Trigger`
   - **URL**: `https://api.github.com/repos/Chiru9030/Automation/actions/workflows/story_pipeline.yml/dispatches`
   - **Request Method**: `POST`
   - **Schedule**: User-defined $\rightarrow$ `Daily at 14:00 UTC`
3. Under **Headers**, add:
   - `Authorization`: `Bearer github_pat_...`
   - `Accept`: `application/vnd.github.v3+json`
   - `User-Agent`: `Cron-Job-Story-Dispatcher`
4. Under **Request Body**, select `Raw` and paste:
   ```json
   {
     "ref": "main",
     "inputs": {
       "sample_mode": false,
       "privacy_status": "private"
     }
   }
   ```
5. Click **Create**. Done!

---

## 🛡️ Critical Production Hardening Steps

### 1. YouTube OAuth Token Expiry (Testing vs In Production)
* **The Trap**: If your Google Cloud OAuth Consent Screen is left in **"Testing"** mode, refresh tokens expire automatically every **7 days**.
* **The Permanent Fix**:
  1. Open [Google Cloud Console](https://console.cloud.google.com/) $\rightarrow$ **APIs & Services** $\rightarrow$ **OAuth consent screen**.
  2. Under **Publishing status**, click **PUBLISH APP** to move it to **In production**.
  3. *Note*: For a personal automation script uploading to your own channel, Google does NOT require verification! You simply bypass the "unverified app" screen once during token generation.
  4. Now, your `refresh_token` will remain valid indefinitely.

### 2. YouTube AI Synthetic Media Compliance (2025/2026 Policy)
* YouTube strictly enforces synthetic media disclosure.
* Our pipeline sets `status.containsSyntheticMedia = True` and `selfDeclaredMadeForKids = False` in `main.py`, ensuring 100% compliance with platform regulations.

### 3. Review Window (Private $\rightarrow$ Public)
* All videos are initially uploaded as **`private`** (or `unlisted`).
* Review the generated short in your YouTube Studio mobile app. If satisfied, click publish or set a scheduled release!
