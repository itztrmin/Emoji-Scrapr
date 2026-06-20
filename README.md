<div align="center">
<img src="assets/icons/rocket.svg" width="38" alt="" />

<h1>Emoji-Scrapr</h1>

<sub>rip every emoji, sticker, role icon, and banner off a Discord server in one go</sub>

<br><br>

<a href="LICENSE"><img alt="license" src="https://img.shields.io/github/license/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=5865F2"></a>
<a href="https://github.com/itztrmin/Emoji-Scrapr/commits/main"><img alt="last commit" src="https://img.shields.io/github/last-commit/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=57F287"></a>
<a href="https://www.python.org/"><img alt="python" src="https://img.shields.io/badge/python-3.10%2B-2b2d31?style=for-the-badge&labelColor=2b2d31&color=EB459E"></a>
<a href="https://github.com/itztrmin/Emoji-Scrapr/stargazers"><img alt="stars" src="https://img.shields.io/github/stars/itztrmin/Emoji-Scrapr?style=for-the-badge&labelColor=2b2d31&color=FEE75C"></a>

</div>

<br>

> [!WARNING]
> User tokens break Discord's ToS. Other people's emojis aren't yours to redistribute. Read **Disclaimers** before you run this on a server you don't own.

## What it does

```
icon · banner · splash · emojis (static + animated) · stickers (image + lottie) · role icons
```

One script, one token, one server ID. It pulls everything above at max resolution, sorts it into folders, and writes a `manifest.json` so re-runs only grab what's new or changed.

## Get a token

**Bot (use this one)**
[Developer Portal](https://discord.com/developers/applications) → New App → **Bot** tab → Reset Token → enable **Server Members Intent** → invite it to the server.

**User (your account, your risk)**
Discord in browser → `F12` → Network tab → click a channel → grab `Authorization` from the request headers.

## Run it

```bash
git clone https://github.com/itztrmin/Emoji-Scrapr.git
cd Emoji-Scrapr && pip install -r requirements.txt
cp .env.example .env   # paste your token in here
```

Edit the top of `main.py`:

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

## Output

```
cloned_<server>/
├─ server/      icon · banner · splash
├─ emojis/      static/ · animated/
├─ stickers/    image/ · lottie/
├─ roles/
└─ manifest.json
```

Name collisions get the asset ID appended — nothing ever overwrites silently.

## Roadmap

- [ ] CLI args instead of editing `main.py` by hand
- [ ] `--only emojis` / `--skip stickers` style filtering
- [ ] Configurable concurrency for big servers
- [ ] Auto-zip the output folder
- [ ] Lottie → preview render instead of raw `.json`

## Disclaimers

- Self-bots / user tokens violate Discord ToS — accounts get warned, locked, or banned. Bot tokens exist for a reason.
- Not affiliated with Discord Inc. in any way.
- Only scrape servers you own or have permission to scrape — emojis and stickers belong to whoever made them.
- Never commit your `.env`. It's already gitignored — keep it that way.
- Provided as-is, no warranty. See [`LICENSE`](LICENSE).

#### This repository is in no way affiliated with, authorized, maintained, sponsored, or endorsed by Discord Inc. (discord.com) or any of its affiliates or subsidiaries.

<br>

<div align="center">
<sub>★ star it if it saved you the trouble — <a href="https://github.com/itztrmin">@itztrmin</a></sub>
</div>
