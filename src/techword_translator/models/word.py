"""Domain models for words and translations."""

from typing import Optional, List
from pydantic import BaseModel


class TranslationItem(BaseModel):
    """Single translation entry."""

    language: str
    translation: str


class Word(BaseModel):
    """Word model with embedded translations."""

    id: int
    word: str
    translations: List[TranslationItem] = []

    def get_translation(self, locale: str) -> Optional[str]:
        """Get translation for a specific locale.

        Args:
            locale: Language code ('en', 'es', 'de')

        Returns:
            Translated term or None if not found
        """
        for t in self.translations:
            if t.language == locale:
                return t.translation
        return None

    def get_all_translations(self) -> dict[str, str]:
        """Get all translations as a dictionary."""
        return {t.language: t.translation for t in self.translations}
