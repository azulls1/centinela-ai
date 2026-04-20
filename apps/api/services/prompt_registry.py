"""Prompt versioning and registry for AI features."""
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

class PromptRegistry:
    """Manages versioned prompts for AI features."""

    def __init__(self):
        self._prompts: dict[str, dict] = {}
        self._load_prompts()

    def _load_prompts(self):
        if not PROMPTS_DIR.exists():
            PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

        for file in PROMPTS_DIR.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                self._prompts[data["id"]] = data
            except Exception as e:
                logger.error(f"Failed to load prompt {file}: {e}")

    def get(self, prompt_id: str, version: Optional[str] = None) -> Optional[dict]:
        prompt = self._prompts.get(prompt_id)
        if not prompt:
            return None
        if version and prompt.get("version") != version:
            return None
        return prompt

    def get_text(self, prompt_id: str) -> str:
        prompt = self.get(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        return prompt["template"]

    def register(self, prompt_id: str, template: str, metadata: Optional[dict] = None):
        version_hash = hashlib.sha256(template.encode()).hexdigest()[:8]
        prompt_data = {
            "id": prompt_id,
            "version": version_hash,
            "template": template,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "char_count": len(template),
        }
        self._prompts[prompt_id] = prompt_data

        file_path = PROMPTS_DIR / f"{prompt_id}.json"
        file_path.write_text(json.dumps(prompt_data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Registered prompt '{prompt_id}' v{version_hash}")
        return prompt_data

    def list_all(self) -> list[dict]:
        return [{"id": p["id"], "version": p["version"], "chars": p["char_count"]} for p in self._prompts.values()]

# Singleton
prompt_registry = PromptRegistry()
