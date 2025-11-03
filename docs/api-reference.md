# API Reference

Complete reference for all available MCP tools.

## Available Tools

### 1. `translate_term`

Translate a technical term from one language to another.

**Parameters:**
- `term` (string): The technical term to translate
- `from_locale` (string): Source language code (en, es, or de)
- `to_locale` (string): Target language code (en, es, or de)

**Example:**
```
translate_term(term="computer", from_locale="en", to_locale="es")
→ computer (en) → computadora (es)
```

**Returns:**
- Success: Formatted translation string
- Not found: Message indicating term not found

---

### 2. `search_tech_terms`

Search for technical terms in the database.

**Parameters:**
- `term` (string): The term to search for (case-insensitive partial match)
- `locale` (string, optional): Language to search in (en, es, or de)
- `limit` (int, optional): Maximum number of results (default: 10, max: 50)

**Example:**
```
search_tech_terms(term="software", locale="en", limit=5)
```

**Returns:**
- List of matching terms with their translations
- Empty list if no matches found

---

### 3. `get_all_translations`

Get all available translations for a term from a specific source language.

**Parameters:**
- `term` (string): The technical term to translate
- `source_locale` (string): Source language code (en, es, or de)

**Example:**
```
get_all_translations(term="server", source_locale="en")
```

**Returns:**
- Formatted string with all available translations
- Error message if term not found

---

### 4. `get_term_details`

Get detailed information about a specific technical term by its ID.

**Parameters:**
- `word_id` (int): The ID of the word to retrieve

**Example:**
```
get_term_details(word_id=42)
```

**Returns:**
- Complete term information including all translations
- Error message if ID not found

---

### 5. `list_tech_terms`

List technical terms with pagination support.

**Parameters:**
- `page_size` (int, optional): Number of terms per page (default: 15)
- `cursor` (string, optional): Pagination cursor for next/previous page

**Example:**
```
list_tech_terms(page_size=10)
```

**Returns:**
- Paginated list of terms
- Pagination metadata (next cursor, page info)

---

## Supported Languages

- **en** - English
- **es** - Spanish (Español)
- **de** - German (Deutsch)

## Response Formats

All tools return human-readable formatted strings suitable for display in chat interfaces.

### Translation Format
```
[term] (source_locale) → [translated_term] (target_locale)
```

### Search Results Format
```
Found N results:
1. [english_word]
   → es: [spanish_translation]
   → de: [german_translation]
...
```

## Error Handling

All tools handle errors gracefully and return user-friendly error messages:

- **Not Found**: "No translation found for [term]"
- **Invalid Locale**: "Unsupported language code"
- **API Errors**: "Unable to fetch data from API"

## Related Documentation

- [Quick Start Guide](quickstart.md) - Get started in 5 minutes
- [Integration Guides](cursor-setup.md) - IDE integration
- [Backend API](https://github.com/josego85/TechWordTranslatorAPI) - TechWordTranslator API
