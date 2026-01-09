"""Serviço de câmbio USD/BRL com fallback e cache."""
from typing import Optional
import httpx
from app.core.cache import RateCache
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("app.services.exchange")


def _fetch_from_awesomeapi() -> float:
    """Busca cotação USD-BRL na AwesomeAPI (retorna BRL por USD)."""
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    resp = httpx.get(url, timeout=5.0)
    resp.raise_for_status()
    data = resp.json()
    bid = data.get("USDBRL", {}).get("bid")
    if not bid:
        raise ValueError("Cotação não encontrada na AwesomeAPI")
    return float(bid)


def _fetch_from_frankfurter() -> float:
    """Busca cotação USD-BRL na Frankfurter (retorna BRL por USD)."""
    url = "https://api.frankfurter.app/latest?from=USD&to=BRL"
    resp = httpx.get(url, timeout=5.0)
    resp.raise_for_status()
    data = resp.json()
    rate = data.get("rates", {}).get("BRL")
    if rate is None:
        raise ValueError("Cotação não encontrada na Frankfurter")
    return float(rate)


def get_usd_brl_rate(cache: Optional[RateCache] = None) -> float:
    """Obtém a taxa USD→BRL com cache e fallback.

    Retorna BRL por 1 USD. Se `EXCHANGE_RATE_FIXED` estiver definido, usa-o diretamente
    (útil para testes offline).
    """
    # Fixed rate para testes
    if settings.EXCHANGE_RATE_FIXED is not None:
        return float(settings.EXCHANGE_RATE_FIXED)

    cache = cache or RateCache(settings.REDIS_URL, settings.EXCHANGE_RATE_TTL)
    cached = cache.get("usd_brl")
    if cached:
        return cached

    # Tenta AwesomeAPI primeiro, fallback Frankfurter
    try:
        rate = _fetch_from_awesomeapi()
        cache.set("usd_brl", rate)
        return rate
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha na AwesomeAPI, tentando fallback", extra={"error": str(exc)})

    rate = _fetch_from_frankfurter()
    cache.set("usd_brl", rate)
    return rate
