"""Voice Profile Manager for Universal TTS System"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
from datetime import datetime
import hashlib
import yaml

from utils.exceptions import VoiceProfileError
from utils.logger import TTSLogger

class VoiceManager:
    """Manager for voice profiles"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load all voice profiles from disk"""
        for profile_file in self.profiles_dir.glob("*.yaml"):
            try:
                with open(profile_file, 'r') as f:
                    profile = yaml.safe_load(f)
                    self.profiles[profile["name"]] = profile
            except Exception as e:
                print(f"Error loading profile {profile_file}: {str(e)}")
    
    def create_profile(self, name: str, engine: str, voice_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new voice profile
        
        Args:
            name: Profile name
            engine: TTS engine to use
            voice_id: Voice identifier
            settings: Engine-specific settings
            
        Returns:
            Created profile dictionary
            
        Raises:
            ValueError: If profile with same name exists
        """
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")
        
        profile = {
            "name": name,
            "engine": engine,
            "voice_id": voice_id,
            "settings": settings
        }
        
        # Save to disk
        profile_path = self.profiles_dir / f"{name}.yaml"
        with open(profile_path, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        
        self.profiles[name] = profile
        return profile
    
    def update_profile(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing voice profile
        
        Args:
            name: Profile name
            settings: New settings to apply
            
        Returns:
            Updated profile dictionary
            
        Raises:
            ValueError: If profile doesn't exist
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        profile = self.profiles[name]
        profile["settings"].update(settings)
        
        # Save to disk
        profile_path = self.profiles_dir / f"{name}.yaml"
        with open(profile_path, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False)
        
        return profile
    
    def delete_profile(self, name: str) -> None:
        """
        Delete a voice profile
        
        Args:
            name: Profile name
            
        Raises:
            ValueError: If profile doesn't exist
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        # Delete from disk
        profile_path = self.profiles_dir / f"{name}.yaml"
        if profile_path.exists():
            os.remove(profile_path)
        
        del self.profiles[name]
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a voice profile by name
        
        Args:
            name: Profile name
            
        Returns:
            Profile dictionary or None if not found
        """
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        List all available profiles
        
        Returns:
            List of profile dictionaries
        """
        return list(self.profiles.values())
    
    def export_profile(self, name: str, output_path: str) -> None:
        """
        Export a profile to a file
        
        Args:
            name: Profile name
            output_path: Path to save the profile
            
        Raises:
            ValueError: If profile doesn't exist
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        with open(output_path, 'w') as f:
            yaml.dump(self.profiles[name], f, default_flow_style=False)
    
    def import_profile(self, profile_path: str) -> Dict[str, Any]:
        """
        Import a profile from a file
        
        Args:
            profile_path: Path to the profile file
            
        Returns:
            Imported profile dictionary
            
        Raises:
            ValueError: If profile with same name exists
        """
        with open(profile_path, 'r') as f:
            profile = yaml.safe_load(f)
        
        return self.create_profile(
            name=profile["name"],
            engine=profile["engine"],
            voice_id=profile["voice_id"],
            settings=profile["settings"]
        )
    
    def clone_profile(self, name: str, new_name: str) -> Dict[str, Any]:
        """
        Create a copy of an existing profile
        
        Args:
            name: Source profile name
            new_name: New profile name
            
        Returns:
            Cloned profile dictionary
            
        Raises:
            ValueError: If source profile doesn't exist or new name already exists
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' not found")
        if new_name in self.profiles:
            raise ValueError(f"Profile '{new_name}' already exists")
        
        profile = self.profiles[name].copy()
        profile["name"] = new_name
        
        return self.create_profile(
            name=new_name,
            engine=profile["engine"],
            voice_id=profile["voice_id"],
            settings=profile["settings"]
        )

    def backup_profiles(self, backup_dir: str) -> str:
        """
        Create a backup of all voice profiles.

        Args:
            backup_dir: Directory to store the backup

        Returns:
            Path to the backup directory
        """
        try:
            backup_dir = Path(backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"profiles_backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy all profile files
            for profile_file in self.profiles_dir.glob("*.yaml"):
                shutil.copy2(profile_file, backup_path)

            return str(backup_path)
        except Exception as e:
            raise VoiceProfileError(f"Failed to backup profiles: {str(e)}")

    def restore_profiles(self, backup_dir: str) -> None:
        """
        Restore voice profiles from a backup.

        Args:
            backup_dir: Directory containing the backup
        """
        try:
            backup_dir = Path(backup_dir)
            if not backup_dir.exists():
                raise VoiceProfileError(f"Backup directory not found: {backup_dir}")

            # Clear existing profiles
            self.profiles.clear()
            for profile_file in self.profiles_dir.glob("*.yaml"):
                profile_file.unlink()

            # Restore profiles from backup
            for profile_file in backup_dir.glob("*.yaml"):
                shutil.copy2(profile_file, self.profiles_dir)

            # Reload profiles
            self._load_profiles()
        except Exception as e:
            raise VoiceProfileError(f"Failed to restore profiles: {str(e)}")
