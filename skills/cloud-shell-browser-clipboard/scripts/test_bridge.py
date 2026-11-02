import unittest
from unittest.mock import AsyncMock

from aiohttp import WSServerHandshakeError, web
from aiohttp.test_utils import TestClient, TestServer

from bridge import create_app, validate_origin


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        upstream = web.Application()

        async def page(request):
            return web.Response(text='<textarea id="noVNC_clipboard_text"></textarea></body>', content_type="text/html")

        async def socket(request):
            ws = web.WebSocketResponse(protocols=("binary",))
            await ws.prepare(request)
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await ws.send_str(msg.data)
            return ws

        upstream.router.add_get('/vnc.html', page)
        upstream.router.add_get('/websockify', socket)
        self.server = TestServer(upstream)
        await self.server.start_server()
        self.origin = 'https://8080-cs-123.cs-example.cloudshell.dev'
        self.paste = AsyncMock()
        app = create_app(self.origin, str(self.server.make_url('')).rstrip('/'), ':99', paste=self.paste)
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        await self.server.close()

    async def test_injected_native_clipboard_button(self):
        response = await self.client.get('/vnc.html')
        html = await response.text()
        self.assertEqual(response.status, 200)
        self.assertIn('noVNC_clipboard_text', html)
        self.assertIn('/clipboard-bridge.js', html)

    async def test_unicode_and_origin_enforcement(self):
        headers = {'Origin': self.origin, 'Content-Type': 'text/plain; charset=utf-8'}
        resp = await self.client.post('/clipboard-paste', headers=headers, data='한글 English')
        self.assertEqual(resp.status, 200)
        self.paste.assert_awaited_once_with('한글 English', ':99')
        for origin in ('https://evil.example', '', 'https://evil.cloudshell.dev'):
            headers['Origin'] = origin
            resp = await self.client.post('/clipboard-paste', headers=headers, data='denied')
            self.assertEqual(resp.status, 403)
        self.assertEqual(self.paste.await_count, 1)

    async def test_websocket_origin_and_relay(self):
        with self.assertRaises(WSServerHandshakeError) as rejected:
            await self.client.ws_connect('/websockify', headers={'Origin': 'https://evil.example'})
        self.assertEqual(rejected.exception.status, 403)
        ws = await self.client.ws_connect('/websockify', headers={'Origin': self.origin}, protocols=('binary',))
        await ws.send_str('hello')
        self.assertEqual((await ws.receive()).data, 'hello')
        await ws.close()


class OriginTests(unittest.TestCase):
    def test_exact_safe_origin_formats(self):
        self.assertTrue(validate_origin('https://8080-cs-123.cs-example.cloudshell.dev'))
        for value in ('https://cloudshell.dev.evil.example', 'https://foo.cloudshell.dev/path',
                      'http://foo.cloudshell.dev', 'https://user@foo.cloudshell.dev'):
            self.assertFalse(validate_origin(value))
        self.assertFalse(validate_origin('http://127.0.0.1:8080'))
        self.assertTrue(validate_origin('http://127.0.0.1:8080', True))
        self.assertTrue(validate_origin('http://localhost:8090', True))
        self.assertFalse(validate_origin('http://localhost.evil.example:8090', True))


if __name__ == '__main__':
    unittest.main()
