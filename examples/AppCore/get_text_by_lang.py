from pathlib import Path
from tbot223_core import AppCore
import json

if __name__ == "__main__":
    # Define base directory and language directory
    BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"
    LANG_DIR= BASE_DIR / "Languages"

    # Language files are automatically detected and loaded, and even if naming conventions like en or en-GB are mixed, they will be loaded. Note that you must distinguish them carefully.
    # However, for simplicity in this example, only en, es, fr, de, and ko are used. In practice, it is better to use en-GB as the default.
    LANG_FILES={
        "en": {
            "greeting.txt": "Hello!\nWelcome to our application.\nEnjoy your stay!",
            "farewell.txt": "Goodbye!\nThank you for using our application.\nSee you next time!",
        }
        ,"es": {
            "greeting.txt": "¡Hola!\nBienvenido a nuestra aplicación.\n¡Disfruta tu estadía!",
            "farewell.txt": "¡Adiós!\nGracias por usar nuestra aplicación.\n¡Hasta la próxima!",
        }
        ,"fr": {
            "greeting.txt": "Bonjour!\nBienvenue dans notre application.\nProfitez de votre séjour!",
            "farewell.txt": "Au revoir!\nMerci d'utiliser notre application.\nÀ la prochaine!"
        }
        ,"de": {
            "greeting.txt": "Hallo!\nWillkommen zu unserer Anwendung.\nGenießen Sie Ihren Aufenthalt!",
            "farewell.txt": "Auf Wiedersehen!\nDanke, dass Sie unsere Anwendung genutzt haben.\nBis zum nächsten Mal!"
        }
        ,"ko": {
            "greeting.txt": "안녕하세요!\n우리 애플리케이션에 오신 것을 환영합니다.\n즐거운 시간 되세요!",
            "farewell.txt": "안녕히 가세요!\n우리 애플리케이션을 이용해 주셔서 감사합니다.\n다음에 또 뵙겠습니다!"
        }
    }

    # `AppCore` will automatically load language files from the `Languages` directory. *.json files placed in this directory will be detected and loaded.

    # Create language files
    LANG_DIR.mkdir(parents=True, exist_ok=True)

    # Write language files
    for lang_code, files in LANG_FILES.items():
        with open(LANG_DIR / f"{lang_code}.json", "w", encoding="utf-8") as f:
            json.dump(files, f, ensure_ascii=False, indent=4)

    # Initialize AppCore
    ap = AppCore.AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    # Retrieve and print messages in different languages
    for lang in ap._supported_langs:
        greeting = ap.get_text_by_lang("greeting.txt", lang).data
        farewell = ap.get_text_by_lang("farewell.txt", lang).data

        print(f"--- Messages in {lang} ---")
        print(greeting, end="\n --- few time later... --- \n") 
        print(farewell, end="\n--- end of messages ---\n")

    # Clean up created language files
    for lang_code in LANG_FILES.keys():
        lang_file = LANG_DIR / f"{lang_code}.json"
        if lang_file.exists():
            lang_file.unlink()

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")