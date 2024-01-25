const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.static('public'));

const clients = new Set();

let messageCounter = 0; // 메시지의 고유 ID를 저장하기 위한 변수

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    console.log('Received message from client:', message);
    const parsedMessage = JSON.parse(message);

    if (parsedMessage.event === 'setNickname') {
      // 클라이언트에서 서버로 닉네임 설정 요청
      ws.nickname = parsedMessage.nickname;

      // 클라이언트 목록에 추가
      clients.add(ws);

      // 입장 메시지 전송
      const joinMessage = `${ws.nickname} has joined the chat.`;

      // 고유 ID를 부여한 입장 메시지 전송
      const messageId = messageCounter++;
      clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          if (client !== ws) {
            // 새로운 클라이언트에게 입장 메시지 전송
            client.send(JSON.stringify({ event: 'userJoined', userList: Array.from(clients).map(client => client.nickname), message: joinMessage, messageId }));
          }
          // 기존 클라이언트에게 새로운 클라이언트의 닉네임을 포함한 입장 메시지 전송
          ws.send(JSON.stringify({ event: 'userJoined', userList: Array.from(clients).map(client => client.nickname), message: joinMessage, messageId }));
        }
      });
    } else if (parsedMessage.event === 'sendMessage') {
      // 클라이언트에서 서버로 메시지 전송 요청
      const messageToSend = {
        nickname: ws.nickname,
        content: parsedMessage.content
      };

      // 모든 클라이언트에게 메시지 전송
      clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(messageToSend));
        }
      });
    }
  });
  
    ws.on('close', () => {
      console.log('Client disconnected');
  
      // 클라이언트 목록에서 제거
      clients.delete(ws);
  
      // 클라이언트가 연결 종료시 사용자 목록 업데이트
      const userList = Array.from(clients).map(client => client.nickname);
      clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          // 사용자가 퇴장한 경우 메시지 전송
          client.send(JSON.stringify({ event: 'userLeft', nickname: ws.nickname, userList }));
        }
      });
    });
  });

server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
