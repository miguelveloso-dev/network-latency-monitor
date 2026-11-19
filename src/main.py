import argparse
import time
from database import get_summary, init_db, save_check
from prober import check_target

DB_PATH = "monitor.db"

# Lista de alvos a monitorizar (Podes adicionar o IP do teu router local!)
TARGETS = [
    ("1.1.1.1", 443),    # Cloudflare
    ("8.8.8.8", 53),     # Google DNS
    ("uminho.pt", 443),  # Universidade do Minho
]


def run_watch(interval: int) -> None:
    init_db(DB_PATH)
    print(f"A monitorizar {len(TARGETS)} alvos a cada {interval}s (Ctrl+C para parar)...\n")
    try:
        while True:
            timestamp = time.strftime("%H:%M:%S")
            for host, port in TARGETS:
                status, latency = check_target(host, port)
                save_check(DB_PATH, host, port, status, latency)
                lat_str = f"{latency} ms" if latency is not None else "---"
                print(f"[{timestamp}] {host}:{port:<5} -> {status:<7} ({lat_str})")
            print("-" * 45)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitorização terminada pelo utilizador.")


def run_report() -> None:
    init_db(DB_PATH)
    rows = get_summary(DB_PATH)
    if not rows:
        print("Ainda não existem dados. Executa primeiro com --watch.")
        return

    print(f"\n{'Alvo':<22} {'Testes':<8} {'Uptime':<9} {'Média':<10} {'Mín':<10} {'Máx':<10}")
    print("-" * 70)
    for target, port, total, online, avg_ms, min_ms, max_ms in rows:
        uptime = (online / total) * 100
        alvo = f"{target}:{port}"
        avg_s = f"{avg_ms} ms" if avg_ms is not None else "---"
        min_s = f"{min_ms} ms" if min_ms is not None else "---"
        max_s = f"{max_ms} ms" if max_ms is not None else "---"
        print(f"{alvo:<22} {total:<8} {uptime:>6.1f}%   {avg_s:<10} {min_s:<10} {max_s:<10}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor de Latência e Disponibilidade de Rede")
    parser.add_argument("--watch", action="store_true", help="Inicia monitorização contínua")
    parser.add_argument("--report", action="store_true", help="Mostra resumo histórico")
    parser.add_argument("--interval", type=int, default=5, help="Segundos entre ciclos (padrão: 5)")
    args = parser.parse_args()

    if args.watch:
        run_watch(args.interval)
    elif args.report:
        run_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()