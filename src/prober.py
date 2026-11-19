import socket
import time


def check_target(host: str, port: int, timeout: float = 2.0) -> tuple[str, float | None]:
    """Tenta abrir uma ligação TCP ao alvo e devolve (estado, latência_ms)."""
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return "ONLINE", round(elapsed_ms, 2)
    except (socket.timeout, socket.gaierror, OSError):
        return "OFFLINE", None


if __name__ == "__main__":
    # Teste rápido direto neste ficheiro
    print("Cloudflare DNS:", check_target("1.1.1.1", 443))
    print("Alvo inválido:", check_target("192.0.2.1", 80, timeout=1.0))