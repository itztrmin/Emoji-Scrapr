import asyncio
import json
import os
import struct
import time
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# Config: Edit these three values.

# True = bot token  (normal bot accounts)
# False = user token (use at your own risk)
IS_BOT = True

# Your target server/guild ID.
SERVER_ID = "1370351288079876147"

# To hardcode instead: TOKEN = "your_token_here"
TOKEN = os.getenv("DISCORD_TOKEN")

RETRY_LIMIT = 3
STICKER_FMT = {1: "png", 2: "png", 3: "json", 4: "gif"}

if not TOKEN:
    raise ValueError("DISCORD_TOKEN is not set")
if not str(SERVER_ID).strip():
    raise ValueError("SERVER_ID is empty. Set it in the Config section at the top of main.py.")

SERVER_ID = str(SERVER_ID).strip()


def auth_headers() -> dict:
    prefix = "Bot " if IS_BOT else ""
    return {
        "Authorization": f"{prefix}{TOKEN}",
        "User-Agent": "DiscordBot (https://github.com/discord/discord-api-docs, 10)",
    }


def folder_safe(name: str) -> str:
    illegal = r'\/:*?"<>|' + "\x00"
    cleaned = "".join(c for c in name if c not in illegal).strip()
    return cleaned or SERVER_ID


def ensure_dirs(root: str):
    for sub in [
        "server",
        os.path.join("emojis", "static"),
        os.path.join("emojis", "animated"),
        os.path.join("stickers", "image"),
        os.path.join("stickers", "lottie"),
        "roles",
    ]:
        os.makedirs(os.path.join(root, sub), exist_ok=True)


def png_dims(path: str):
    try:
        with open(path, "rb") as f:
            f.read(16)
            w = struct.unpack(">I", f.read(4))[0]
            h = struct.unpack(">I", f.read(4))[0]
        return w, h
    except Exception:
        return None, None


def file_info(path: str) -> str:
    if not os.path.exists(path):
        return "missing"
    kb = os.path.getsize(path) // 1024
    if path.endswith((".png", ".gif")):
        w, h = png_dims(path)
        if w:
            return f"{w}x{h}  {kb}KB"
    return f"{kb}KB"


async def handle_rate_limit(resp) -> bool:
    if resp.status == 429:
        try:
            body = await resp.json()
            wait = float(body.get("retry_after", 5))
        except Exception:
            wait = float(resp.headers.get("Retry-After", 5))
        print(f"  rate limited — waiting {wait}s")
        await asyncio.sleep(wait)
        return True
    return False


async def api_get(session: aiohttp.ClientSession, url: str):
    while True:
        async with session.get(url, headers=auth_headers()) as resp:
            if await handle_rate_limit(resp):
                continue
            if resp.status != 200:
                try:
                    body = await resp.json()
                except Exception:
                    body = await resp.text()
                print(f"  HTTP {resp.status}: {url}")
                print(f"  {body}")
                return None
            return await resp.json()


async def download_file(session: aiohttp.ClientSession, url: str, path: str) -> tuple[bool, bool]:
    existed = os.path.exists(path)
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            async with session.get(url) as resp:
                if await handle_rate_limit(resp):
                    continue
                if resp.status == 200:
                    data = await resp.read()
                    with open(path, "wb") as f:
                        f.write(data)
                    return True, not existed
                if attempt < RETRY_LIMIT:
                    await asyncio.sleep(1)
                else:
                    print(f"  failed ({resp.status}) after {RETRY_LIMIT} attempts: {os.path.basename(path)}")
                    return False, False
        except aiohttp.ClientError as e:
            if attempt < RETRY_LIMIT:
                await asyncio.sleep(1)
            else:
                print(f"  error after {RETRY_LIMIT} attempts: {os.path.basename(path)}  ({e})")
                return False, False
    return False, False


def build_manifest(server_data, emojis, stickers, roles) -> dict:
    return {
        "server": {
            "id":          server_data.get("id"),
            "name":        server_data.get("name"),
            "description": server_data.get("description"),
            "members":     server_data.get("approximate_member_count"),
            "has_icon":    bool(server_data.get("icon")),
            "has_banner":  bool(server_data.get("banner")),
            "has_splash":  bool(server_data.get("splash")),
        },
        "emojis": {
            "count":    len(emojis),
            "static":   [{"id": e["id"], "name": e["name"]} for e in emojis if not e.get("animated")],
            "animated": [{"id": e["id"], "name": e["name"]} for e in emojis if e.get("animated")],
        },
        "stickers": {
            "count": len(stickers),
            "items": [
                {
                    "id":     s["id"],
                    "name":   s["name"],
                    "desc":   s.get("description", ""),
                    "format": STICKER_FMT.get(s.get("format_type", 1), "png"),
                }
                for s in stickers
            ],
        },
        "roles": {
            "count":      len(roles),
            "with_icons": [{"id": r["id"], "name": r["name"]} for r in roles if r.get("icon")],
        },
        "cloned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


async def main():
    start = time.time()

    async with aiohttp.ClientSession() as session:
        server = await api_get(
            session,
            f"https://discord.com/api/v10/guilds/{SERVER_ID}?with_counts=true",
        )
        if not server:
            print("couldn't connect — check DISCORD_TOKEN, SERVER_ID, and IS_BOT.")
            return

        server_name  = server.get("name", "unknown")
        root         = f"./cloned_{folder_safe(server_name)}"
        is_first_run = not os.path.exists(root)
        ensure_dirs(root)

        members   = server.get("approximate_member_count", "?")
        run_label = "first run" if is_first_run else "updating"
        print(f"{server_name}  ({members} members)  [{run_label}]")
        print(f"{root}\n")

        queue = []

        icon_hash = server.get("icon")
        if icon_hash:
            ext  = "gif" if icon_hash.startswith("a_") else "png"
            url  = f"https://cdn.discordapp.com/icons/{SERVER_ID}/{icon_hash}.{ext}?size=4096"
            path = os.path.join(root, "server", f"icon.{ext}")
            queue.append((path, download_file(session, url, path)))

        banner_hash = server.get("banner")
        if banner_hash:
            ext  = "gif" if banner_hash.startswith("a_") else "png"
            url  = f"https://cdn.discordapp.com/banners/{SERVER_ID}/{banner_hash}.{ext}?size=4096"
            path = os.path.join(root, "server", f"banner.{ext}")
            queue.append((path, download_file(session, url, path)))

        splash_hash = server.get("splash")
        if splash_hash:
            url  = f"https://cdn.discordapp.com/splashes/{SERVER_ID}/{splash_hash}.png?size=4096"
            path = os.path.join(root, "server", "splash.png")
            queue.append((path, download_file(session, url, path)))

        emojis   = await api_get(session, f"https://discord.com/api/v10/guilds/{SERVER_ID}/emojis") or []
        n_static = sum(1 for e in emojis if not e.get("animated"))
        n_anim   = sum(1 for e in emojis if e.get("animated"))
        if emojis:
            print(f"emojis: {len(emojis)}  ({n_static} static, {n_anim} animated)")
            print("  note: emoji quality is capped by Discord at the original upload size")
        else:
            print("no custom emojis")

        seen: set[str] = set()
        for emoji in emojis:
            animated  = emoji.get("animated", False)
            ext       = "gif" if animated else "png"
            subfolder = "animated" if animated else "static"
            e_id      = emoji["id"]
            e_name    = emoji.get("name") or e_id
            filename  = f"{e_name}.{ext}"
            if filename in seen:
                filename = f"{e_name}_{e_id}.{ext}"
            seen.add(filename)
            url  = f"https://cdn.discordapp.com/emojis/{e_id}.{ext}?size=4096"
            path = os.path.join(root, "emojis", subfolder, filename)
            queue.append((path, download_file(session, url, path)))

        stickers = await api_get(session, f"https://discord.com/api/v10/guilds/{SERVER_ID}/stickers") or []
        n_img    = sum(1 for s in stickers if s.get("format_type") != 3)
        n_lottie = sum(1 for s in stickers if s.get("format_type") == 3)
        if stickers:
            print(f"\nstickers: {len(stickers)}  ({n_img} image, {n_lottie} lottie)")
        else:
            print("no stickers")

        seen = set()
        for sticker in stickers:
            fmt       = sticker.get("format_type", 1)
            ext       = STICKER_FMT.get(fmt, "png")
            subfolder = "lottie" if fmt == 3 else "image"
            s_id      = sticker["id"]
            s_name    = sticker.get("name") or s_id
            filename  = f"{s_name}.{ext}"
            if filename in seen:
                filename = f"{s_name}_{s_id}.{ext}"
            seen.add(filename)
            url  = f"https://cdn.discordapp.com/stickers/{s_id}.{ext}?size=4096"
            path = os.path.join(root, "stickers", subfolder, filename)
            queue.append((path, download_file(session, url, path)))

        roles      = server.get("roles", [])
        role_icons = [r for r in roles if r.get("icon")]
        if role_icons:
            print(f"\nrole icons: {len(role_icons)}")
        seen = set()
        for role in role_icons:
            r_id     = role["id"]
            r_name   = role.get("name") or r_id
            r_hash   = role["icon"]
            ext      = "gif" if r_hash.startswith("a_") else "png"
            url      = f"https://cdn.discordapp.com/role-icons/{r_id}/{r_hash}.{ext}?size=4096"
            filename = f"{r_name}.{ext}"
            if filename in seen:
                filename = f"{r_name}_{r_id}.{ext}"
            seen.add(filename)
            path = os.path.join(root, "roles", filename)
            queue.append((path, download_file(session, url, path)))

        if not queue:
            print("\nnothing to download.")
            return

        print(f"\ndownloading {len(queue)} files...")
        paths, coros = zip(*queue)
        results = await asyncio.gather(*coros)

        ok = fails = new_count = replaced = 0
        for path, (success, is_new) in zip(paths, results):
            name = os.path.basename(path)
            if success:
                ok += 1
                info = file_info(path)
                tag  = "new" if is_new else "replaced"
                print(f"  [{tag}] {name:<30}  {info}")
                if is_new:
                    new_count += 1
                else:
                    replaced += 1
            else:
                fails += 1
                print(f"  [fail] {name}")

        parts = []
        if new_count: parts.append(f"{new_count} new")
        if replaced:  parts.append(f"{replaced} replaced")
        if fails:     parts.append(f"{fails} failed")
        print("\n  " + ("  |  ".join(parts) if parts else "nothing to do"))

        manifest = build_manifest(server, emojis, stickers, roles)
        with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    elapsed = round(time.time() - start, 2)
    print(f"\ndone in {elapsed}s  →  {root}")


if __name__ == "__main__":
    asyncio.run(main())
