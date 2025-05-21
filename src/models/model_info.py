from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ModelInfo:
    """
    Data class for model information from Civitai
    """
    id: int
    name: str
    description: str
    type: str
    base_model: str
    version_id: int
    download_url: str
    tags: List[str] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    nsfw: bool = False
    size: int = 0
    download_date: str = ""
    thumbnail: str = ""
    favorite: bool = False
    last_updated: str = ""
    creator: str = ""
    version_name: str = ""
    stats: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert ModelInfo to dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "base_model": self.base_model,
            "version_id": self.version_id,
            "download_url": self.download_url,
            "tags": self.tags,
            "images": self.images,
            "nsfw": self.nsfw,
            "size": self.size,
            "download_date": self.download_date,
            "thumbnail": self.thumbnail,
            "favorite": self.favorite,
            "last_updated": self.last_updated,
            "creator": self.creator,
            "version_name": self.version_name,
            "stats": self.stats,
            "url": f"https://civitai.com/models/{self.id}"
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelInfo':
        """Create ModelInfo from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            type=data.get("type", "Other"),
            base_model=data.get("base_model", "Unknown"),
            version_id=data.get("version_id", 0),
            download_url=data.get("download_url", ""),
            tags=data.get("tags", []),
            images=data.get("images", []),
            nsfw=data.get("nsfw", False),
            size=data.get("size", 0),
            download_date=data.get("download_date", ""),
            thumbnail=data.get("thumbnail", ""),
            favorite=data.get("favorite", False),
            last_updated=data.get("last_updated", ""),
            creator=data.get("creator", "Unknown"),
            version_name=data.get("version_name", ""),
            stats=data.get("stats", {})
        )