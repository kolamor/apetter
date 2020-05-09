import asyncio
import aiohttp
from aiohttp import web
from pyppeteer import launch
import logging

# logger = logging.getLogger(__name__)


class Rout(web.View):

    async def post(self):
        try:
            _json = await self.request.json()
            if 'url' not in _json.keys():
                return web.json_response({'error': 'need url'}, status=400)
        except Exception as e:
            logging.error(f'{e} , {e.args}')
            return web.json_response({'error': 'error json'}, status=400)
        resp = await peteer(self.request.app, _json)
        return web.json_response(resp, status=200)


def setup_routes(app):
    app.router.add_routes([
        web.post('/', Rout),
        ])


async def create_app(config: dict):
    app = web.Application()
    app['config'] = config
    app.on_startup.append(on_start)
    # app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    setup_routes(app)


async def peteer(app, _json):
    proxy = _json.get('proxy', None)
    proxy = proxy if proxy else app['config']['web_proxy']
    args_webkit = []
    proxy_user = proxy_pass = None
    if proxy:
        proxy = f'--proxy-server={proxy}'
        args_webkit.append(proxy)
        basic_auth = _json.get('proxy_auth', None)
        try:
            proxy_user, proxy_pass = basic_auth.split(':')
        except Exception as e:
            logging.error(f'{e} , {e.args}')

    cookies = _json.get('cookies', None)
    js_code = _json.get('js_code', None)
    url = _json.get('url', None)

    browser = await launch(
        headless=False,
        ignoreHTTPSErrors=True,
        args=args_webkit
    )
    page = await browser.newPage()
    # cookies = {'name': 'name', 'value':'value'}
    # cookies = [{'name':'name1', 'value': 'bcc4e79fa45a9471ea6fcde17cf2ec1c'},
    #            { 'name': 'name2', 'value': '1'},
    #            ]
    try:
        if proxy_user and proxy_pass:
            await page.authenticate({'username' : proxy_user, 'password' : proxy_pass})
        # await page.goto('https://url.com/',)
        await page.goto(url=url)
        await asyncio.sleep(1)
        try:
            if cookies:
                await page.setCookie(*cookies)
                await page.reload()

        except Exception as e:
            logging.error(f'{e} , {e.args}')
        await asyncio.sleep(2)

        if js_code:
            dimensions = await page.evaluate(js_code)
            print(dimensions)
        await asyncio.sleep(2)
        text = await page.content()
        # await page.screenshot({'path': 'example.png'})
    except Exception as e:
        logging.error(f'{e} , {e.args}')
        print(e, e.args)
        return {'error': f'{e} :-: {e.args}'}
    finally:
        await browser.close()
    return {'text': text}


if __name__ == '__main__':
    if __name__ == "__main__":
        config = {"web_proxy": None}
        logging.basicConfig(level=logging.DEBUG)
        app = create_app(config)
        aiohttp.web.run_app(app, host='127.0.0.1', port=5000)
