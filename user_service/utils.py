import os
import subprocess

def execute_cmd(cmd, wait=False):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        start_new_session=True
    )
    if wait:
        stdout, stderr = proc.communicate()
        if stdout:
            print(f"[STDOUT] {stdout.decode().strip()}")
        if stderr:
            print(f"[STDERR] {stderr.decode().strip()}")

