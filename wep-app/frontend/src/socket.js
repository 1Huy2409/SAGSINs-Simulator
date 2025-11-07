import { io } from "socket.io-client";

const socket = io("http://192.168.2.5:3000", {
  transports: ["websocket"],
});

export default socket;
