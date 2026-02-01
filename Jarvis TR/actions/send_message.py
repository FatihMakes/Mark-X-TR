import time
import pyautogui
from tts import edge_speak
import pyperclip

REQUIRED_PARAMS = ["receiver", "message_text", "platform"]

def send_message(parameters: dict, response: str | None = None, player=None, session_memory=None) -> bool:
    """
    Windows uygulaması aracılığıyla mesaj gönderme sistemi (WhatsApp, Telegram, vb.)

    Çoklu adım desteği:
    - Eksik bir parametre varsa sorarak devam eder.

    Beklenen parametreler:
        - receiver (str)
        - message_text (str)
        - platform (str, Varsayılan: "WhatsApp")
    """

    if session_memory is None:
        msg = "Efendim, geçici hafıza hatası oluştu. İşlem yapılamıyor."
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False


    if parameters:
        session_memory.update_parameters(parameters)


    for param in REQUIRED_PARAMS:
        value = session_memory.get_parameter(param)
        if not value:

            session_memory.set_current_question(param)
            question_text = ""

            if param == "receiver":
                question_text = "Efendim, mesajı kime göndereyim?"
            elif param == "message_text":
                question_text = "Efendim, ne mesaj göndereyim?"
            elif param == "platform":
                question_text = "Efendim, hangi platformu kullanayım? (WhatsApp, Telegram, vb.)"
            else:
                question_text = f"Efendim, lütfen {param} bilgisini belirtin."

            if player:
                player.write_log(f"AI: {question_text}")
            edge_speak(question_text, player)
            return False  


    receiver = session_memory.get_parameter("receiver").strip()
    platform = session_memory.get_parameter("platform").strip() or "WhatsApp"
    message_text = session_memory.get_parameter("message_text").strip()

    if response:
        if player:
            player.write_log(response)
        edge_speak(response, player)

    try:
        pyautogui.PAUSE = 0.1

        pyautogui.press("win")
        time.sleep(0.3)
        pyautogui.write(platform, interval=0.03)
        pyautogui.press("enter")
        time.sleep(0.6)

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        pyautogui.write(receiver, interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.2)

        pyperclip.copy(message_text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")

        session_memory.clear_current_question()
        session_memory.clear_pending_intent()
        session_memory.update_parameters({})

        time.sleep(1)

        return True

    except Exception as e:
        msg = f"Efendim, mesajı gönderirken bir sorun oluştu. Hata: ({e})"
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False
