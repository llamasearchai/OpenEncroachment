from __future__ import annotations

import argparse
import json
import subprocess
import sys

from .analytics.predictive import predict_geofence_risk
from .case_management.case_manager import CaseManager
from .config import load_config
from .evidence.chain_of_custody import verify_ledger
from .pipeline import run_pipeline


def cmd_run_pipeline(args: argparse.Namespace) -> None:
    result = run_pipeline(config_path=args.config, use_sample_data=args.sample_data)
    print(json.dumps(result, indent=2))


def cmd_predict(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    cm = CaseManager(db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db"))
    incs = cm.list_incidents(limit=1000)
    res = predict_geofence_risk(cfg, incs)
    print(json.dumps(res, indent=2))


def cmd_case(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    cm = CaseManager(db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db"))
    if args.action == "list":
        print(json.dumps(cm.list_cases(limit=args.limit), indent=2))
    elif args.action == "incidents":
        print(json.dumps(cm.list_incidents(limit=args.limit), indent=2))


def cmd_evidence(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    ok, n = verify_ledger(cfg)
    print(json.dumps({"ok": ok, "checked": n}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="open-encroachment", description="OpenEncroachment CLI")
    p.add_argument("--config", default="config/settings.yaml", help="Path to YAML config")
    sub = p.add_subparsers(dest="cmd", required=True)

    rp = sub.add_parser("run-pipeline", help="Run end-to-end pipeline")
    rp.add_argument("--sample-data", action="store_true", help="Generate/use sample data inputs")
    rp.set_defaults(func=cmd_run_pipeline)

    pr = sub.add_parser("predict", help="Compute geofence risk map")
    pr.set_defaults(func=cmd_predict)

    cm = sub.add_parser("case", help="Case management operations")
    cm.add_argument("action", choices=["list", "incidents"], help="Action to perform")
    cm.add_argument("--limit", type=int, default=20)
    cm.set_defaults(func=cmd_case)

    ev = sub.add_parser("evidence", help="Verify evidence ledger")
    ev.set_defaults(func=cmd_evidence)

    ag = sub.add_parser("agent", help="Agent operations")
    ag.add_argument("rest", nargs=argparse.REMAINDER, help="Arguments passed to agent CLI")

    def cmd_agent(args: argparse.Namespace) -> None:
        call = [sys.executable, "-m", "open_encroachment.agents.cli"] + args.rest
        sys.exit(subprocess.call(call))

    ag.set_defaults(func=cmd_agent)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)

