# app_materials/validators.py

from urllib.parse import urlparse

from rest_framework import serializers

WHITE_LIST_DOMAINS = (
    "youtube.com",
    "www.youtube.com",
    "rutube.ru",
    "www.rutube.ru",
)


def _allowed_domains_human() -> str:
    """
    Превращает список доменов в строку для сообщения.
    """
    return ", ".join(WHITE_LIST_DOMAINS)


def validate_video_url(value: str) -> str:
    """
    Разрешаем только ссылки на разрешенные домены.
    Остальные домены считаем сторонними ресурсами.
    """
    parsed = urlparse(value)

    # Если нет схемы/доменной части - сразу ошибка.
    if not parsed.netloc:
        # Если нет домена или URL неполный.
        raise serializers.ValidationError(
            f"Некорректная ссылка на видео: укажите полный URL на один из разрешённых доменов "
            f"({_allowed_domains_human()}), например https://{WHITE_LIST_DOMAINS[0]}/..."
        )

    domain = parsed.netloc.lower()

    # Если адреса нет в разрешительном списке - сразу ошибка.
    if domain not in WHITE_LIST_DOMAINS:
        raise serializers.ValidationError(
            f"Можно прикреплять только ссылки на видео с доменов: {_allowed_domains_human()}. "
            f"Ссылки на другие сайты и платформы запрещены."
        )

    return value
