"""Python-owned Metamap shard and immutable, current-record report projection.

This module proves local correspondence only. Records, native validators and the
protocol retain authority; a viable graph grants no permission or truth claim.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from urllib.parse import quote

from .models import HARD_GATES, load_json, load_portfolio
from .workflow import HANDOFF_ROUTES, WORKFLOW_ACTIONS

PREFIX = "urn:humanifest:"
PRODUCER = {"status": "generated", "assertedBy": "humanifest-python-shard@1"}
CONTROL_FILES = (
    "AGENTS.md", "GOALS.md", "README.md", "docs/contribution-protocol.md",
    "schemas/project.schema.json", "schemas/opportunity.schema.json",
    "humanifest/models.py", "humanifest/workflow.py", "humanifest/correspondence.py",
    "metamap/exclusions.json", "tools/metamap/compile.mjs", "tools/metamap/package-lock.json",
    "tools/metamap/package.json", "scripts/compile_correspondence.py",
)


def digest(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                                separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def identity(kind, name):
    return PREFIX + kind + ":" + quote(name, safe="-._~")


def snapshot(root):
    paths = [root / name for name in CONTROL_FILES]
    paths += sorted((root / "portfolio/projects").glob("*.json"))
    paths += sorted((root / "portfolio/opportunities").glob("*.json"))
    # Authored reusable prompts are projections too, but are not silently treated
    # as generated from today's records. Each needs a current explicit exclusion.
    paths += sorted((root / "handoffs").glob("*.md"))
    return {str(p.relative_to(root)): "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def export_shard(root: Path):
    root = root.resolve()
    projects, opportunities, issues = load_portfolio(root)
    if issues:
        raise ValueError("; ".join(f"{i.record}: {i.message}" for i in issues))
    inputs = snapshot(root)
    graph = {"schemaVersion": "2.0.0", "id": PREFIX + "portfolio", "namespace": "humanifest",
             "revision": digest(inputs), "entities": [], "mappings": [], "authorities": [],
             "relationPacks": [{"id": "urn:metamap:relation-pack:routing", "version": "1.0.0"},
                               {"id": PREFIX + "relations", "version": "1.0.0"}]}
    relations = {}

    def entity(kind, name, label=None, **attrs):
        eid = identity(kind, name)
        graph["entities"].append({"id": eid, "kind": kind, "label": label or name,
                                  "attributes": attrs, "provenance": PRODUCER.copy()})
        return eid

    def link(relation, source, target):
        graph["mappings"].append({"id": identity("mapping", digest([relation, source, target])[7:]),
                                  "relation": relation, "sources": [source], "targets": [target],
                                  "cardinality": "one-to-one", "lossiness": "lossless",
                                  "provenance": PRODUCER.copy()})
        if relation.startswith("hf:"):
            relations[relation] = {"id": relation, "description": relation.removeprefix("hf:"),
                                   "cardinalities": ["one-to-one"], "cyclePolicy": "allow",
                                   "impactDirection": "target-to-source"}

    def authority(subject, source):
        graph["authorities"].append({"id": identity("authority", subject), "concept": subject,
                                      "source": source, "facts": ["current-record"], "mode": "canonical",
                                      "provenance": PRODUCER.copy()})

    policy_id = entity("routing:policy", "contribution-protocol", path="docs/contribution-protocol.md",
                       digest=inputs["docs/contribution-protocol.md"], authorizationGranted=False)
    actor = entity("hf:actor", "humanifest-bot", verifiedAtRuntime=False)
    handler = entity("routing:handler", "guidance", locator="python:humanifest.models.next_action",
                     executable=False)
    schema = entity("routing:schema", "opportunity", path="schemas/opportunity.schema.json",
                    digest=inputs["schemas/opportunity.schema.json"])
    for state, text in WORKFLOW_ACTIONS.items():
        action = entity("routing:command", state, text, state=state, authorizationGranted=False)
        for rel, target in [("routing:handled_by", handler), ("routing:accepts", schema),
                            ("routing:authorized_by", policy_id), ("hf:actor", actor)]:
            link(rel, action, target)

    handoff_handler = entity("routing:handler", "handoff", locator="python:humanifest.models.generate_handoff", executable=False)
    for target, route in HANDOFF_ROUTES.items():
        action = entity("routing:command", "handoff-" + target, target, target=target, **route)
        for rel, dest in [("routing:handled_by", handoff_handler), ("routing:accepts", schema),
                          ("routing:authorized_by", policy_id), ("hf:actor", actor)]:
            link(rel, action, dest)

    for kind, records, folder in [("hf:project", projects, "projects"), ("hf:opportunity", opportunities, "opportunities")]:
        for record in records:
            path = next(p for p in (root / "portfolio" / folder).glob("*.json") if load_json(p)["id"] == record["id"])
            relative = str(path.relative_to(root))
            rid = entity(kind, record["id"], record.get("name", record.get("title")), recordId=record["id"],
                         path=relative, digest=inputs[relative], projectId=record.get("project_id"))
            current = entity("hf:record", relative, path=relative, digest=inputs[relative])
            link("hf:current_record", rid, current)
            authority(rid, current)
            for src in record["sources"]:
                sid = entity("hf:source", rid + ":" + src["id"], url=src["url"], accessed=src["accessed"])
                link("hf:source", rid, sid)
                link("hf:current_record", sid, current)
            for index, item in enumerate(record.get("evidence", record.get("impact_evidence", []))):
                eid = entity("hf:evidence", rid + ":" + str(index), item["claim"], evidenceType=item["type"])
                link("hf:evidence", rid, eid)
                link("hf:source", eid, identity("hf:source", rid + ":" + item["source_id"]))
                link("hf:current_record", eid, current)
            if kind == "hf:project":
                continue
            link("hf:project", rid, identity("hf:project", record["project_id"]))
            link("hf:guidance", rid, identity("routing:command", record["pipeline_state"]))
            link("hf:policy", rid, policy_id)
            link("hf:actor", rid, actor)
            for target in HANDOFF_ROUTES:
                link("hf:handoff_route", rid, identity("routing:command", "handoff-" + target))
            for gate in HARD_GATES:
                item = record["gates"][gate]
                gid = entity("hf:gate", rid + ":" + gate, gate, passed=item["passed"],
                             cited=bool(item.get("source_ids")), rationale=item["rationale"])
                link("hf:gate", rid, gid)
                link("hf:current_record", gid, current)
                for src in item.get("source_ids", []):
                    link("hf:source", gid, identity("hf:source", rid + ":" + src))
                # Prerequisites are references to native gate decisions, not a
                # second state machine or permission to perform a transition.
                link("hf:prerequisite", rid, gid)
                if gate == "maintainer_interest_confirmed":
                    confirmation = entity("hf:confirmation", record["id"], confirmed=item["passed"])
                    link("hf:confirmation", gid, confirmation)
                    link("hf:current_record", confirmation, current)
                    for src in item.get("source_ids", []):
                        link("hf:source", confirmation, identity("hf:source", rid + ":" + src))
            contribution = entity("hf:contribution", record["id"], recordedState=record["pipeline_state"], deliveryEvidenceRequired=True)
            link("hf:current_record", contribution, current)
            for output_kind in ("hf:report", "hf:handoff"):
                output = entity(output_kind, record["id"], generated=True)
                link("hf:output", rid, output)
                link("hf:current_record", output, current)
                link("hf:project", output, identity("hf:project", record["project_id"]))
                link("hf:policy", output, policy_id)
                link("hf:actor", output, actor)
                link("hf:guidance", output, identity("routing:command", record["pipeline_state"]))

    exclusions = load_json(root / "metamap/exclusions.json")["exclusions"]
    used = set()
    for path in sorted((root / "handoffs").glob("*.md")):
        relative = str(path.relative_to(root))
        match = [x for x in exclusions if x.get("path") == relative]
        if len(match) != 1:
            raise ValueError(f"{relative}: authored handoff needs one explicit relation-scoped exclusion")
        exclusion = match[0]
        if (exclusion.get("digest") != inputs[relative] or not isinstance(exclusion.get("reason"), str) or not exclusion["reason"].strip()
                or not isinstance(exclusion.get("owner"), str) or not exclusion["owner"].strip() or exclusion.get("relations") != ["hf:current_record"]):
            raise ValueError(f"{relative}: stale or invalid projection exclusion")
        used.add(relative)
        entity("hf:authored-handoff", relative, topologyDisposition="excluded",
               exclusionRelations=exclusion["relations"], exclusionReason=exclusion["reason"],
               exclusionOwner=exclusion["owner"])
    if used != {e.get("path") for e in exclusions}:
        raise ValueError("stale projection exclusion: its authored handoff no longer exists")

    constraints = []
    def total(kinds, rel, cardinality="exactly-one", **extra):
        constraints.append({"id": identity("constraint", str(len(constraints))),
                            "kind": "topology:relation-totality", "subjects": [graph["id"]],
                            "parameters": {"subjectKinds": kinds, "relation": rel, "direction": "source",
                                           "cardinality": cardinality, **extra}})

    for rel in ("routing:handled_by", "routing:accepts", "routing:authorized_by", "hf:actor"):
        total(["routing:command"], rel)
    total(["hf:project", "hf:opportunity", "hf:evidence", "hf:source", "hf:gate", "hf:confirmation",
           "hf:contribution", "hf:report", "hf:handoff"], "hf:current_record")
    total(["hf:opportunity", "hf:report", "hf:handoff"], "hf:project", counterpartKinds=["hf:project"])
    for rel in ("hf:guidance", "hf:policy", "hf:actor"):
        total(["hf:opportunity", "hf:report", "hf:handoff"], rel)
    total(["hf:project", "hf:opportunity", "hf:evidence"], "hf:source", "one-or-more")
    total(["hf:opportunity"], "hf:gate", "one-or-more")
    total(["hf:opportunity"], "hf:prerequisite", "one-or-more")
    total(["hf:opportunity"], "hf:output", "one-or-more")
    total(["hf:opportunity"], "hf:handoff_route", "one-or-more", counterpartKinds=["routing:command"])
    if any(e["kind"] == "hf:gate" and e["attributes"]["cited"] for e in graph["entities"]):
        total(["hf:gate"], "hf:source", "one-or-more", subjectAttributes={"cited": True})
    if any(e["kind"] == "hf:confirmation" and e["attributes"]["confirmed"] for e in graph["entities"]):
        total(["hf:confirmation"], "hf:source", "one-or-more", subjectAttributes={"confirmed": True})
    if used:
        total(["hf:authored-handoff"], "hf:current_record", allowExcluded=True)
    constraints.append({"id": PREFIX + "constraint:exact-authority", "kind": "hf:exact-authority",
                        "subjects": [graph["id"]], "parameters": {"gates": HARD_GATES, "handoffTargets": list(HANDOFF_ROUTES)}})
    policy = {"schemaVersion": "1.0.0", "id": PREFIX + "viability", "graph": {"id": graph["id"], "revision": graph["revision"]},
              "mappings": [{"select": {"relations": sorted({m["relation"] for m in graph["mappings"]})},
                            "coverage": "total", "determinism": "deterministic", "reversibility": "irreversible"}],
              "constraints": constraints, "evidence": []}
    kinds = {
        "hf:current_record": (["hf:project", "hf:opportunity", "hf:source", "hf:evidence", "hf:gate",
                               "hf:confirmation", "hf:contribution", "hf:report", "hf:handoff", "hf:authored-handoff"], ["hf:record"]),
        "hf:source": (["hf:project", "hf:opportunity", "hf:evidence", "hf:gate", "hf:confirmation"], ["hf:source"]),
        "hf:evidence": (["hf:project", "hf:opportunity"], ["hf:evidence"]),
        "hf:project": (["hf:opportunity", "hf:report", "hf:handoff"], ["hf:project"]),
        "hf:guidance": (["hf:opportunity", "hf:report", "hf:handoff"], ["routing:command"]),
        "hf:policy": (["hf:opportunity", "hf:report", "hf:handoff"], ["routing:policy"]),
        "hf:actor": (["routing:command", "hf:opportunity", "hf:report", "hf:handoff"], ["hf:actor"]),
        "hf:gate": (["hf:opportunity"], ["hf:gate"]),
        "hf:prerequisite": (["hf:opportunity"], ["hf:gate"]),
        "hf:confirmation": (["hf:gate"], ["hf:confirmation"]),
        "hf:output": (["hf:opportunity"], ["hf:report", "hf:handoff"]),
        "hf:handoff_route": (["hf:opportunity"], ["routing:command"]),
    }
    for relation, definition in relations.items():
        definition["sourceKinds"], definition["targetKinds"] = kinds[relation]
    pack = {"schemaVersion": "1.0.0", "id": PREFIX + "relations", "version": "1.0.0", "relations": list(relations.values())}
    spec = {"schemaVersion": "1.0.0", "id": PREFIX + "report-projection", "select": {"kinds": ["hf:opportunity"]},
            "slots": [{"name": name, "relation": relation, "direction": "outgoing", "cardinality": cardinality}
                      for name, relation, cardinality in [("project", "hf:project", "exactly-one"),
                          ("guidance", "hf:guidance", "exactly-one"), ("authority", "hf:current_record", "exactly-one"),
                          ("outputs", "hf:output", "one-or-more"), ("policy", "hf:policy", "exactly-one"),
                          ("actor", "hf:actor", "exactly-one"), ("handoff_routes", "hf:handoff_route", "one-or-more")]]}
    return {"inputs": inputs, "graph": graph, "policy": policy, "pack": pack, "spec": spec}


@dataclass(frozen=True)
class PortfolioProjection:
    guidance: MappingProxyType
    handoff_routes: MappingProxyType


def load_projection(root: Path):
    """No Node, graph traversal, external reads, permissions or state mutations."""
    root = root.resolve()
    artifact = load_json(root / "metamap/generated/portfolio.json")
    current = snapshot(root)
    if artifact.get("inputs") != current:
        raise ValueError("stale Metamap projection: regenerate against current records and protocol")
    projection = artifact.get("projection", {})
    if artifact.get("projection_checksum") != digest(projection):
        raise ValueError("Metamap projection checksum mismatch")
    result = {}
    routes = {}
    try:
        for entry in projection["entries"]:
            record_id = entry["subject"]["attributes"]["recordId"]
            slots = {s["name"]: s["targets"] for s in entry["slots"]}
            authority = slots["authority"][0]["attributes"]
            if len(slots["authority"]) != 1 or authority["digest"] != current[authority["path"]]:
                raise ValueError("detached current record authority")
            if len(slots["project"]) != 1 or len(slots["guidance"]) != 1 or len(slots["outputs"]) != 2:
                raise ValueError("incomplete projection linkage")
            if record_id in result:
                raise ValueError("duplicate projected record")
            record = load_json(root / authority["path"])
            project = slots["project"][0]["attributes"]
            action = slots["guidance"][0]
            if (record["id"] != record_id or record["project_id"] != project["recordId"]
                    or current.get(project["path"]) != project["digest"]
                    or action["attributes"]["state"] != record["pipeline_state"]
                    or action["label"] != WORKFLOW_ACTIONS[record["pipeline_state"]]
                    or len(slots["policy"]) != 1 or len(slots["actor"]) != 1
                    or slots["policy"][0]["attributes"]["digest"] != current["docs/contribution-protocol.md"]
                    or slots["actor"][0]["id"] != identity("hf:actor", "humanifest-bot")):
                raise ValueError("projection detached from record, policy, identity or workflow guidance")
            projected_routes = {}
            for route in slots["handoff_routes"]:
                attrs = route["attributes"]
                name = attrs["target"]
                values = {key: attrs[key] for key in ("prefix", "suffix")}
                if name in projected_routes or values != HANDOFF_ROUTES.get(name):
                    raise ValueError("handoff route differs from current route authority")
                projected_routes[name] = values
            if set(projected_routes) != set(HANDOFF_ROUTES):
                raise ValueError("incomplete handoff routing projection")
            routes = projected_routes
            result[record_id] = action["label"]
        expected = {load_json(p)["id"] for p in (root / "portfolio/opportunities").glob("*.json")}
        if set(result) != expected:
            raise ValueError("projection does not cover exact current portfolio")
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("malformed Metamap portfolio projection") from error
    return PortfolioProjection(MappingProxyType(result), MappingProxyType({k: MappingProxyType(v) for k, v in routes.items()}))
