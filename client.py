# client.py

import pygame
import json
import asyncio
import websockets

class OmokClient:
    def __init__(self):
        self.client_id = None
        self.current_player = None
        self.ws = None

    async def main(self):
        pygame.init()
        try:
            uri = "ws://localhost:3000"
            async with websockets.connect(uri) as ws:
                self.ws = ws
                message = await ws.recv()
                data = json.loads(message)
                if data["type"] == "playerId":
                    self.client_id = data["playerId"]
                if data["type"] == "initialPlayer":
                    self.current_player = data["initialPlayer"]

                await self.game()
        except Exception as e:
            print(f"Error in main: {e}")
        finally:
            pygame.quit()

    def get_user_input(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                row = event.pos[1] // 40
                col = event.pos[0] // 40
                return row, col

    async def game(self):
        while True:
            row, col = self.get_user_input()
            await self.ws.send(json.dumps({"type": "placeStone", "position": (row, col), "clientId": self.client_id}))

            try:
                message = await self.ws.recv()
                data = json.loads(message)
                if data["type"] == "updateStones" and data["currentPlayer"] == self.client_id:
                    break
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"ConnectionClosedError: {e}")
                break
            except Exception as e:
                print(f"Unexpected error in game loop: {e}")

async def main():
    client = OmokClient()
    try:
        await client.main()
    except Exception as e:
        print(f"Error in main: {e}")

asyncio.get_event_loop().run_until_complete(main())
