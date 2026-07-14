import argparse

def main():
    parser = argparse.ArgumentParser(description="Mercury AI CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # setup command
    subparsers.add_parser("setup", help="Setup Mercury AI connection configurations")
    
    # status command
    subparsers.add_parser("status", help="Check status of integrations and database connectivity")
    
    # ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Run the trace ingestion pipeline")
    ingest_parser.add_argument("--app-id", type=str, help="Application ID to ingest for")
    ingest_parser.add_argument("--lookback-hours", type=int, default=24, help="Time lookback window in hours")
    
    args = parser.parse_args()
    if args.command == "setup":
        print("Setting up Mercury AI...")
    elif args.command == "status":
        print("Checking status...")
    elif args.command == "ingest":
        print(f"Running ingest pipeline for app-id: {args.app_id} (lookback: {args.lookback_hours} hours)...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
