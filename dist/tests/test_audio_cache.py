import os
import asyncio
import pytest
from pathlib import Path
from ..utils.audio_cache import AudioCache

@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory"""
    cache_path = tmp_path / "test_cache"
    cache_path.mkdir()
    return str(cache_path)

@pytest.fixture
def audio_cache(cache_dir):
    """Create an AudioCache instance with test settings"""
    return AudioCache(
        cache_dir=cache_dir,
        max_size_mb=10,
        max_age_days=1
    )

@pytest.mark.asyncio
async def test_cache_audio(audio_cache):
    """Test caching audio data"""
    # Test data
    text = "Hello, world!"
    engine = "test_engine"
    voice_id = "test_voice"
    settings = {"rate": 1.0, "pitch": 1.0}
    audio_data = b"test audio data"
    
    # Cache audio
    cache_key = await audio_cache.cache_audio(
        text=text,
        engine=engine,
        voice_id=voice_id,
        settings=settings,
        audio_data=audio_data
    )
    
    # Verify cache entry
    assert cache_key in audio_cache.cache_index
    assert audio_cache._get_cache_path(cache_key).exists()
    
    # Verify cached data
    cached_audio = await audio_cache.get_cached_audio(
        text=text,
        engine=engine,
        voice_id=voice_id,
        settings=settings
    )
    assert cached_audio == audio_data

@pytest.mark.asyncio
async def test_cache_expiration(audio_cache):
    """Test cache entry expiration"""
    # Cache test data
    cache_key = await audio_cache.cache_audio(
        text="test",
        engine="test",
        voice_id="test",
        settings={},
        audio_data=b"test"
    )
    
    # Modify creation time to simulate old entry
    audio_cache.cache_index[cache_key]["created_at"] = 0
    audio_cache._save_index()
    
    # Verify entry is expired
    cached_audio = await audio_cache.get_cached_audio(
        text="test",
        engine="test",
        voice_id="test",
        settings={}
    )
    assert cached_audio is None
    assert cache_key not in audio_cache.cache_index

@pytest.mark.asyncio
async def test_cache_size_limit(audio_cache):
    """Test cache size limit enforcement"""
    # Cache large data
    large_data = b"x" * (audio_cache.max_size_bytes + 1)
    await audio_cache.cache_audio(
        text="large",
        engine="test",
        voice_id="test",
        settings={},
        audio_data=large_data
    )
    
    # Verify cache size is within limits
    stats = audio_cache.get_cache_stats()
    assert stats["total_size_bytes"] <= audio_cache.max_size_bytes

def test_cache_stats(audio_cache):
    """Test cache statistics"""
    stats = audio_cache.get_cache_stats()
    assert "total_size_bytes" in stats
    assert "entry_count" in stats
    assert "oldest_entry_age_seconds" in stats
    assert "max_size_bytes" in stats
    assert "max_age_seconds" in stats

@pytest.mark.asyncio
async def test_clear_cache(audio_cache):
    """Test clearing the cache"""
    # Add some test data
    await audio_cache.cache_audio(
        text="test1",
        engine="test",
        voice_id="test",
        settings={},
        audio_data=b"test1"
    )
    await audio_cache.cache_audio(
        text="test2",
        engine="test",
        voice_id="test",
        settings={},
        audio_data=b"test2"
    )
    
    # Clear cache
    audio_cache.clear_cache()
    
    # Verify cache is empty
    assert len(audio_cache.cache_index) == 0
    assert not any(audio_cache.cache_dir.iterdir())

@pytest.mark.asyncio
async def test_cleanup_task(audio_cache):
    """Test periodic cleanup task"""
    # Start cleanup task with short interval
    audio_cache.start_cleanup_task(interval_hours=0.001)
    
    # Add test data
    await audio_cache.cache_audio(
        text="test",
        engine="test",
        voice_id="test",
        settings={},
        audio_data=b"test"
    )
    
    # Wait for cleanup
    await asyncio.sleep(0.1)
    
    # Stop cleanup task
    audio_cache.stop_cleanup_task()
    
    # Verify cleanup task is stopped
    assert audio_cache._cleanup_task is None 