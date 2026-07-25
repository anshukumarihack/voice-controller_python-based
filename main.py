#!/usr/bin/env python3
"""
Offline Voice Command Desktop Assistant
Uses Vosk ASR for speech recognition + PyAutoGUI for automation
"""

import argparse
import sys
import time
from assistant import VoiceAssistant


def main():
    parser = argparse.ArgumentParser(description="Offline Voice Command Desktop Assistant")
    parser.add_argument(
        "--tray",
        action="store_true",
        help="Launch the system tray UI for start/stop listening, stats, and quit.",
    )
    args = parser.parse_args()
    print("=" * 60)
    print("  Offline Voice Command Desktop Assistant")
    print("  Powered by Vosk ASR + PyAutoGUI")
    print("=" * 60)

    assistant = VoiceAssistant()

    try:
        if args.tray:
            from ui.tray_app import AssistantTrayApp

            tray_app = AssistantTrayApp(assistant)
            tray_app.run()
        else:
            assistant.start()
            print("[*] Assistant running! Say: hey assistant")
            print("[*] Press Ctrl+C to quit.")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down assistant...")
        assistant.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()