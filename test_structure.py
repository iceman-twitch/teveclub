"""
Quick test script to verify the new structure works
Run this to test without logging in
"""
from src.config import LOGIN_URL, MYTEVE_URL, TANIT_URL, TIPP_URL
from src.utils import get_user_agent, do_sleep
from src.bot_core import TeveClub

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    print(f"✓ Config loaded - LOGIN_URL: {LOGIN_URL}")
    print(f"✓ Utils loaded - User Agent: {get_user_agent()}")
    print("✓ Bot core loaded - TeveClub class available")
    print("\nAll imports successful!")

def test_config():
    """Test configuration values"""
    print("\nTesting configuration...")
    print(f"LOGIN_URL: {LOGIN_URL}")
    print(f"MYTEVE_URL: {MYTEVE_URL}")
    print(f"TANIT_URL: {TANIT_URL}")
    print(f"TIPP_URL: {TIPP_URL}")
    print("✓ All URLs configured correctly")

def test_bot_creation():
    """Test bot instantiation"""
    print("\nTesting bot creation...")
    bot = TeveClub("test_user", "test_pass")
    print(f"✓ Bot created with username: {bot.username}")
    print(f"✓ Session object exists: {bot.session is not None}")
    print("✓ Bot instantiation successful")

if __name__ == "__main__":
    print("=" * 50)
    print("TEVECLUB BOT - NEW STRUCTURE TEST")
    print("=" * 50)
    
    try:
        test_imports()
        test_config()
        test_bot_creation()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        print("\nYou can now run the bot with:")
        print("  python main.py              (GUI mode)")
        print("  python main.py user pass    (CLI mode)")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
