
"""Skeleton runner that would read a manifest and call tools in order."""

def run_manifest(path_to_manifest: str):
    # 1) Load JSON
    # 2) For each step in pipeline, resolve args (including $prev.* references)
    # 3) Call tool.apply(), then tool.verify()
    # 4) Collect outputs and pass forward
    pass
