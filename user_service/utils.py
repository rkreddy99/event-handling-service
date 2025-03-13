import os
import subprocess
import asyncio

async def execute_cmd(cmd, wait=False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if wait:
        stdout, stderr = await proc.communicate()
        if stdout:
            print(f"[STDOUT] {stdout.decode().strip()}")
        if stderr:
            print(f"[STDERR] {stderr.decode().strip()}")

