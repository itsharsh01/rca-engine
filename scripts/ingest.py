import argparse

def main():
    parser = argparse.ArgumentParser(description="Ingest traces helper script")
    parser.add_argument("--app-id", type=str, required=True)
    parser.add_argument("--lookback-hours", type=int, default=24)
    args = parser.parse_args()
    print(f"Ingesting traces for {args.app_id} (lookback: {args.lookback_hours})...")

if __name__ == "__main__":
    main()
