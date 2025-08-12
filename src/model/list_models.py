import subprocess
def get_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            models = [line.split()[0].strip() for line in lines[1:] if line]
            return sorted(set(models))
    except:
        pass
    return []