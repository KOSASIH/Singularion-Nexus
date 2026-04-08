"""Tests for resilience patterns."""
import pytest
import asyncio
from src.core.resilience import CircuitBreaker, CircuitBreakerOpenError, TokenBucketRateLimiter, CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_normal():
    cb = CircuitBreaker(name="test", failure_threshold=3)
    async def ok():
        return "ok"
    result = await cb.call(ok)
    assert result == "ok"
    assert cb.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    cb = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout=0.1)
    async def fail():
        raise ValueError("fail")
    for _ in range(2):
        with pytest.raises(ValueError):
            await cb.call(fail)
    assert cb.state == CircuitState.OPEN
    with pytest.raises(CircuitBreakerOpenError):
        await cb.call(fail)

@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    cb = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout=0.1)
    async def fail():
        raise ValueError()
    for _ in range(2):
        with pytest.raises(ValueError):
            await cb.call(fail)
    await asyncio.sleep(0.15)
    assert cb.state == CircuitState.HALF_OPEN

@pytest.mark.asyncio
async def test_rate_limiter():
    rl = TokenBucketRateLimiter(rate=100, capacity=5)
    results = [await rl.acquire() for _ in range(5)]
    assert all(results)
    assert await rl.acquire() is False
