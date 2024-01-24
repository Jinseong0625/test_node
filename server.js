// server.js

const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.static('public'));

wss.on('connection', (ws) => {
  // 클라이언트가 연결되었을 때 실행되는 로직
  console.log('Client connected');

  // 클라이언트로부터 메시지를 받았을 때 실행되는 로직
  ws.on('message', (message) => {
    const parsedMessage = JSON.parse(message);
    console.log(`Received message from ${parsedMessage.nickname}: ${parsedMessage.content}`);
  

    // 모든 클라이언트에게 메시지 전송
    /*wss.clients.forEach((client) => {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(message);
      }*/

      // 모든 클라이언트에게 메시지 전송
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
            nickname: parsedMessage.nickname,
            content: parsedMessage.content
          }));
        }
      });
    });

  // 클라이언트가 연결을 종료했을 때 실행되는 로직
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
