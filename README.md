# Emoji-Scrapr

rip every emoji, sticker, role icon, and banner off a Discord server in one go

[![license](https://img.shields.io/github/license/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=5865F2)](LICENSE)
[![last commit](https://img.shields.io/github/last-commit/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=57F287)](https://github.com/itztrmin/Emoji-Scrapr/commits/main)
[![python](https://img.shields.io/badge/python-3.10%2B-2b2d31?style=for-the-badge&labelColor=2b2d31&color=EB459E)](https://www.python.org/)
[![stars](https://img.shields.io/github/stars/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=FEE75C)](https://github.com/itztrmin/Emoji-Scrapr/stargazers)

> [!WARNING]
> User tokens break Discord's ToS. Other people's emojis aren't yours to redistribute. Also — [never share your token with anyone](#getting-a-token), ever. Read **Disclaimers** before running this on a server you don't own.

## What it does
```
icon · banner · splash · emojis (static + animated) · stickers (image + lottie) · role icons
```
One script, one token, one server ID. Pulls everything above at max resolution, sorts it into folders, writes a `manifest.json` so re-runs only grab what's new or changed.

- Full resolution downloads, no Discord CDN compression tricks
- Skips files it already has — re-running only grabs what's new
- Static and animated emojis sorted into their own folders automatically
- Works with either a bot token or a user token
- Zero setup beyond pasting in a token and a server ID

## Quick start

```bash
git clone https://github.com/itztrmin/Emoji-Scrapr.git
cd Emoji-Scrapr
pip install -r requirements.txt
cp .env.example .env
```

Paste your token into `.env`, then edit the top of `main.py`:

```python
IS_BOT = True
SERVER_ID = "your target server id"
```

```bash
python main.py
```

```
emojis: 38  (29 static, 9 animated)
stickers: 6  (4 image, 2 lottie)
role icons: 3

  47 new

done in 3.41s  →  ./cloned_My Cool Server
```

No token yet? See **Getting a token** below.

## Getting a token

**Bot — use this one**
[Developer Portal](https://discord.com/developers/applications) → New App → **Bot** tab → Reset Token → enable **Server Members Intent** → invite it to the server.

**User token — your account, your risk**
Discord in browser → `F12` → Network tab → click a channel → grab `Authorization` from the request headers.

> Either way — the bot or account behind that token has to actually be **in** the server you're targeting. It can't read a server it hasn't joined.

`SERVER_ID` comes from right-clicking the server icon in Discord (needs Developer Mode on in settings).

> [!CAUTION]
> **Do not give your token to anyone.** Not a "token checker" bot, not a giveaway site, not a friend asking nicely.
> It skips the login screen entirely — no password, no 2FA, no prompt. Whoever has it *is* you, as far as Discord's API is concerned.
> If it leaks: regenerate it from the Developer Portal (bot) or change your password (user). That's the only real fix.

## Output
```
cloned_<server>/
├─ server/      icon · banner · splash
├─ emojis/      static/ · animated/
├─ stickers/    image/ · lottie/
├─ roles/
└─ manifest.json
```
Name collisions get the asset ID appended — nothing overwrites silently.

## Roadmap
- [ ] CLI args instead of editing `main.py` by hand
- [ ] `--only emojis` / `--skip stickers` filtering
- [ ] Configurable concurrency for big servers
- [ ] Auto-zip the output folder
- [ ] Lottie → preview render instead of raw `.json`

## Disclaimers
- Self-bots / user tokens violate Discord ToS — accounts get warned, locked, or banned. Bot tokens exist for a reason.
- Not affiliated with Discord Inc. in any way.
- Only scrape servers you own or have permission to scrape — emojis and stickers belong to whoever made them.
- Never commit your `.env`. It's already gitignored — keep it that way.
- Provided as-is, no warranty. See [`LICENSE`](LICENSE).

---

This repository is in no way affiliated with, authorized, maintained, sponsored, or endorsed by Discord Inc. or any of its affiliates or subsidiaries.

★ star it if it saved you the trouble — [@itztrmin](https://github.com/itztrmin)
