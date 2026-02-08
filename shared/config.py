"""
Configuration management for Document Analyzer application.
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENAI_BASE_URL"
    )
    model_id: str = Field(
        default="openrouter/google/gemini-3-flash-preview",
        env="MODEL_ID"
    )
    max_tokens: int = Field(default=4096, env="MAX_TOKENS")
    
    # Server Configuration
    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(default=8000, env="BACKEND_PORT")
    frontend_port: int = Field(default=8501, env="FRONTEND_PORT")
    
    # File Upload Configuration
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_extensions: str = Field(
        default="pdf,jpg,jpeg,png",
        env="ALLOWED_EXTENSIONS"
    )
    
    # Image Processing
    max_image_width: int = Field(default=600, env="MAX_IMAGE_WIDTH")
    image_dpi: int = Field(default=200, env="IMAGE_DPI")
    image_quality: int = Field(default=85, env="IMAGE_QUALITY")
    
    # Paths
    upload_dir: Path = Field(default=Path("./data/uploads"), env="UPLOAD_DIR")
    processed_dir: Path = Field(default=Path("./data/processed"), env="PROCESSED_DIR")
    log_dir: Path = Field(default=Path("./logs"), env="LOG_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=('settings_',)
    )
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_environment(self):
        """Setup environment variables for external libraries."""
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        os.environ["OPENAI_BASE_URL"] = self.openai_base_url


# Global settings instance
settings = Settings()
settings.setup_directories()
settings.setup_environment()
