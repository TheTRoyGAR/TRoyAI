"""A directory-listing tool that won't blow the context budget.

crewai_tools' DirectoryReadTool does a raw, unfiltered os.walk() over
whatever directory it's pointed at — no exclusion list, no size cap. Pointed
at a real project root that includes node_modules/.next/.git, a single call
can return millions of tokens in one shot (this happened for real on
2026-08-31: TRoyGO's CTO audit tried to send a 2.9M-token prompt against a
200K-token API limit and crashed outright). Task-prompt instructions like
"don't read node_modules" don't help — the tool call itself already returns
the full listing before the agent gets a chance to follow that instruction.

This tool walks the tree itself, prunes known junk directories before
descending into them (so they're never even stat'd, let alone listed), and
hard-caps the number of paths returned so a real answer always comes back
instead of a hard API failure.

Ported from TRoyMAR/TRoyMEDIA/TRoyGO, 2026-09-28 — TRoyAI was the one
company in the group without any of this.
"""
import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_EXCLUDED_DIRS = {
    "node_modules", ".next", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", "out", ".turbo", "coverage", ".pytest_cache",
    ".mypy_cache", "site-packages", ".cache",
}
_MAX_PATHS = 500


class SafeDirectoryReadInput(BaseModel):
    directory: str = Field(
        default="",
        description="Optional subdirectory (relative to the sandboxed root) to list instead of the whole root.",
    )


class SafeDirectoryReadTool(BaseTool):
    name: str = "list_dir"
    description: str = (
        "List real file paths under a directory, skipping node_modules/.next/.git/"
        "__pycache__/build output and other generated/dependency directories "
        "automatically. Capped at 500 paths so it always returns instead of "
        "failing on a huge tree. Pass a subdirectory to narrow the listing."
    )
    args_schema: type[BaseModel] = SafeDirectoryReadInput
    root: str = ""

    def _run(self, directory: str = "") -> str:
        start = os.path.join(self.root, directory) if directory else self.root
        start = os.path.normpath(start)
        if not start.startswith(os.path.normpath(self.root)):
            return f"Refused: '{directory}' resolves outside the sandboxed root."
        if not os.path.isdir(start):
            return f"Not a directory: {start}"

        paths: list[str] = []
        truncated = False
        for dirpath, dirnames, filenames in os.walk(start):
            dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIRS and not d.startswith(".")]
            for filename in filenames:
                if len(paths) >= _MAX_PATHS:
                    truncated = True
                    break
                full = os.path.join(dirpath, filename)
                paths.append(os.path.relpath(full, self.root))
            if truncated:
                break

        header = f"File paths under '{directory or '.'}' (relative to project root):\n"
        body = "\n".join(f"- {p}" for p in paths)
        footer = (
            f"\n\n[Truncated at {_MAX_PATHS} paths — narrow with the `directory` argument for more.]"
            if truncated else ""
        )
        return header + body + footer
