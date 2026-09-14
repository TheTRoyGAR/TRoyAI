#!/usr/bin/env python3
"""TRoyAI E-Automation Agency — Entry Point"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from agency.core.agency import TRoyAIAgency


def main():
    agency = TRoyAIAgency()

    if len(sys.argv) < 2:
        print(json.dumps(agency.status(), indent=2))
        print()
        print("Usage: python main.py <command> [args]")
        print("Commands:")
        print("  briefing              — Daily CEO briefing")
        print("  sales <brief>         — Run sales pipeline")
        print("  marketing <brief>     — Run marketing campaign")
        print("  finance [period]      — Generate finance report")
        print("  cto <brief>           — Run CTO task")
        print("  intake <brief>        — Full orchestration: TRoyVibe read, delegate, review, QA")
        print("  status                — Agency status")
        return

    command = sys.argv[1]
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if command == "briefing":
        print(agency.run_daily_briefing(args))
    elif command == "sales":
        print(agency.run_sales_pipeline(args))
    elif command == "marketing":
        print(agency.run_marketing_campaign(args))
    elif command == "finance":
        print(agency.run_finance_report(args or "monthly"))
    elif command == "cto":
        print(agency.run_cto_task(args))
    elif command == "intake":
        print(agency.intake_brief(args))
    elif command == "status":
        print(json.dumps(agency.status(), indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
