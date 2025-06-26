import socket
import threading
import json

class TrackmanUDPListener(threading.Thread):
    def __init__(self, callback, port=20998, buffer_size=16384):
        super().__init__(daemon=True)
        self.port = port
        self.buffer_size = buffer_size
        self.callback = callback
        self._running = True
        self.sock = None

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # ✅ CRITICAL: bind to all interfaces
        self.sock.bind(('', self.port))
        self.sock.settimeout(1.0)

        print(f"[Trackman] ✅ Listening on UDP port {self.port}...")

        while self._running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                print(f"[Trackman] 🟢 {len(data)} bytes from {addr}")

                try:
                    message = json.loads(data.decode('utf-8'))
                    print("[Trackman] ✅ Parsed as JSON")
                    self.callback(message)
                except json.JSONDecodeError as e:
                    print("[Trackman] ❌ JSON decode failed:", e)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Trackman] General error: {e}")


    def stop(self):
        self._running = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(b'{}', ('127.0.0.1', self.port))
        except Exception as e:
            print(f"[Trackman] Dummy packet error: {e}")
        if self.sock:
            self.sock.close()
