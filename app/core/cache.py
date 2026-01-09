"""Cache utilitário para taxas de câmbio com fallback em memória."""
import time
from typing import Optional
from redis import Redis, RedisError


class RateCache:
    """Cache simples para taxas de câmbio, com Redis opcional e fallback em memória.

    Parâmetros:
        redis_url (str | None): URL do Redis; se None usa apenas memória local.
        ttl_seconds (int): Tempo de vida do valor em cache, em segundos.

    Retorna:
        RateCache: Instância capaz de armazenar valores numéricos com expiração.
    """

    def __init__(self, redis_url: Optional[str], ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self._memory_cache: dict[str, tuple[float, float]] = {}
        self._redis: Optional[Redis] = None

        if redis_url:
            try:
                self._redis = Redis.from_url(redis_url, decode_responses=True)
                # Testa a conexão de forma leve
                self._redis.ping()
            except RedisError:
                # Se Redis não estiver acessível, segue com cache em memória
                self._redis = None

    def get(self, key: str) -> Optional[float]:
        """Retorna o valor em cache se não expirou."""
        now = time.time()

        if self._redis:
            try:
                val = self._redis.get(key)
                if val is None:
                    return None
                return float(val)
            except RedisError:
                # Fallback silencioso para memória
                pass

        if key not in self._memory_cache:
            return None
        value, expires_at = self._memory_cache[key]
        if now > expires_at:
            self._memory_cache.pop(key, None)
            return None
        return value

    def set(self, key: str, value: float) -> None:
        """Armazena valor com TTL configurado."""
        expires_at = time.time() + self.ttl_seconds

        if self._redis:
            try:
                self._redis.setex(key, self.ttl_seconds, value)
                return
            except RedisError:
                # Fallback silencioso para memória
                pass

        self._memory_cache[key] = (value, expires_at)
