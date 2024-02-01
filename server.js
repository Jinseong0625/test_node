// Express 및 WebSocket 라이브러리 import
const express = require('express');
const http = require('http');
const WebSocket = require('ws');

// Express 애플리케이션 및 HTTP 서버 생성
const app = express();
const server = http.createServer(app);

// WebSocket 서버 생성
const wss = new WebSocket.Server({ server });

// 정적 파일 제공을 위한 미들웨어 설정
app.use(express.static('public'));

// 클라이언트 저장을 위한 Set 생성
const clients = new Set();

// 메시지의 고유 ID를 저장하기 위한 변수
let messageCounter = 0;

// 클라이언트가 WebSocket에 연결되면 실행되는 콜백 함수
wss.on('connection', (ws) => {
  console.log('Client connected');

  // 클라이언트로부터 메시지를 수신했을 때 실행되는 콜백 함수
  ws.on('message', (message) => {
    console.log('Received message from client:', message);
    const parsedMessage = JSON.parse(message);

    // 클라이언트가 닉네임 설정을 요청한 경우
    if (parsedMessage.event === 'setNickname') {
      // 클라이언트의 소켓에 닉네임 설정
      ws.nickname = parsedMessage.nickname;

      // 클라이언트를 클라이언트 목록에 추가
      clients.add(ws);

      // 클라이언트 입장 메시지 생성
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
    } 
    // 클라이언트가 메시지를 전송한 경우
    else if (parsedMessage.event === 'sendMessage') {
      // 클라이언트의 메시지를 모든 클라이언트에게 전송
      const messageToSend = {
        nickname: ws.nickname,
        content: parsedMessage.content
      };

      clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(messageToSend));
        }
      });
    }
  });

  // 클라이언트가 연결을 종료한 경우
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

// 서버를 지정된 포트로 listen
server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
