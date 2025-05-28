
# 📘 TAMU Canvas Scraper

This project automates logging into [Texas A&M University's Canvas portal](https://canvas.tamu.edu/) and scrapes course assignment names and due dates using Selenium. It supports persistent login using cookies and handles Microsoft SSO with optional DUO 2FA fallback.

## 🔧 Features

- Auto-login to TAMU Canvas with Microsoft credentials
- Persistent sessions using cookies
- Manual DUO 2FA support
- Scrapes all Canvas courses
- Collects assignment titles and due dates
- Environment-variable-based credentials (no hardcoded passwords)

## 📁 Project Structure

```
Canvas-Scraper/
├── get_access.py         # Main scraping script
├── .env                  # Your login credentials (not included in repo)
├── cookies.pkl           # Saved session cookies (auto-created)
├── requirements.txt      # Python dependencies
```

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/canvas-scraper.git
cd canvas-scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a `.env` file in the project root with your TAMU credentials:

```
EMAIL=your_netid@tamu.edu
PASSWORD=your_password_here
```

> **Warning**: Use an [app password](https://support.microsoft.com/en-us/account-billing/create-app-passwords-in-microsoft-365-6e4eac7f-d61e-4ff6-9203-20c4f6b72261) or secure your `.env` file. Never commit it to version control!

### 4. Run the script

```bash
python get_access.py
```

The first time you run the script, it will log you in via Microsoft, wait for you to approve DUO manually, then save cookies to skip this step in future runs.

## 🔒 Notes on Authentication

- This script uses [Selenium](https://www.selenium.dev/) and saves login session cookies to `cookies.pkl`.
- Cookies are only valid for `https://login.microsoftonline.com/` — not Canvas directly.
- If your session expires, it will automatically prompt for login again.

## ✅ Sample Output

```
📘 Course name: MATH 308 - Differential Equations
   📝 HW 5 — Due May 30
   📝 Project Proposal — No due date
📘 Course name: CSCE 313 - Introduction to Systems Programming
   📝 Midterm 2 — Due June 3
```

## 🧠 Tips & Improvements

- Add email notifications for upcoming deadlines
- Convert scraped data to CSV or calendar format
- Integrate with Google Calendar API
- Schedule the script to run daily via cron or Task Scheduler

## 📎 Dependencies

- `selenium`
- `python-dotenv`
- `pickle` (built-in)
- Chrome + [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) (match your Chrome version)

## 🛑 Disclaimer

This script is intended for personal academic use. It is **not affiliated** with Texas A&M University or Instructure (Canvas). Use responsibly and do not overload university servers.

---

## 📜 License

[MIT License](LICENSE)
