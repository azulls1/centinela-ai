#!/usr/bin/env python3
"""
NXT AI Development - MCP Manager
=================================
Functional manager for MCP (Model Context Protocol) servers.

Reads .claude/mcp.json for server definitions, validates environment
variables, maps skills to servers via .nxt/skill-mcp-mapping.yaml,
and provides a working CLI for inspection and diagnostics.

Version: 3.8.0
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

try:
    from utils import get_project_root
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import get_project_root

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MCPServer:
    """A single MCP server entry parsed from .claude/mcp.json."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    disabled: bool = False
    required_env_vars: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    @property
    def enabled(self) -> bool:
        return not self.disabled


# ---------------------------------------------------------------------------
# Core manager
# ---------------------------------------------------------------------------

class MCPManager:
    """
    Reads and validates MCP server configuration.

    Responsibilities:
      - Parse .claude/mcp.json into MCPServer objects
      - Detect required env vars from ${VAR} references
      - Validate that those env vars are set in the current environment
      - Load skill-to-MCP mapping from .nxt/skill-mcp-mapping.yaml
      - Provide query methods for status, listing, checking, and skill lookup
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = root or get_project_root()
        self.mcp_config_path = self.root / ".claude" / "mcp.json"
        self.skill_mapping_path = self.root / ".nxt" / "skill-mcp-mapping.yaml"
        self.servers: Dict[str, MCPServer] = {}
        self.skill_mcp: Dict[str, List[str]] = {}
        self.mcp_skills: Dict[str, List[str]] = {}

        self._load_mcp_config()
        self._load_skill_mapping()

    # -- Loading ---------------------------------------------------------------

    def _load_mcp_config(self) -> None:
        """Parse .claude/mcp.json into MCPServer objects."""
        if not self.mcp_config_path.exists():
            return

        with open(self.mcp_config_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for name, cfg in raw.get("mcpServers", {}).items():
            env = cfg.get("env", {})
            required = self._extract_env_vars(env)
            disabled = cfg.get("disabled", False)

            self.servers[name] = MCPServer(
                name=name,
                command=cfg.get("command", ""),
                args=cfg.get("args", []),
                env=env,
                description=cfg.get("description", ""),
                disabled=disabled,
                required_env_vars=required,
            )

    @staticmethod
    def _extract_env_vars(env: Dict[str, str]) -> List[str]:
        """Extract real env-var names from ${VAR} references."""
        result = []
        for value in env.values():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                result.append(value[2:-1])
        return result

    def _load_skill_mapping(self) -> None:
        """Load .nxt/skill-mcp-mapping.yaml (skill_mcp + mcp_skills sections)."""
        if not self.skill_mapping_path.exists():
            return
        try:
            import yaml
        except ImportError:
            return

        with open(self.skill_mapping_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.skill_mcp = {
            k: (v if isinstance(v, list) else [])
            for k, v in data.get("skill_mcp", {}).items()
        }
        self.mcp_skills = {
            k: (v if isinstance(v, list) else [])
            for k, v in data.get("mcp_skills", {}).items()
        }

        # Attach skill names to each server object
        for skill_name, server_names in self.skill_mcp.items():
            for sname in server_names:
                if sname in self.servers and skill_name not in self.servers[sname].skills:
                    self.servers[sname].skills.append(skill_name)

    # -- Queries ---------------------------------------------------------------

    def get_server(self, name: str) -> Optional[MCPServer]:
        return self.servers.get(name)

    def list_servers(self, *, only_enabled: bool = False) -> List[MCPServer]:
        servers = list(self.servers.values())
        if only_enabled:
            servers = [s for s in servers if s.enabled]
        return sorted(servers, key=lambda s: (s.disabled, s.name))

    def check_env(self, server: MCPServer) -> Dict[str, bool]:
        """Return {VAR_NAME: is_set} for every required env var of a server."""
        return {var: bool(os.environ.get(var)) for var in server.required_env_vars}

    def check_all_env(self) -> Dict[str, Dict[str, bool]]:
        """Run check_env on every server that has required vars."""
        results = {}
        for name, srv in self.servers.items():
            if srv.required_env_vars:
                results[name] = self.check_env(srv)
        return results

    def get_servers_for_skill(self, skill_name: str) -> List[MCPServer]:
        """Return the MCP servers required by a given skill."""
        names = self.skill_mcp.get(skill_name, [])
        return [self.servers[n] for n in names if n in self.servers]

    def get_skills_for_server(self, server_name: str) -> List[str]:
        """Return skills that depend on a given server."""
        return self.mcp_skills.get(server_name, [])

    def server_ready(self, name: str) -> bool:
        """True if the server is enabled and all its env vars are set."""
        srv = self.servers.get(name)
        if srv is None or srv.disabled:
            return False
        return all(os.environ.get(v) for v in srv.required_env_vars)

    def get_status(self) -> Dict[str, Any]:
        """Full status summary as a JSON-serializable dict."""
        total = len(self.servers)
        enabled = sum(1 for s in self.servers.values() if s.enabled)
        ready = sum(1 for s in self.servers.values() if self.server_ready(s.name))

        server_details = {}
        for name, srv in self.servers.items():
            env_check = self.check_env(srv)
            server_details[name] = {
                "enabled": srv.enabled,
                "ready": self.server_ready(name),
                "command": srv.command,
                "description": srv.description,
                "env_ok": all(env_check.values()) if env_check else True,
                "missing_env": [k for k, v in env_check.items() if not v],
                "skills": srv.skills,
            }

        return {
            "config_file": str(self.mcp_config_path),
            "skill_mapping_file": str(self.skill_mapping_path),
            "total_servers": total,
            "enabled_servers": enabled,
            "disabled_servers": total - enabled,
            "ready_servers": ready,
            "total_skills_mapped": len(self.skill_mcp),
            "servers": server_details,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

HEADER = """
NXT MCP Manager v3.8.0
"""

def _ok(text: str) -> str:
    return f"  [OK]  {text}"

def _fail(text: str) -> str:
    return f"  [!!]  {text}"

def _info(text: str) -> str:
    return f"  [--]  {text}"


def cmd_status(mgr: MCPManager) -> None:
    """Show overall MCP status."""
    st = mgr.get_status()
    print(HEADER)
    print(f"  Config:          {st['config_file']}")
    print(f"  Skill mapping:   {st['skill_mapping_file']}")
    print(f"  Total servers:   {st['total_servers']}")
    print(f"  Enabled:         {st['enabled_servers']}")
    print(f"  Disabled:        {st['disabled_servers']}")
    print(f"  Ready (env ok):  {st['ready_servers']}")
    print(f"  Skills mapped:   {st['total_skills_mapped']}")
    print()

    # Per-server summary
    for name, info in st["servers"].items():
        if info["ready"]:
            tag = _ok(name)
        elif info["enabled"]:
            tag = _fail(f"{name}  (missing env: {', '.join(info['missing_env'])})" if info["missing_env"] else name)
        else:
            tag = _info(f"{name}  (disabled)")
        print(tag)
    print()


def cmd_list(mgr: MCPManager, only_enabled: bool = False) -> None:
    """List all MCP servers."""
    servers = mgr.list_servers(only_enabled=only_enabled)
    label = "enabled " if only_enabled else ""
    print(f"\nMCP Servers - {len(servers)} {label}configured\n")

    for srv in servers:
        status_tag = "enabled" if srv.enabled else "disabled"
        ready_tag = "ready" if mgr.server_ready(srv.name) else "not ready"
        print(f"  {srv.name}")
        print(f"    Status:  {status_tag} | {ready_tag}")
        print(f"    Command: {srv.command} {' '.join(srv.args[:3])}{'...' if len(srv.args) > 3 else ''}")
        if srv.description:
            print(f"    Desc:    {srv.description}")
        if srv.required_env_vars:
            print(f"    Env:     {', '.join(srv.required_env_vars)}")
        if srv.skills:
            print(f"    Skills:  {', '.join(srv.skills)}")
        print()


def cmd_check(mgr: MCPManager, server_name: Optional[str] = None) -> None:
    """Validate env vars for servers."""
    print(f"\nEnvironment variable check\n")

    if server_name:
        srv = mgr.get_server(server_name)
        if srv is None:
            print(f"  Server '{server_name}' not found in .claude/mcp.json")
            return
        _print_env_check(mgr, srv)
    else:
        results = mgr.check_all_env()
        if not results:
            print("  All servers have no env requirements or none are configured.")
            return
        for name in sorted(results):
            srv = mgr.get_server(name)
            if srv:
                _print_env_check(mgr, srv)
    print()


def _print_env_check(mgr: MCPManager, srv: MCPServer) -> None:
    env_results = mgr.check_env(srv)
    if not env_results:
        print(f"  {srv.name}: no env vars required")
        return
    all_ok = all(env_results.values())
    header = _ok(srv.name) if all_ok else _fail(srv.name)
    print(header)
    for var, is_set in env_results.items():
        marker = "SET" if is_set else "MISSING"
        print(f"        {var}: {marker}")


def cmd_skills(mgr: MCPManager) -> None:
    """Show skill-to-MCP mapping."""
    if not mgr.skill_mcp:
        print("\n  No skill-MCP mapping found. Ensure .nxt/skill-mcp-mapping.yaml exists.\n")
        return

    print(f"\nSkill -> MCP mapping ({len(mgr.skill_mcp)} skills)\n")
    for skill in sorted(mgr.skill_mcp):
        servers = mgr.skill_mcp[skill]
        if not servers:
            print(f"  {skill:25s}  (no MCP required)")
        else:
            ready_tags = []
            for s in servers:
                ok = mgr.server_ready(s)
                ready_tags.append(f"{s} [{'OK' if ok else '!!'}]")
            print(f"  {skill:25s}  {', '.join(ready_tags)}")

    print(f"\nMCP -> Skills (reverse mapping)\n")
    for server_name in sorted(mgr.mcp_skills):
        skills_list = mgr.mcp_skills[server_name]
        ready = mgr.server_ready(server_name)
        tag = "OK" if ready else "!!"
        print(f"  {server_name} [{tag}]:  {', '.join(skills_list)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NXT MCP Manager v3.8.0 - Manage MCP server configuration",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show MCP status overview")

    list_p = sub.add_parser("list", help="List all MCP servers")
    list_p.add_argument("--enabled", action="store_true", help="Only enabled servers")

    check_p = sub.add_parser("check", help="Validate env vars for MCP servers")
    check_p.add_argument("server", nargs="?", default=None, help="Server name (omit for all)")

    sub.add_parser("skills", help="Show skill-to-MCP mapping and readiness")

    # JSON output for programmatic use
    sub.add_parser("json", help="Dump full status as JSON")

    args = parser.parse_args()

    mgr = MCPManager()

    if args.command == "status":
        cmd_status(mgr)
    elif args.command == "list":
        cmd_list(mgr, only_enabled=args.enabled)
    elif args.command == "check":
        cmd_check(mgr, server_name=args.server)
    elif args.command == "skills":
        cmd_skills(mgr)
    elif args.command == "json":
        print(json.dumps(mgr.get_status(), indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
