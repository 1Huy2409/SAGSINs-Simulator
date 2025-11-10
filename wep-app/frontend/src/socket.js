import { io } from "socket.io-client";

const socket = io("http://172.29.176.1:3000", {
  transports: ["websocket"],
});

export default socket;
