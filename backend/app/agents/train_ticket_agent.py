"""12306 train ticket skill adapter and deterministic recommendation logic."""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


SEAT_FIELDS = ("swz", "zy", "ze", "rw", "dw", "yw", "yz", "wz")


class TrainTicketAgent:
    """Query the local 12306 skill without adding another LLM call."""

    def __init__(self, skill_dir: Optional[str] = None, timeout: int = 30):
        project_root = Path(__file__).resolve().parents[3]
        configured_dir = skill_dir or os.getenv("TRAIN_TICKET_SKILL_DIR", "")
        self.skill_dir = (
            Path(configured_dir).expanduser().resolve()
            if configured_dir
            else project_root / "external" / "12306-skill"
        )
        self.script_path = self.skill_dir / "scripts" / "query.mjs"
        self.node_binary = os.getenv("NODE_BINARY", "node")
        self.timeout = timeout

    async def search_outbound(
        self,
        origin_city: str,
        destination_city: str,
        travel_date: str,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "status": "unavailable",
            "origin_city": origin_city,
            "destination_city": destination_city,
            "date": travel_date,
        }

        if not self.script_path.is_file():
            result["message"] = "12306 Skill 未安装，已跳过去程车票查询"
            return result

        command = (
            self.node_binary,
            str(self.script_path),
            origin_city,
            destination_city,
            "-d",
            travel_date,
            "--available",
            "--json",
        )

        try:
            try:
                completed = await asyncio.to_thread(
                    subprocess.run,
                    command,
                    cwd=str(self.skill_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                result["message"] = "12306 查询超时，已使用普通交通建议"
                return result

            if completed.returncode != 0:
                error_text = completed.stderr.strip()
                result["message"] = error_text[-300:] or "12306 查询失败"
                return result

            raw_tickets = json.loads(completed.stdout)
            if not isinstance(raw_tickets, list):
                raise ValueError("12306 返回格式不是列表")

            tickets = [self._normalize_ticket(ticket) for ticket in raw_tickets]
            tickets = [ticket for ticket in tickets if ticket]
            if not tickets:
                result["message"] = "当前日期未查询到可购买车次"
                return result

            fastest = min(tickets, key=lambda item: item["duration_minutes"])
            recommended = min(tickets, key=self._recommendation_score)
            options = sorted(tickets, key=self._recommendation_score)[:5]

            result.update(
                {
                    "status": "success",
                    "fastest": fastest,
                    "recommended": recommended,
                    "options": options,
                    "message": "余票为查询时刻快照，请以 12306 实时信息为准",
                }
            )
            return result
        except Exception as exc:
            detail = str(exc).strip() or type(exc).__name__
            result["message"] = f"12306 查询不可用：{detail[:200]}"
            return result

    @staticmethod
    def _minutes(value: str) -> int:
        try:
            hours, minutes = value.split(":", 1)
            return int(hours) * 60 + int(minutes)
        except (AttributeError, TypeError, ValueError):
            return 24 * 60

    def _normalize_ticket(self, raw: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(raw, dict) or raw.get("canBuy") != "Y":
            return None

        seats = {
            seat: raw.get(seat)
            for seat in SEAT_FIELDS
            if raw.get(seat) not in (None, "", "--", "无")
        }
        return {
            "train_code": str(raw.get("trainCode", "")),
            "from_station": str(raw.get("fromStation", "")),
            "to_station": str(raw.get("toStation", "")),
            "depart_time": str(raw.get("departTime", "")),
            "arrive_time": str(raw.get("arriveTime", "")),
            "duration": str(raw.get("duration", "")),
            "duration_minutes": self._minutes(str(raw.get("duration", ""))),
            "seats": seats,
        }

    def _recommendation_score(self, ticket: Dict[str, Any]) -> tuple[int, int]:
        depart_minutes = self._minutes(ticket["depart_time"])
        if 7 * 60 <= depart_minutes <= 19 * 60:
            time_penalty = 0
        else:
            time_penalty = 120
        duration = int(ticket["duration_minutes"])
        return duration + time_penalty, depart_minutes
