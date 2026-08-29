def write_file(path, content):
    try:
        with open(path, 'w') as f:   # open in write mode, creates file if not exists
            f.write(content)          # write content to file
        return {"success": True, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e)}
