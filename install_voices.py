#!/usr/bin/env python3
"""
GreenTech - Native Voice Installation Helper

This script helps install and verify Windows native voices for:
- Telugu (తెలుగు)
- Hindi (हिन्दी) 
- Tamil (தமிழ்)
- Kannada (ಕನ್ನಡ)
"""

import subprocess
import sys
import time
from services.tts_service import get_tts_status, list_installed_voices

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📋 Step {step}: {description}")
    print("-" * 50)

def check_current_voices():
    """Check what voices are currently available"""
    print_header("CURRENT VOICE STATUS")
    
    languages = ["English", "Telugu", "Hindi", "Tamil", "Kannada"]
    
    for lang in languages:
        status = get_tts_status(lang)
        if status["available"]:
            print(f"✅ {lang}: {status['voice_name']}")
        else:
            print(f"❌ {lang}: Not available")
    
    print(f"\n🔊 Total installed voices: {len(list_installed_voices())}")
    all_voices = list_installed_voices()
    for i, voice in enumerate(all_voices, 1):
        print(f"   {i}. {voice}")

def open_windows_settings():
    """Open Windows Language Settings"""
    print_header("OPENING WINDOWS SETTINGS")
    
    try:
        # Try to open Language settings directly
        subprocess.run(["start", "ms-settings:regionlanguage"], shell=True)
        print("✅ Opening Windows Language Settings...")
        print("   If this doesn't work, manually go to:")
        print("   Settings → Time & Language → Language & Region")
    except Exception as e:
        print(f"❌ Could not open settings automatically: {e}")
        print("\n📱 Manual Instructions:")
        print("   1. Press Windows + I")
        print("   2. Go to Time & Language → Language & Region")
        print("   3. Click 'Add a language'")

def show_installation_steps():
    """Show detailed installation instructions"""
    print_header("INSTALLATION INSTRUCTIONS")
    
    languages = [
        ("Telugu", "తెలుగు", "te-IN"),
        ("Hindi", "हिन्दी", "hi-IN"), 
        ("Tamil", "தமிழ்", "ta-IN"),
        ("Kannada", "ಕನ್ನಡ", "kn-IN")
    ]
    
    print("For EACH language below, follow these steps in Windows Settings:")
    print()
    
    for i, (eng_name, native_name, code) in enumerate(languages, 1):
        print(f"{i}. {eng_name} ({native_name}):")
        print(f"   • Search for '{eng_name}' or '{native_name}'")
        print(f"   • Select '{eng_name} (India)' - {code}")
        print(f"   • Click 'Next' → 'Install'")
        print(f"   • ⚠️ IMPORTANT: Also click 'Language options' → Download:")
        print(f"     - ✅ Speech recognition")
        print(f"     - ✅ Text-to-speech") 
        print(f"     - ✅ Language pack")
        print()
    
    print("⏱️  Each language takes 10-20 minutes to download and install")
    print("💾 Total download size: ~600MB-1GB")
    print("🌐 Ensure stable internet connection")

def wait_for_installation():
    """Interactive waiting for user to complete installation"""
    print_header("WAITING FOR INSTALLATION")
    
    print("Complete the installation in Windows Settings, then:")
    print("1. Install all 4 languages (Telugu, Hindi, Tamil, Kannada)")
    print("2. Download Speech recognition AND Text-to-speech for each")
    print("3. Wait for all downloads to complete")
    print("4. Come back here and press Enter")
    
    input("\n⏳ Press Enter when installation is complete...")

def verify_installation():
    """Verify that voices were installed successfully"""
    print_header("VERIFICATION")
    
    print("🔄 Checking for newly installed voices...")
    
    # Check each language
    languages = ["Telugu", "Hindi", "Tamil", "Kannada"]
    installed_count = 0
    
    for lang in languages:
        status = get_tts_status(lang)
        if status["available"]:
            print(f"✅ {lang}: {status['voice_name']}")
            installed_count += 1
        else:
            print(f"❌ {lang}: Still not available")
            print(f"   💡 {status['install_guide']}")
    
    print(f"\n📊 Results: {installed_count}/4 languages successfully installed")
    
    if installed_count == 4:
        print("🎉 ALL NATIVE VOICES INSTALLED SUCCESSFULLY!")
        print("   GreenTech will now use native voices for Read Aloud")
    elif installed_count > 0:
        print("🔄 PARTIAL SUCCESS - Some voices installed")
        print("   Installed voices will work natively")
        print("   Missing voices will use English fallback")
    else:
        print("⚠️  NO NATIVE VOICES DETECTED")
        print("   Possible issues:")
        print("   • Installation not complete")
        print("   • Need to restart Windows")
        print("   • Need to restart GreenTech")

def test_speech():
    """Test speech output for installed voices"""
    print_header("SPEECH TEST")
    
    languages = ["Telugu", "Hindi", "Tamil", "Kannada"]
    test_phrases = {
        "Telugu": "నమస్కారం, ఇది తెలుగు వాయిస్ టెస్ట్",
        "Hindi": "नमस्ते, यह हिन्दी वॉयस टेस्ट है", 
        "Tamil": "வணக்கம், இது தமிழ் குரல் சோதனை",
        "Kannada": "ನಮಸ್ಕಾರ, ಇದು ಕನ್ನಡ ಧ್ವನಿ ಪರೀಕ್ಷೆ"
    }
    
    for lang in languages:
        status = get_tts_status(lang)
        if status["available"]:
            print(f"🔊 Testing {lang} voice...")
            phrase = test_phrases[lang]
            
            # Test speech
            from services.tts_service import speak
            result = speak(phrase, lang)
            
            if result["success"]:
                print(f"   ✅ {lang} speech test successful!")
                print(f"   🎤 Voice: {result['voice']}")
            else:
                print(f"   ❌ {lang} speech test failed: {result.get('error')}")
            
            time.sleep(2)  # Wait between tests

def restart_greentech():
    """Instructions for restarting GreenTech"""
    print_header("RESTART GREENTECH")
    
    print("To use the new native voices in GreenTech:")
    print("1. ⏹️  Stop the current GreenTech session (Ctrl+C in terminal)")
    print("2. 🔄 Restart GreenTech:")
    print("   streamlit run main.py")
    print("3. 🧪 Test Read Aloud with Telugu/Hindi/Tamil/Kannada")
    print("4. ✅ Should now use native voices instead of English fallback")

def main():
    """Main installation workflow"""
    print_header("GREENTECH NATIVE VOICE INSTALLER")
    print("This tool helps install Telugu, Hindi, Tamil, Kannada voices for Windows TTS")
    
    # Step 1: Check current status
    print_step(1, "Current Voice Status")
    check_current_voices()
    
    # Step 2: Open Windows Settings
    print_step(2, "Open Windows Language Settings")
    open_windows_settings()
    
    # Step 3: Show installation instructions
    print_step(3, "Installation Instructions")
    show_installation_steps()
    
    # Step 4: Wait for user to complete installation
    print_step(4, "Complete Installation")
    wait_for_installation()
    
    # Step 5: Verify installation
    print_step(5, "Verify Installation")
    verify_installation()
    
    # Step 6: Test speech (optional)
    print_step(6, "Test Speech Output")
    test_choice = input("🔊 Test native voice speech? (y/n): ").lower()
    if test_choice in ['y', 'yes']:
        test_speech()
    
    # Step 7: Restart instructions
    print_step(7, "Restart GreenTech")
    restart_greentech()
    
    print_header("INSTALLATION COMPLETE")
    print("🎉 Native voice installation process finished!")
    print("📱 Use GreenTech with Telugu/Hindi/Tamil/Kannada for best experience")

if __name__ == "__main__":
    main()