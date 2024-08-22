import os
import signal
import sys
import asyncio
from aiohttp import web
from src.api import create_app
from src.cli import run_cli


class Config:
    HOST = "0.0.0.0"
    HTTP_PORT = 5000

def get_file_path_from_args() -> str:
    default_file_path = "routes.csv"

    if len(sys.argv) > 1 and sys.argv[1]:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"File '{file_path}' not found. Using default '{default_file_path}'.")
    return default_file_path

async def run_server(app: web.Application) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, Config.HOST, Config.HTTP_PORT)
    await site.start()
    print(f"Server started at http://{Config.HOST}:{Config.HTTP_PORT}")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        print("Server task cancelled")
    finally:
        print("Shutting down the server...")
        await runner.cleanup()

async def run_cli_with_shutdown(file_path: str, stop_event: asyncio.Event) -> None:
    cli_task = asyncio.create_task(run_cli(file_path, stop_event))
    try:
        await cli_task
    except asyncio.CancelledError:
        pass

async def main(file_path: str, run_cli_option: bool, run_web_option: bool) -> None:
    tasks = []
    stop_event = asyncio.Event()

    if run_web_option:
        app = create_app(file_path)
        tasks.append(asyncio.create_task(run_server(app)))

    if run_cli_option:
        await asyncio.sleep(0.2)
        tasks.append(asyncio.create_task(run_cli_with_shutdown(file_path, stop_event)))

    if tasks:
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("Main task cancelled, shutting down.")

def handle_exit_signal(loop, stop_event):
    print("Received exit signal, shutting down...")
    stop_event.set()
    for task in asyncio.all_tasks(loop):
        task.cancel()

if __name__ == '__main__':
    file_path = get_file_path_from_args()
    run_cli_option = '--cli' in sys.argv
    run_web_option = '--web' in sys.argv

    if not run_cli_option and not run_web_option:
        run_cli_option = True
        run_web_option = True

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop_event = asyncio.Event()

    # Configura manipuladores de sinal para encerramento gracioso
    for signal_name in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(
            getattr(signal, signal_name),
            lambda: handle_exit_signal(loop, stop_event)
        )

    try:
        loop.run_until_complete(main(file_path, run_cli_option, run_web_option))
    except KeyboardInterrupt:
        print("Application interrupted by user.")
    finally:
        print("Application shutdown.")
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()