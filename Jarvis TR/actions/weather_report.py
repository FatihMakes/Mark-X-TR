import webbrowser
from urllib.parse import quote_plus
from tts import edge_speak


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None
):
    """
    Hava durumu eylemi.
    Google hava durumu aramasını açar ve kısa bir sesli onay verir.
    """

    city = parameters.get("city")
    time = parameters.get("time")
    if not city or not isinstance(city, str):
        msg = "Efendim, hava durumu raporu için şehir bilgisi eksik."
        _speak_and_log(msg, player)
        return msg

    city = city.strip()

    if not time or not isinstance(time, str):
        time = "bugün"
    else:
        time = time.strip()

    search_query = f"{city} hava durumu {time}"
    encoded_query = quote_plus(search_query)
    url = f"https://www.google.com/search?q={encoded_query}"

    try:
        webbrowser.open(url)
    except Exception:
        msg = "Efendim, hava durumu için tarayıcıyı açamadım."
        _speak_and_log(msg, player)
        return msg

    msg = f"{city} için {time} hava durumunu gösteriyorum, efendim."
    _speak_and_log(msg, player)

    if session_memory:
        try:
            session_memory.set_last_search(
                query=search_query,
                response=msg
            )
        except Exception:
            pass  

    return msg


def _speak_and_log(message: str, player=None):
    """Yardımcı: güvenli şekilde loglama + TTS"""
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass

    try:
        edge_speak(message)
    except Exception:
        pass
