"""Audio Cache Manager for Universal TTS System"""

import os
import hashlib
import json
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import shutil
from datetime import datetime, timedelta
import threading
from collections import OrderedDict
import aiofiles
import asyncio

from utils.exceptions import AudioCacheError
from utils.logger import TTSLogger

class AudioCache:
    """Cache manager for TTS audio output"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 100, max_age_days: int = 7):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age_seconds = max_age_days * 24 * 60 * 60
        self.index_file = self.cache_dir / "cache_index.json"
        self.cache_index: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task = None
        self._load_index()
    
    def _load_index(self) -> None:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception as e:
                print(f"Error loading cache index: {str(e)}")
                self.cache_index = {}
    
    def _save_index(self) -> None:
        """Save cache index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.cache_index, f)
        except Exception as e:
            print(f"Error saving cache index: {str(e)}")
    
    def _generate_cache_key(self, text: str, engine: str, voice_id: str, settings: Dict[str, Any]) -> str:
        """Generate a unique cache key for the given parameters"""
        key_data = f"{text}:{engine}:{voice_id}:{json.dumps(settings, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry"""
        return self.cache_dir / f"{cache_key}.mp3"
    
    def _get_cache_size(self) -> int:
        """Get total size of cache in bytes"""
        total_size = 0
        for cache_key in self.cache_index:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                total_size += cache_path.stat().st_size
        return total_size
    
    def _remove_old_entries(self) -> None:
        """Remove cache entries that are too old"""
        current_time = time.time()
        to_remove = []
        
        for cache_key, entry in self.cache_index.items():
            if current_time - entry["created_at"] > self.max_age_seconds:
                to_remove.append(cache_key)
        
        for cache_key in to_remove:
            self.remove_from_cache(cache_key)
    
    def _remove_largest_entries(self, target_size: int) -> None:
        """Remove largest cache entries until total size is below target"""
        while self._get_cache_size() > target_size:
            # Find largest entry
            largest_key = max(
                self.cache_index.keys(),
                key=lambda k: self._get_cache_path(k).stat().st_size if self._get_cache_path(k).exists() else 0
            )
            self.remove_from_cache(largest_key)
    
    async def get_cached_audio(
        self,
        text: str,
        engine: str,
        voice_id: str,
        settings: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Get cached audio if available
        
        Args:
            text: Text that was converted to speech
            engine: TTS engine used
            voice_id: Voice ID used
            settings: Engine settings used
            
        Returns:
            Cached audio data or None if not found
        """
        cache_key = self._generate_cache_key(text, engine, voice_id, settings)
        
        if cache_key not in self.cache_index:
            return None
        
        entry = self.cache_index[cache_key]
        cache_path = self._get_cache_path(cache_key)
        
        # Check if file exists and is not too old
        if not cache_path.exists():
            del self.cache_index[cache_key]
            self._save_index()
            return None
        
        if time.time() - entry["created_at"] > self.max_age_seconds:
            self.remove_from_cache(cache_key)
            return None
        
        # Update last accessed time
        entry["last_accessed"] = time.time()
        self._save_index()
        
        # Read cached audio
        try:
            with open(cache_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading cached audio: {str(e)}")
            return None
    
    async def cache_audio(
        self,
        text: str,
        engine: str,
        voice_id: str,
        settings: Dict[str, Any],
        audio_data: bytes
    ) -> str:
        """
        Cache audio data
        
        Args:
            text: Text that was converted to speech
            engine: TTS engine used
            voice_id: Voice ID used
            settings: Engine settings used
            audio_data: Audio data to cache
            
        Returns:
            Cache key for the stored audio
        """
        cache_key = self._generate_cache_key(text, engine, voice_id, settings)
        cache_path = self._get_cache_path(cache_key)
        
        # Check if we need to make space
        current_size = self._get_cache_size()
        if current_size + len(audio_data) > self.max_size_bytes:
            self._remove_largest_entries(self.max_size_bytes - len(audio_data))
        
        # Save audio data
        try:
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
        except Exception as e:
            print(f"Error saving cached audio: {str(e)}")
            return cache_key
        
        # Update cache index
        self.cache_index[cache_key] = {
            "created_at": time.time(),
            "last_accessed": time.time(),
            "size": len(audio_data),
            "engine": engine,
            "voice_id": voice_id
        }
        self._save_index()
        
        return cache_key
    
    def remove_from_cache(self, cache_key: str) -> None:
        """
        Remove an entry from the cache
        
        Args:
            cache_key: Key of the cache entry to remove
        """
        if cache_key in self.cache_index:
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                try:
                    os.remove(cache_path)
                except Exception as e:
                    print(f"Error removing cached file: {str(e)}")
            del self.cache_index[cache_key]
            self._save_index()
    
    def clear_cache(self) -> None:
        """Clear all cached audio"""
        for cache_key in list(self.cache_index.keys()):
            self.remove_from_cache(cache_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary containing cache statistics
        """
        total_size = self._get_cache_size()
        entry_count = len(self.cache_index)
        oldest_entry = min(
            (entry["created_at"] for entry in self.cache_index.values()),
            default=time.time()
        )
        
        return {
            "total_size_bytes": total_size,
            "entry_count": entry_count,
            "oldest_entry_age_seconds": time.time() - oldest_entry,
            "max_size_bytes": self.max_size_bytes,
            "max_age_seconds": self.max_age_seconds
        }
    
    def start_cleanup_task(self, interval_hours: int = 24) -> None:
        """
        Start periodic cleanup task
        
        Args:
            interval_hours: Hours between cleanup runs
        """
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval_hours))
    
    def stop_cleanup_task(self) -> None:
        """Stop periodic cleanup task"""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            self._cleanup_task = None
    
    async def _cleanup_loop(self, interval_hours: int) -> None:
        """Periodic cleanup task"""
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)
                self._remove_old_entries()
                if self._get_cache_size() > self.max_size_bytes:
                    self._remove_largest_entries(self.max_size_bytes)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in cleanup task: {str(e)}") 