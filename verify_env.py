import sys
import os

def main():
    print("=== Environment Verification ===")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Test imports
    print("\n=== Testing Imports ===")
    try:
        import docx
        print(f"python-docx: {docx.__version__}")
    except ImportError as e:
        print(f"Error importing python-docx: {e}")
    
    # Test document_processor
    try:
        from document_processor import BulletFormatter
        print("Successfully imported BulletFormatter")
        
        # Test creating an instance
        formatter = BulletFormatter()
        print("Successfully created BulletFormatter instance")
        
        # Test bullet detection
        test_text = "• Test bullet"
        is_bullet = formatter._is_bullet_point(test_text)
        print(f"Bullet detection test: {test_text!r} -> {'Bullet' if is_bullet else 'Not a bullet'}")
        
    except Exception as e:
        print(f"Error with document_processor: {e}")
        import traceback
        traceback.print_exc()
    
    # Test file operations
    print("\n=== Testing File Operations ===")
    test_file = "test_file.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test content")
        print(f"Successfully wrote to {test_file}")
        os.remove(test_file)
        print(f"Successfully removed {test_file}")
    except Exception as e:
        print(f"File operation test failed: {e}")

if __name__ == "__main__":
    main()
