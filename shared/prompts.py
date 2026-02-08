"""
Document extraction prompt template.
"""

DOCUMENT_EXTRACTION_PROMPT = """
# Document Analysis & Extraction Prompt

## Task
Extract structured data from document images and return as valid JSON. Use exact enumeration values provided. Extract text in its ORIGINAL SCRIPT - never transliterate or translate names, titles, or any text unless the original is in that script.

## Output Format

```json
{
  "document_classification": {
    "type": "enum: official_letter | decree | regulation | statistical_report | table_of_contents | administrative_decision | legal_amendment | memo | certificate | form | invoice | contract | court_ruling | minutes | circular | announcement | report | other",
    "subtype": "string or null",
    "category": "enum: legal | administrative | financial | statistical | correspondence | technical | hr | other",
    "primary_language": "enum: arabic | english | french | mixed | other",
    "secondary_languages": ["array of language codes if multilingual"]
  },

  "source": {
    "issuing_authority": "string: full organization name in ORIGINAL SCRIPT",
    "department": "string or null: specific division/unit in ORIGINAL SCRIPT",
    "location": "string or null: city/region",
    "document_number": "string or null: official reference number EXACTLY as shown",
    "related_references": ["array: all other document numbers mentioned anywhere in document"],
    "dates": {
      "primary_date": {
        "date_text": "string: main document date EXACTLY as written",
        "calendar_type": "enum: hijri | gregorian | unknown",
        "date_type": "enum: issue_date | effective_date | received_date | other",
        "indicators": "string: calendar markers like 'هـ' or 'م'",
        "location_in_document": "enum: header | body | footer | stamp | other"
      },
      "additional_dates": [
        {
          "date_text": "string: EXACTLY as written",
          "calendar_type": "enum: hijri | gregorian | unknown",
          "date_type": "enum: reference_date | deadline | expiry_date | effective_date | other",
          "context": "string: brief context of where/why this date appears",
          "indicators": "string or null"
        }
      ]
    }
  },

  "physical_properties": {
    "page_number": "string: e.g., '7', '7/254', 'single', 'unknown'",
    "total_pages": "integer or null",
    "image_type": "enum: digital | scanned | photographed | mixed | unknown",
    "quality": "enum: high | medium | low | illegible",
    "color_mode": "enum: color | grayscale | black_white | mixed",
    "has_watermark": "boolean",
    "watermark_description": "string or null",
    "has_security_pattern": "boolean",
    "security_pattern_description": "string or null",
    "orientation": "enum: portrait | landscape"
  },

  "official_marks": {
    "seals": [
      {
        "organization": "string: in ORIGINAL SCRIPT",
        "position": "enum: header | footer | center | top_right | top_left | bottom_right | bottom_left | margin | overlapping_text | other",
        "description": "string: detailed visual description",
        "is_digital": "boolean",
        "shape": "enum: circular | oval | rectangular | square | irregular | other"
      }
    ],
    "stamps": [
      {
        "type": "enum: approval | received | confidential | urgent | date_stamp | routing | registry | copy | original | other",
        "text_content": "string: ALL text on stamp in ORIGINAL SCRIPT",
        "color": "enum: red | blue | black | green | purple | brown | other",
        "position": "enum: header | footer | center | top_right | top_left | bottom_right | bottom_left | margin | overlapping_text | other",
        "is_digital": "boolean",
        "shape": "enum: circular | rectangular | square | oval | irregular"
      }
    ],
    "barcodes_qr": [
      {
        "type": "enum: barcode | qr_code | data_matrix | other",
        "position": "string",
        "readable_data": "string or null"
      }
    ]
  },

  "signatures_authorization": {
    "signatories": [
      {
        "name": "string: EXACTLY as written in ORIGINAL SCRIPT (Arabic/English/etc)",
        "name_transliteration": "string or null: only if BOTH scripts appear in document",
        "title": "string: official position in ORIGINAL SCRIPT",
        "signature_type": "enum: handwritten | digital | stamp | printed_name | not_present",
        "position": "enum: bottom_left | bottom_right | bottom_center | top_right | top_left | middle_right | middle_left | end_of_document | other",
        "role": "enum: primary_signatory | co_signatory | witness | approver | preparer | reviewer | other"
      }
    ],
    "approval_chain": [
      {
        "step": "integer: order in chain (1, 2, 3...)",
        "role": "enum: prepared_by | reviewed_by | approved_by | authorized_by | noted_by | verified_by | other",
        "name": "string or null: in ORIGINAL SCRIPT",
        "title": "string or null: in ORIGINAL SCRIPT",
        "date": "string or null"
      }
    ]
  },

  "routing_distribution": {
    "addressed_to": [
      {
        "type": "enum: person | department | organization | position | general",
        "name": "string: in ORIGINAL SCRIPT",
        "honorific": "string or null: titles like 'فضيلة', 'سعادة', 'معالي'"
      }
    ],
    "carbon_copy": [
      {
        "type": "enum: person | department | organization | position",
        "name": "string: in ORIGINAL SCRIPT"
      }
    ],
    "forwarded_to": [
      {
        "type": "enum: person | department | organization | position",
        "name": "string: in ORIGINAL SCRIPT",
        "date": "string or null"
      }
    ],
    "file_reference": "string or null: internal filing/tracking code",
    "classification": "string or null: security/filing classification in ORIGINAL SCRIPT"
  },

  "content": {
    "subject": "string: document subject/title in ORIGINAL SCRIPT",
    "subject_translation": "string or null: only if explicitly needed",
    "keywords": ["array: 5-10 keywords in ORIGINAL SCRIPT"],
    "full_text": "string: complete text extraction with line breaks, in ORIGINAL SCRIPT",
    "has_tables": "boolean",
    "tables": [
      {
        "title": "string or null: in ORIGINAL SCRIPT",
        "headers": ["array: column headers in ORIGINAL SCRIPT"],
        "rows": [
          ["array of cell values per row in ORIGINAL SCRIPT"]
        ],
        "notes": "string or null"
      }
    ],
    "has_lists": "boolean",
    "lists": [
      {
        "type": "enum: numbered | bulleted | lettered | arabic_numbered | hierarchical",
        "items": ["array: items in ORIGINAL SCRIPT with hierarchy preserved"]
      }
    ],
    "has_charts": "boolean",
    "charts": [
      {
        "type": "enum: bar | line | pie | area | scatter | table | mixed | other",
        "title": "string or null: chart title in ORIGINAL SCRIPT",
        "description": "string: brief description of what chart displays",
        "data": [
          {
            "label": "string: category/bar/data point label in ORIGINAL SCRIPT",
            "value": "number or string: numerical value EXACTLY as shown",
            "position": "integer: order/sequence (1, 2, 3...)"
          }
        ],
        "axis_info": {
          "x_axis_label": "string or null: in ORIGINAL SCRIPT",
          "y_axis_label": "string or null: in ORIGINAL SCRIPT",
          "x_axis_type": "enum: categorical | numerical | date | other",
          "y_axis_type": "enum: categorical | numerical | percentage | other"
        },
        "notes": "string or null: any footnotes or additional chart info"
      }
    ],
    "legal_articles": [
      {
        "article_number": "string: in ORIGINAL SCRIPT e.g., 'المادة الأولى', 'Article 1'",
        "article_title": "string or null: in ORIGINAL SCRIPT",
        "content": "string: full article text in ORIGINAL SCRIPT"
      }
    ],
    "financial_data": [
      {
        "description": "string: in ORIGINAL SCRIPT",
        "amount": "string: numerical value EXACTLY as shown",
        "currency": "string: SAR, USD, etc. or in ORIGINAL SCRIPT"
      }
    ]
  },

  "structural_elements": {
    "header": {
      "present": "boolean",
      "content": "string or null: ALL header text in ORIGINAL SCRIPT",
      "has_logo": "boolean",
      "logo_description": "string or null",
      "reference_numbers": ["array: any reference numbers in header"]
    },
    "footer": {
      "present": "boolean",
      "content": "string or null: ALL footer text in ORIGINAL SCRIPT",
      "has_page_number": "boolean",
      "page_info": "string or null: page numbering format"
    },
    "letterhead": {
      "present": "boolean",
      "organization_name": "string or null: in ORIGINAL SCRIPT",
      "organization_name_secondary": "string or null: if in another language",
      "emblem_description": "string or null",
      "contact_info": "string or null: addresses, phones, emails, websites"
    },
    "margins_notes": {
      "has_margin_notes": "boolean",
      "margin_content": "string or null: any handwritten or printed margin notes in ORIGINAL SCRIPT"
    }
  },

  "attachments_references": {
    "attachments_mentioned": [
      {
        "description": "string: in ORIGINAL SCRIPT",
        "count": "integer or null",
        "reference_number": "string or null"
      }
    ],
    "referenced_documents": [
      {
        "type": "enum: law | regulation | decree | previous_decision | letter | circular | report | contract | minutes | other",
        "reference": "string: document identifier in ORIGINAL SCRIPT",
        "date": "string or null: if date is mentioned for this reference"
      }
    ]
  },

  "condition_notes": {
    "completeness": "enum: complete | partial | missing_pages | fragment | unknown",
    "legibility_issues": ["array: describe sections with poor legibility"],
    "physical_damage": "enum: none | minor | moderate | severe | not_applicable",
    "damage_description": "string or null",
    "handwritten_annotations": {
      "present": "boolean",
      "description": "string or null: describe notes, highlights, corrections"
    },
    "special_observations": "string or null"
  },

  "confidence_quality": {
    "overall_confidence": "enum: high | medium | low",
    "uncertain_elements": ["array: list specific elements with low confidence"],
    "requires_manual_review": "boolean",
    "review_reasons": ["array: specific areas needing verification"]
  }
}
```

## Critical Extraction Rules

### 1. ORIGINAL SCRIPT REQUIREMENT ⚠️
**MOST IMPORTANT**: Extract ALL text in its original script/language:
- Arabic names stay in Arabic: سلمان بن فوزان الفوزان (NOT "Salman bin Fawzan Al-Fawzan")
- Arabic titles stay in Arabic: القائم بعمل نائب وزير العدل (NOT translated)
- Do NOT romanize, transliterate, or translate unless the document itself shows both versions
- Preserve all diacritics and special characters exactly

### 2. Chart and Graph Data Extraction
**CRITICAL**: Extract actual data values as structured arrays:

For **Bar Charts**:
```json
"data": [
  {"label": "التعديلات", "value": 33, "position": 1},
  {"label": "المواد الملغية", "value": 51, "position": 2}
]
```

**DO NOT** create text summaries - extract structured data objects.

## Output Instructions
Return ONLY the JSON object. No markdown code blocks, no explanatory text. Start directly with `{` and end with `}`.
""".strip()


def get_extraction_prompt() -> str:
    """Get the document extraction prompt."""
    return DOCUMENT_EXTRACTION_PROMPT
