import json

def load_config(path):
    """
    Belirtilen JSON dosyasını yükler
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON dosyası bulunamadı: {path}")
