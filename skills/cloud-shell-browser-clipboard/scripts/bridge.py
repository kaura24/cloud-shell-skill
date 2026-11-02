#!/usr/bin/env python3
"""Loopback noVNC proxy with explicit-origin UTF-8 X11 clipboard paste."""
import argparse
import asyncio
import os
import urllib.parse

from aiohttp import ClientSession, ClientTimeout, WSMsgType, web

CLIENT_KEY = web.AppKey("client", ClientSession)
MAX_TEXT_BYTES = 256 * 1024
HOP_HEADERS = {"connection", "transfer-encoding", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "upgrade", "content-length", "content-encoding"}


def validate_origin(origin, allow_local=False):
    parsed = urllib.parse.urlsplit(origin)
    try:
        port = parsed.port
    except ValueError:
        return False
    if parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        return False
    host = parsed.hostname or ""
    if parsed.scheme == "https" and host.endswith(".cloudshell.dev") and host != "cloudshell.dev" and port in (None, 443):
        return origin == f"https://{host}"  # exact canonical origin
    return (allow_local and parsed.scheme == "http" and host in {"127.0.0.1", "localhost"}
            and port is not None and origin == f"http://{host}:{port}")


async def paste_x11(text, display):
    env = os.environ.copy()
    env["DISPLAY"] = display
    proc = await asyncio.create_subprocess_exec(
        "xclip", "-selection", "clipboard", "-i", "-target", "UTF8_STRING",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL, env=env,
    )
    try:
        await asyncio.wait_for(proc.communicate(text.encode("utf-8")), 5)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError("clipboard command timed out")
    if proc.returncode:
        raise RuntimeError("clipboard command failed")
    proc = await asyncio.create_subprocess_exec(
        "xdotool", "key", "--clearmodifiers", "ctrl+v",
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL, env=env,
    )
    try:
        await asyncio.wait_for(proc.wait(), 5)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError("paste command timed out")
    if proc.returncode:
        raise RuntimeError("paste command failed")


def create_app(origin, upstream, display, paste=paste_x11, allow_local=False):
    if not validate_origin(origin, allow_local):
        raise ValueError("Expected a canonical HTTPS Cloud Shell preview origin")
    app = web.Application(client_max_size=MAX_TEXT_BYTES)

    async def start(app):
        app[CLIENT_KEY] = ClientSession(timeout=ClientTimeout(total=None, connect=10))

    async def stop(app):
        await app[CLIENT_KEY].close()

    app.on_startup.append(start)
    app.on_cleanup.append(stop)

    async def clipboard(request):
        if request.headers.get("Origin") != origin:
            raise web.HTTPForbidden(text="Untrusted origin")
        if request.content_type != "text/plain":
            raise web.HTTPUnsupportedMediaType()
        data = await request.read()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise web.HTTPBadRequest(text="Invalid UTF-8")
        if not text or "\x00" in text:
            raise web.HTTPBadRequest(text="Empty or invalid text")
        try:
            await paste(text, display)
        except Exception:
            raise web.HTTPInternalServerError(text="Clipboard transfer failed")
        return web.Response(text="전송했습니다. 원격 입력란을 확인하세요.", headers={"Cache-Control": "no-store"})

    async def js(request):
        return web.FileResponse(os.path.join(os.path.dirname(__file__), "clipboard.js"), headers={"Cache-Control": "no-store"})

    async def proxy(request):
        url = upstream.rstrip("/") + request.rel_url.path_qs
        if request.headers.get("Upgrade", "").lower() == "websocket":
            if request.headers.get("Origin") != origin:
                raise web.HTTPForbidden(text="Untrusted origin")
            client = app[CLIENT_KEY]
            async with client.ws_connect(url.replace("http://", "ws://", 1), protocols=("binary",), autoping=True) as remote:
                local = web.WebSocketResponse(protocols=("binary",), autoping=True)
                await local.prepare(request)
                async def forward(src, dst):
                    async for msg in src:
                        if msg.type == WSMsgType.TEXT:
                            await dst.send_str(msg.data)
                        elif msg.type == WSMsgType.BINARY:
                            await dst.send_bytes(msg.data)
                        elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE, WSMsgType.CLOSED):
                            break
                    await dst.close()
                await asyncio.gather(forward(local, remote), forward(remote, local))
                return local
        if request.method not in ("GET", "HEAD"):
            raise web.HTTPMethodNotAllowed(request.method, ["GET", "HEAD"])
        headers = {"Accept-Encoding": "identity"}
        async with app[CLIENT_KEY].request(request.method, url, headers=headers, allow_redirects=False) as resp:
            body = await resp.read()
            if request.path == "/vnc.html" and request.method == "GET" and resp.status == 200:
                marker = b"</body>"
                if marker not in body or b'noVNC_clipboard_text' not in body:
                    raise web.HTTPBadGateway(text="Unsupported noVNC page")
                body = body.replace(marker, b'<script src="/clipboard-bridge.js"></script></body>', 1)
            response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in HOP_HEADERS}
            response_headers["Cache-Control"] = "no-store"
            return web.Response(body=body, status=resp.status, headers=response_headers)

    app.router.add_post("/clipboard-paste", clipboard)
    app.router.add_get("/clipboard-bridge.js", js)
    app.router.add_route("*", "/{tail:.*}", proxy)
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True, help="Current HTTPS Cloud Shell preview origin")
    parser.add_argument("--display", default=os.environ.get("DISPLAY", ":99"))
    parser.add_argument("--upstream-port", type=int, default=6080)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--allow-local-test", action="store_true", help="Allow localhost origin for local tests only")
    args = parser.parse_args()
    app = create_app(args.origin, f"http://127.0.0.1:{args.upstream_port}", args.display, allow_local=args.allow_local_test)
    web.run_app(app, host="127.0.0.1", port=args.port, access_log=None)


if __name__ == "__main__":
    main()
