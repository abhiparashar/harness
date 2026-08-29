def read_file(path):
    try:
        with open(path, 'r') as f:
            return {"content": f.read(), "error": None}
    except Exception as e:
        return {"content": None, "error": str(e)}
