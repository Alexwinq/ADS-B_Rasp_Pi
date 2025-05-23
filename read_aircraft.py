import subprocess

# Full path to the dump1090-fa binary
DUMP1090_PATH = "/usr/bin/dump1090-fa"

# Command to run with interactive and net options
command = [DUMP1090_PATH, "--interactive", "--net"]

try:
    print("Starting dump1090-fa in interactive mode...")
    subprocess.run(command, check=True)
except FileNotFoundError:
    print("dump1090-fa not found at the specified path.")
except subprocess.CalledProcessError as e:
    print(f"dump1090-fa exited with error code: {e.returncode}")
except KeyboardInterrupt:
    print("\nStopped by user.")
