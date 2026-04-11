import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── 1. New hire access recommendation ────────────────────────────────────────

NEW_HIRE_SYSTEM = """You are an expert IT Operations Manager with deep IAM experience.
Given a new hire's details and their department's standard access package, return a JSON object:
{
  "recommended_apps": [
    {
      "app": str,
      "permission_level": str,   // user | read-only | admin
      "rationale": str,           // one sentence
      "sox_sensitive": bool,
      "provisioning_priority": str  // immediate | within_24h | within_week
    }
  ],
  "elevated_access_flags": [str],   // apps where admin may be justified — list reasons
  "provisioning_notes": str          // 2-3 sentences of notes for the IT tech doing the work
}
Return ONLY valid JSON. No markdown, no preamble."""

VIOLATION_SYSTEM = """You are an IAM compliance analyst performing a SOX access review.
Analyze the employee access data and return a JSON array of violations:
[
  {
    "employee_id": str,
    "employee_name": str,
    "violation_type": str,  // "terminated_active_access" | "over_provisioned" |
                            //  "stale_sox_access" | "orphaned_approval" |
                            //  "incomplete_provisioning" | "on_leave_sensitive_access"
    "severity": str,        // "Critical" | "High" | "Medium"
    "apps_affected": [str],
    "description": str,     // 2 sentences: what the violation is and why it matters
    "recommended_action": str  // specific, actionable next step
  }
]
Return ONLY the JSON array. No markdown, no preamble."""

AUDIT_SYSTEM = """You are an IT Operations Manager writing a SOX access review report
for the CTO, CFO, and external auditors. Be direct, specific, and compliance-focused.

Write a structured report:

## Access Review Summary
2-3 sentences: review scope, date, total employees, methodology.

## Critical Findings
List all Critical and High severity violations with employee names, apps affected, and risk.

## SOX Compliance Status
Assess SOX-sensitive system coverage: which systems were reviewed, any access gaps found.

## Risk Assessment
Overall risk rating (Low/Medium/High/Critical) with 3-4 sentence justification.

## Remediation Plan
5 numbered action items, each with: action, responsible party, deadline (relative, e.g. "within 24 hours").

## Sign-off Block
Format as:
Reviewed by: IT Operations Manager
Review date: [today]
Next scheduled review: [90 days from today]
Status: FINDINGS REQUIRE IMMEDIATE ACTION / COMPLIANT WITH NOTED EXCEPTIONS

Use the exact data provided. Reference specific employee IDs and app names."""


def recommend_new_hire_access(hire_info: dict, standard_package: list) -> dict:
    payload = {"new_hire": hire_info, "standard_package": standard_package}
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=NEW_HIRE_SYSTEM,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def detect_violations(employees: list) -> list:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=VIOLATION_SYSTEM,
        messages=[{"role": "user", "content": json.dumps(employees)}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_audit_report(summary: dict) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=AUDIT_SYSTEM,
        messages=[{"role": "user", "content": json.dumps(summary)}],
    )
    return msg.content[0].text.strip()
