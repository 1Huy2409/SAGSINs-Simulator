import { io } from "socket.io-client";

const socket = io("http://172.28.118.59:3000", {
  transports: ["websocket"],
});

export default socket;
