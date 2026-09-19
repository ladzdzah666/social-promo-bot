# Social Promo Bot (X & Threads Automation Engine)

A data-driven, cross-platform publishing and engagement automation tool for **X (formerly Twitter)** and **Threads**, built with **Python** and **Playwright**. Designed for creators and businesses to schedule promotional content via local spreadsheets without costly enterprise API subscriptions.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Automated_Browser-green?logo=playwright&logoColor=white)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Modular_Data--Driven-orange)](#system-architecture)

---

## Overview

High-tier social media platforms increasingly restrict or paywall their public posting APIs. **Social Promo Bot** bypasses this constraint through localized browser automation with persistent user context:
- **Zero API Fees**: Interacts directly with official web interfaces via headless/headed Chromium contexts.
- **Isolated Local Sessions**: Stores authentication cookies and tokens locally on your machine—no passwords stored in plaintext or database.
- **Spreadsheet-Driven Queue**: Manage campaigns, caption copy, scheduled dates, and image attachments directly in standard Excel files (`promo_data.xlsx`).
- **Human Behavioral Simulation**: Applies randomized keystroke intervals and action delays to comply with natural user pacing and platform rate limits.

---

## System Architecture

```text
 ┌─────────────────┐       ┌─────────────────┐       ┌──────────────────────┐
 │ promo_data.xlsx │ ────▶ │  DataManager    │ ────▶ │   Main Scheduler     │
 └─────────────────┘       └─────────────────┘       └──────────┬───────────┘
                                                                │
                                         ┌──────────────────────┴──────────────────────┐
                                         ▼                                             ▼
                              ┌────────────────────┐                        ┌────────────────────┐
                              │  XPoster (X.com)   │                        │ ThreadsPoster      │
                              │ (Persistent Auth)  │                        │ (Persistent Auth)  │
                              └────────────────────┘                        └────────────────────┘
```

The codebase is structured around a decoupled, modular design:
- **`DataManager`**: Handles spreadsheet extraction, format normalization, and status tracking (`pending` &rarr; `posted` / `failed`).
- **`BasePoster`**: Manages Chromium browser lifecycle, randomized pacing, and human typing simulation.
- **`XPoster` & `ThreadsPoster`**: Platform-specific DOM navigators and media upload handlers.
- **`EngagementBot`**: Autonomous keyword monitoring and context-sensitive response dispatcher.

---

## Key Features

- **Multi-Platform Dispatch**: Simultaneously publish to X, Threads, or single platforms on demand.
- **Persistent Authentication**: One-time interactive login creates a persistent session profile (`browser_profiles/`), avoiding automated credential logins that trigger captchas.
- **Dynamic Scheduling**: Supports both immediate execution and future timestamp queues (`YYYY-MM-DD HH:MM`).
- **Media Upload Pipeline**: Automates image attachment handling alongside multiline text and hashtags.
- **Real-Time Spreadsheet Sync**: Automatically stamps publication timestamps (`POSTED_AT`) and captures error diagnostics (`NOTES`) back into the Excel sheet.
- **Keyword Auto-Engagement**: Monitors live search streams for designated keywords/hashtags and responds with randomized reply templates.

---

## Repository Structure

```text
social-promo-bot/
├── .agents/                 # Engineering skills and anti-slop filters
├── posters/
│   ├── base_poster.py       # Browser lifecycle and human typing simulation
│   ├── x_poster.py          # X/Twitter DOM interaction layer
│   ├── threads_poster.py    # Threads.net DOM interaction layer
│   └── engagement_bot.py    # Live keyword search & auto-reply engine
├── sample_images/           # Sample image assets for demonstrations
├── config.py                # Global timeouts, delay ranges, and path definitions
├── data_manager.py          # Excel spreadsheet data access layer
├── main.py                  # CLI dashboard, argument parser, & scheduler runner
├── setup_accounts.py        # One-time interactive session initializer
├── promo_data.xlsx          # Content publication queue
├── reply_templates.txt      # Randomized comment response templates
├── requirements.txt         # Project dependencies
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/ladzdzah666/social-promo-bot.git
cd social-promo-bot

# Initialize virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# or: .venv\Scripts\activate   # Windows

# Install required Python packages
pip install -r requirements.txt

# Install Playwright Chromium binaries
playwright install chromium
```

### 2. Initial Account Setup (One-time only)
Initialize your authenticated browser profile:
```bash
python setup_accounts.py
```
1. Select the platform you wish to initialize (`1` for X, `2` for Threads, or `3` for both).
2. A browser window will open to the login portal. Log in manually and complete any 2FA/OTP prompts.
3. Once the main feed has loaded, return to the terminal and press `ENTER`.
4. Your authenticated session is now securely stored in your local `browser_profiles/` folder.

---

## Usage

### Interactive CLI Menu
Launch the interactive command console:
```bash
python main.py
```
From here you can view queues, verify active sessions, dispatch campaigns, or initiate keyword engagement.

### CLI Automation Flags
Run headless or background automation using command-line arguments:

- **Inspect Pending Queue:**
  ```bash
  python main.py --test-excel
  ```
- **Verify Session Health:**
  ```bash
  python main.py --check-login
  ```
- **Process Due Items Immediately:**
  ```bash
  python main.py --run-now
  ```
- **Run Continuous Background Monitor (e.g. check every 30 minutes):**
  ```bash
  python main.py --schedule 30
  ```

---

## Queue Spreadsheet Specification

Campaigns are managed via `promo_data.xlsx`. Standard column headers:

| Column | Type | Description |
|:---|:---|:---|
| `ID` | Integer | Unique identifier for the entry (e.g. `1`, `2`, `3`) |
| `PLATFORM` | String | Target destination: `both`, `x`, or `threads` |
| `SCHEDULE` | Datetime | Optional timestamp (`YYYY-MM-DD HH:MM`). Leave blank for immediate dispatch. |
| `CAPTION` | Text | The post content, promotional copy, links, and hashtags |
| `IMAGE` | Path | Relative or absolute path to an image (`sample_images/product.jpg`). Leave blank for text-only. |
| `STATUS` | String | Set to `pending` to queue. Auto-updated to `posted` or `failed`. |
| `POSTED_AT` | Datetime | Automatically populated upon successful publication |
| `NOTES` | Text | Error traces or delivery status notes |

---

## Security & Best Practices

- **Strict Session Isolation**: Active session data in `browser_profiles/` is explicitly ignored via `.gitignore` to prevent leaking session tokens or cookies to public repositories.
- **No Stored Plaintext Secrets**: The application operates without requiring passwords or access tokens in source code or `.env` files.
- **Platform Rate Limit Adherence**: Includes configurable safety delays between actions (`config.py`) to reduce automated activity flagging.
- **Standardized Engineering**: Built using production software engineering standards documented in `AGENTS.md`.

---

## Ethical Use Disclaimer

This software is developed strictly for educational research, browser automation demonstration, and personal content management. Users are exclusively responsible for complying with the Terms of Service (ToS) of each respective platform (X Corp and Meta Platforms, Inc.). Automated spamming, aggressive bulk messaging, or deceptive activities are strictly discouraged.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
