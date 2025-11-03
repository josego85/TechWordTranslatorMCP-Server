"""Domain models for words and translations."""

from typing import Optional
from pydantic import BaseModel


class Translation(BaseModel):
    """Translation model for Spanish and German translations."""

    id: int
    word_id: int
    spanish_word: str
    german_word: str


class Word(BaseModel):
    """Word model (English word)."""

    id: int
    english_word: str
    translation: Optional[Translation] = None

    def get_translation(self, locale: str) -> Optional[str]:
        """Get translation for a specific locale.

        Args:
            locale: Language code ('en', 'es', 'de')

        Returns:
            Translated term or None if not found
        """
        if locale == "en":
            return self.english_word

        if not self.translation:
            return None

        if locale == "es":
            return self.translation.spanish_word
        elif locale == "de":
            return self.translation.german_word

        return None

    def get_all_translations(self) -> dict[str, str]:
        """Get all translations as a dictionary."""
        result = {"en": self.english_word}

        if self.translation:
            result["es"] = self.translation.spanish_word
            result["de"] = self.translation.german_word

        return result
