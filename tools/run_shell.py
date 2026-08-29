import subprocess

def run_shell(command, timeout=10):
  result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=timeout
  )

  return {
    "stdout": result.stdout,
    "stderr": result.stderr,
    "exit_code": result.returncode
  }

