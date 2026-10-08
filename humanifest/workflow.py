"""Native state-to-guidance catalog; suggestions never grant authority."""

WORKFLOW_ACTIONS = {
    "QUEUED": "Audit humanitarian relevance and contribution policies using read-only sources.",
    "PROJECT-AUDIT": "Complete the project audit and record evidence before shortlisting an issue.",
    "OPPORTUNITY-RESEARCH": "Verify the issue is current and bound its code surface and regression strategy.",
    "SHORTLISTED": "Prepare a maintainer inquiry; confirm authorization for this exact issue and verify the Humanifest posting identity before sending.",
    "MAINTAINER-CHECK": "Check for maintainer confirmation; respond only within authorization for this exact opportunity using the verified Humanifest identity.",
    "ENVIRONMENT-READY": "Reproduce with synthetic data in the inspected environment; record results.",
    "REPRODUCED": "Check all hard gates and portfolio capacity before starting the approved bounded implementation.",
    "BUILDING": "Complete the bounded change and regression tests, then prepare adversarial review.",
    "ADVERSARIAL-REVIEW": "Review correctness, scope, security, tests, and maintainer burden before human review.",
    "HUMAN-REVIEW": "Review the change line by line and check PR capacity, authorization for this exact PR, and the Humanifest posting identity before opening it.",
    "PR-OPEN": "Review upstream feedback; respond and update only within authorization for this exact PR using the verified Humanifest identity.",
    "MERGED": "Verify release and deployment evidence without assuming that merge proves humanitarian impact.",
    "RELEASED": "Record observed retention and outcomes with sources; do not infer impact from release alone.",
    "PARKED": "Keep parked until the stopping reason is resolved and evidence supports reconsideration.",
    "DECLINED": "Keep declined; do not resume work without a new decision supported by evidence.",
}

# Open handoff destinations have one owner instead of parallel CLI choices and
# renderer branches. The compiled correspondence carries these into handoffs.
HANDOFF_ROUTES = {
    "codex": {
        "prefix": "Use full-reasoning Codex for synthesis, integration, and final go/no-go.",
        "suffix": "",
    },
    "spark": {
        "prefix": "Use a fast Codex model only for bounded inspection or mechanical verification.",
        "suffix": "",
    },
    "cursor-red-team": {
        "prefix": "Act as an independent adversarial reviewer. Do not implement the fix.",
        "suffix": "Focus on hidden scope, security, environment risk, test gaps, and maintainer burden.",
    },
}
