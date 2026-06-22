import os
import shutil
from app.config import settings

class StorageService:
    def __init__(self):
        self.storage_dir = settings.STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> str:
        """Saves a file to local storage and returns its absolute path."""
        # Clean the filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        dest_path = os.path.join(self.storage_dir, safe_filename)
        
        # Write content
        with open(dest_path, "wb") as f:
            f.write(content)
            
        return dest_path

    def delete_file(self, storage_path: str) -> bool:
        """Deletes a file from storage if it exists."""
        try:
            if os.path.exists(storage_path):
                os.remove(storage_path)
                return True
        except Exception as e:
            print(f"Error deleting file from storage: {e}")
        return False

storage_service = StorageService()
