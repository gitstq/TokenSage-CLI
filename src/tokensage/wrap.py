"""TokenSage Agent Wrapper - Configure AI coding agents to use TokenSage."""

from typing import Optional


def wrap_agent(agent: str, proxy_port: int = 8787) -> dict:
    """Generate configuration for wrapping an AI coding agent with TokenSage.

    Args:
        agent: One of "claude", "codex", "cursor", "aider", "copilot"
        proxy_port: The port TokenSage proxy is running on

    Returns:
        Dict with config info (env vars, config files, instructions)
    """
    configs = {
        "claude": {
            "agent_name": "Claude Code",
            "env_var": "CLAUDE_CODE_OPTS",
            "env_value": f"--proxy http://localhost:{proxy_port}",
            "config_file": "~/.claude/claude_code_config.json",
            "instructions": [
                f"1. Set CLAUDE_CODE_OPTS=--proxy http://localhost:{proxy_port}",
                f"2. Or add to ~/.claude/claude_code_config.json: {{\"proxy\": \"http://localhost:{proxy_port}\"}}",
                f"3. Start proxy: tokensage proxy --port {proxy_port}",
            ],
        },
        "codex": {
            "agent_name": "Codex CLI",
            "env_var": "CODEX_PROXY",
            "env_value": f"http://localhost:{proxy_port}",
            "config_file": "~/.codex/config.json",
            "instructions": [
                f"1. Set CODEX_PROXY=http://localhost:{proxy_port}",
                f"2. Start proxy: tokensage proxy --port {proxy_port}",
            ],
        },
        "cursor": {
            "agent_name": "Cursor",
            "env_var": "CURSOR_AGENT_PROXY",
            "env_value": f"http://localhost:{proxy_port}",
            "config_file": "~/.cursor/config.json",
            "instructions": [
                f"1. Set CURSOR_AGENT_PROXY=http://localhost:{proxy_port}",
                f"2. Or add to ~/.cursor/config.json: {{\"agentProxy\": \"http://localhost:{proxy_port}\"}}",
                f"3. Start proxy: tokensage proxy --port {proxy_port}",
            ],
        },
        "aider": {
            "agent_name": "Aider",
            "env_var": "AIDER_OPENAI_PROXY",
            "env_value": f"http://localhost:{proxy_port}",
            "config_file": None,
            "instructions": [
                f"1. Set AIDER_OPENAI_PROXY=http://localhost:{proxy_port}",
                f"2. Start proxy: tokensage proxy --port {proxy_port}",
            ],
        },
        "copilot": {
            "agent_name": "GitHub Copilot CLI",
            "env_var": "COPILOT_PROXY",
            "env_value": f"http://localhost:{proxy_port}",
            "config_file": None,
            "instructions": [
                f"1. Set COPILOT_PROXY=http://localhost:{proxy_port}",
                f"2. Start proxy: tokensage proxy --port {proxy_port}",
            ],
        },
    }

    return configs.get(agent, {
        "agent_name": agent,
        "instructions": [f"Configure {agent} to use http://localhost:{proxy_port} as proxy"],
    })