<div align="center">
  <h2 align="center">CharacterAI Account Creator</h2>
  <p align="center">
    A tool designed to automate the creation of accounts for Character.AI, featuring email verification, proxy support, and efficient batch processing.

   I bypassed their shitty ahh captcha system, they don't even flag emails or headers. I made it quickly and it is 4 am so please forgive this shitty code
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="https://github.com/sexfrance/CharacterAI-Account-Creator#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/CharacterAI-Account-Creator/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/CharacterAI-Account-Creator/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Creates Character.AI accounts with email verification.
- Supports proxy integration to maintain anonymity.
- Automatically fetches and verifies email links using temporary mail services.
- Multi-threaded for efficient account generation.
- Saves account details in a structured output file.
- Recaptcha bypassing!!

---

### 📝 Usage

1. **Preparation**:
   - Place your proxy list in `input/proxies.txt` (optional for proxy-based usage).
   - Configure settings in `input/config.toml`.

2. **Running the script**:
   ```bash
   python main.py
   ```

3. **Output**:
   - All created accounts are saved in `output/accounts.txt`.

---

### 📹 Preview

![Preview](https://i.imgur.com/AgOxIQI.gif)

---

### ❗ Disclaimers

- This project is for educational purposes **only**. It is intended to study the Character.AI API and should not be used to abuse their services.
- The author is not responsible for any misuse of this tool, including account suspensions or bans.
- Use proxies responsibly to avoid violating any terms of service.

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 12/26/2024
! Initial release with Character.AI account generation functionality.
```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/CharacterAI-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/CharacterAI-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/CharacterAI-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>

