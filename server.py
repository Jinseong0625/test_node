import asyncio
import json
import websockets

class OmokGame:
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = [[0] * board_size for _ in range(board_size)]
        self.clients = set()
        self.stones = {}
        self.winner = None
        self.current_player = None

    async def notify_state(self):
        if len(self.clients) == 2:
            message = json.dumps({
                "type": "updateStones",
                "stones": self.stones,
                "currentPlayer": self.current_player,
            })
            tasks = [client.send(message) for client in self.clients]
            await asyncio.gather(*tasks)

    async def register(self, websocket):
        self.clients.add(websocket)
        await websocket.send(json.dumps({"type": "playerId", "playerId": len(self.clients)}))

        if len(self.clients) == 2:
            self.current_player = 1
            await self.notify_state()

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        await self.notify_state()

    def place_stone(self, client_id, row, col):
        if len(self.clients) == 2 and \
                (0 <= row < self.board_size) and (0 <= col < self.board_size) and \
                (row, col) not in self.stones.values() and not self.winner and \
                client_id == self.current_player:
            self.stones[client_id] = (row, col)
            self.board[row][col] = 1 if client_id == 1 else 2
            if self.check_winner(row, col):
                self.winner = client_id
            else:
                self.current_player = 2 if self.current_player == 1 else 1
                asyncio.create_task(self.notify_state())

    def check_winner(self, row, col):
        # Check horizontal
        if self.check_line(row, col, 0, 1):
            return True
        # Check vertical
        if self.check_line(row, col, 1, 0):
            return True
        # Check diagonal (top-left to bottom-right)
        if self.check_line(row, col, 1, 1):
            return True
        # Check diagonal (bottom-left to top-right)
        if self.check_line(row, col, -1, 1):
            return True

        return False

    def check_line(self, row, col, row_dir, col_dir):
        player_id = self.board[row][col]
        count = 1  # 현재 위치의 돌부터 시작하므로 1로 초기화

        # Check in one direction
        for i in range(1, 5):
            next_row = row + i * row_dir
            next_col = col + i * col_dir

            if 0 <= next_row < self.board_size and 0 <= next_col < self.board_size \
                    and self.board[next_row][next_col] == player_id:
                count += 1
            else:
                break

        # Check in the opposite direction
        for i in range(1, 5):
            prev_row = row - i * row_dir
            prev_col = col - i * col_dir

            if 0 <= prev_row < self.board_size and 0 <= prev_col < self.board_size \
                    and self.board[prev_row][prev_col] == player_id:
                count += 1
            else:
                break

        return count >= 5

async def handler(websocket, path, omok_game):
    await omok_game.register(websocket)
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data["type"] == "disconnect":
                break
            elif data["type"] == "placeStone":
                row, col = data["position"]
                omok_game.place_stone(len(omok_game.clients), row, col)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"ConnectionClosedError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await omok_game.unregister(websocket)

omok_game = OmokGame()
start_server = websockets.serve(lambda ws, path: handler(ws, path, omok_game), "localhost", 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
