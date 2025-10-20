from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List


class Settings(BaseSettings):
	app_name: str = "Food Surplus Matcher"
	debug: bool = False
	database_url: str = "sqlite:///./food_matcher.db"
	cors_origins: List[str] = ["*"]
	expiry_interval_seconds: int = 60

	class Config:
		env_prefix = "FSM_"
		case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()


