# 🎯 Gen Con Event Ticket Sniper

This script automates the process of checking for available tickets to a specified GenCon event and purchasing them the moment they become available.

It is designed for serious attendees who want to maximize their event schedule by securing limited-availability tickets automatically. Built using [Playwright](https://playwright.dev/python/), it emulates a real user session and interacts with GenCon.com's website directly.

---

## 📌 Features

- Logs into Gen Con with your account credentials
- Monitors an event's ticket availability
- Automatically selects "Myself" and adds the ticket to your cart
- Completes the checkout (unless in debug mode)
- Screenshots for debugging
- Cleans the cart in debug mode to enable re-testing
- Custom Chrome user-agent to avoid bot detection
- CLI options for debug mode and event selection

---

## 🚀 How It Works

1. Logs into [GenCon.com](https://www.gencon.com)
2. Monitors the event page for ticket availability
3. When tickets are available:
   - Selects the checkbox for yourself
   - Clicks **Add to Cart**
   - Clicks **View My Cart**
   - Proceeds to **Billing**
   - Agrees to Terms of Service
   - Optionally completes checkout (if not in debug mode)
4. (In debug mode) Cleans up the cart for re-testing

---

## 🧰 Requirements

- Python 3.8+
- [Playwright](https://playwright.dev/python/)
- `python-dotenv` (optional, for local `.env` usage)

### Install dependencies:

```bash
pip install playwright python-dotenv
playwright install
```

---

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone git@github.com:naveedi/gc_event_sniper.git
cd gc_event_sniper
```

### 2. Set Environment Variables

You must provide your GenCon login credentials.

#### 🔐 Option A: Windows Environment Variables (Persistent)

Run these commands in PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable("GENCON_EMAIL", "your_email_here", "User")
[System.Environment]::SetEnvironmentVariable("GENCON_PASSWORD", "your_password_here", "User")
```

You only need to do this **once**. You can then use the script without typing your credentials again.

#### 🔐 Option B: `.env` file (Optional)

Create a file called `.env` in the same directory as the script with the following contents:

```
GENCON_EMAIL=your_email_here
GENCON_PASSWORD=your_password_here
```

And make sure `python-dotenv` is installed. The script can be updated to load this automatically if needed.

---

## 🖥️ Usage

```bash
python gc_sniper.py [--debug] [--event EVENT_ID]
```

### Options:

- `--debug`  
  Opens a visible browser, skips final checkout, and cleans the cart after. Also captures screenshots. NOTE: All events in cart are dumped so be careful you purchase what you wanted first.
  
- `--event`  
  Specify the Gen Con Event ID (e.g. `275663`). Defaults to `296631`.

### Example:

```bash
python gc_sniper.py --debug --event 275663
```

---

## 🧪 Debug Mode Behavior

If you use `--debug`, the script will:

- Launch a visible Chrome window
- Use slower interactions (via `slow_mo`) so you can observe steps
- Skip final checkout
- Clean up tickets in the cart
- Take a screenshot at critical points

---

## 🔐 Anti-Bot Measures

To prevent detection:

- Sets the user agent to a modern Chrome browser:

  ```
  Mozilla/5.0 (Windows NT 10.0; Win64; x64)
  AppleWebKit/537.36 (KHTML, like Gecko)
  Chrome/136.0.0.0 Safari/537.36
  ```

- Uses real browser interactions via Playwright

---

## 🧱 Contributing

### Suggested Enhancements:

- Add email or Discord webhook notification when a purchase is made
- Add support for selecting multiple people including "another for me"
- Add a GUI frontend
- Store event history in a SQLite database
- Support multiple simultaneous events
- Remove default event and always require event id at cmdline

### Structure Ideas:

- `sniper.py` — core logic
- `config.py` — shared constants and ENV loading
- `event.py` — event-specific logic
- `cart.py` — shopping cart functions

---

## 📝 License

MIT — Use this script responsibly. Abuse of automated ticketing can lead to bans from Gen Con or other platforms.

---

## 💬 Questions?

Open an issue on [GitHub](https://github.com/naveedi/gc_event_sniper/issues) or reach out via pull request.

Happy hunting!
