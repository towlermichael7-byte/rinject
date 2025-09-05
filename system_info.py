import sys
import os
import platform
import subprocess

def get_system_info():
    print("=== System Information ===")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Check file system access
    print("\n=== File System Access ===")
    test_file = "test_write.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test write operation")
        print(f"Successfully wrote to {test_file}")
        if os.path.exists(test_file):
            print(f"File exists: {os.path.abspath(test_file)}")
            os.remove(test_file)
            print("Test file cleaned up")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
    # List current directory contents
    print("\n=== Directory Contents ===")
    try:
        files = os.listdir('.')
        for f in files:
            print(f"- {f}")
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    # Check Python path
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")

if __name__ == "__main__":
    get_system_info()
