import os

def list_files(directory):
    try:
        items = os.listdir(directory)  # returns list of all files and folders in directory
        return {"success": True, "files": items}
    except FileNotFoundError:
        return {"success": False, "error": f"Directory not found: {directory}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
