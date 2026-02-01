import re
from serpapi import GoogleSearch
from tts import edge_speak


MAX_SNIPPETS = 3
MIN_SENTENCE_LENGTH = 30


def clean(text: str) -> str:
    """Metni temizle: fazla boşlukları, ..., parantezleri kaldır."""
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.\.\.+", ".", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    return text.strip()


def split_sentences(text: str):
    """Metni cümlelere böl ve çok kısa ya da eksik olanları alma."""
    sentences = re.split(r"(?<=[.!?])\s+", text)

    valid_sentences = []
    buffer = ""

    for s in sentences:
        s = clean(s)
        if not s:
            continue

        last_word = s.split()[-1].lower()
        if last_word in [
            "-nun", "içinde", "da", "üstünde", "tarafından",
            "sonra", "önce", "ile", "için", "-a"
        ]:
            buffer += s + " "
            continue

        if buffer:
            s = buffer + s
            buffer = ""

        if len(s) >= MIN_SENTENCE_LENGTH:
            valid_sentences.append(s)

    return valid_sentences


def is_noise(text: str) -> bool:
    """Bir cümlenin gürültü / alakasız olup olmadığını kontrol et."""
    t = text.lower()

    noise_keywords = [
        "devamını oku",
        "daha fazla öğren",
        "buraya tıkla",
        "infografik",
        "google trendleri",
        "yılın aramaları",
        "en çok aranan",
        "ilk 100",
        "abone ol",
        "bunu paylaş",
        "reklam",
        "reklam:"
    ]

    return any(word in t for word in noise_keywords)


def select_best_sentence(snippets):
    """En fazla MAX_SNIPPETS birleştir ve tek, tutarlı bir cümle döndür."""
    final_text = ""
    count = 0

    for snippet in snippets:
        if not snippet or is_noise(snippet):
            continue

        sentences = split_sentences(snippet)

        for s in sentences:
            if is_noise(s):
                continue

            final_text = f"{final_text} {s}".strip()
            count += 1

            if count >= MAX_SNIPPETS:
                return final_text

    return final_text if final_text else None


def serpapi_answer(query: str, api_key: str) -> str:
    """Arama yap ve tek, tutarlı bir cümle döndür."""
    params = {
        "q": query,
        "engine": "google",
        "hl": "tr",
        "gl": "tr",
        "num": 3,
        "api_key": api_key
    }

    try:
        data = GoogleSearch(params).get_dict()
    except Exception:
        return "Efendim, web araması başarısız oldu."

    organic = data.get("organic_results", [])
    if not organic:
        return "Efendim, alakalı bir bilgi bulamadım."

    snippets = [
        r.get("snippet", "")
        for r in organic
        if r.get("snippet")
    ]

    answer = select_best_sentence(snippets)

    if not answer:
        return "Efendim, internette bilgi buldum ancak net bir şekilde özetleyemedim."

    return answer


def web_search(
    parameters: dict,
    player=None,
    session_memory=None,
    api_key: str = ""
):
    """
    Ana web araması:
    - 1 adet tutarlı cümle döndürür
    - Önceki cevapları eklemez
    - Yarım kalan cümleleri önlemek için birden fazla snippet birleştirir
    """

    query = (parameters or {}).get("query", "").strip()

    if not query:
        msg = "Efendim, arama isteğini anlayamadım."
        if player:
            player.write_log(msg)
        edge_speak(msg)
        return msg

    answer = serpapi_answer(query, api_key)

    if player:
        player.write_log(f"Yapay Zeka: {answer}")

    edge_speak(answer)

    if session_memory:
        session_memory.set_last_search(query, answer)

    return answer
