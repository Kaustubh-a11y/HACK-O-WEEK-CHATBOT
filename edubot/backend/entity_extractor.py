import re

COURSE_ALIASES = {
    "cs": "Computer Science",
    "it": "Information Technology",
    "bca": "BCA",
    "bba": "BBA",
    "mba": "MBA",
    "mca": "MCA",
    "bsc": "B.Sc IT",
    "civil": "Civil Engineering",
    "mech": "Mechanical Engineering",
    "computer science": "Computer Science",
    "information technology": "Information Technology",
    "commerce": "Commerce"
}

WORD_TO_NUM = {
    "first": 1, "second": 2, "third": 3, "fourth": 4,
    "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8
}

RESPONSE_TEMPLATES = {
    "semester+course": "For Semester {semester} {course}, {base}",
    "semester_only": "Regarding Semester {semester}: {base}",
    "course_only": "For {course} students: {base}",
    "date_only": "On {date}: {base}",
    "year_only": "For {year} students: {base}",
    "semester+year": "Semester {semester} ({year}): {base}",
    "none": "{base}"
}

class EntityExtractor:
    """Extracts entities from free text and injects them into response templates."""
    def extract(self, query: str) -> dict:
        entities = {}
        lowercased = query.lower()

        # 1. SEMESTER NUMBER
        m1 = re.search(r'\bsem(?:ester)?\s*[-]?\s*(\d+)\b', lowercased)
        m2 = re.search(r'\b(\d+)(?:st|nd|rd|th)\s+sem(?:ester)?\b', lowercased)
        m3 = re.search(r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+sem\b', lowercased)
        
        if m1:
            entities["semester"] = int(m1.group(1))
        elif m2:
            entities["semester"] = int(m2.group(1))
        elif m3:
            entities["semester"] = WORD_TO_NUM[m3.group(1)]

        # 2. COURSE / BRANCH CODE
        for alias, full_name in COURSE_ALIASES.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, lowercased):
                entities["course"] = full_name
                break

        # 3. DATE / MONTH
        d1 = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})(?:[\/\-\.](\d{2,4}))?\b', lowercased)
        months_regex = r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'
        d2 = re.search(r'\b(\d{1,2})\s+' + months_regex + r'\b', lowercased)
        d3 = re.search(r'\b' + months_regex + r'\s+(\d{1,2})\b', lowercased)
        d4 = re.search(r'\b(tomorrow|today|next\s+\w+|this\s+week|this\s+month)\b', lowercased)
        
        if d1:
            entities["date"] = d1.group(0)
        elif d2:
            entities["date"] = d2.group(0)
        elif d3:
            entities["date"] = d3.group(0)
        elif d4:
            entities["date"] = d4.group(0)

        # 4. YEAR
        y1 = re.search(r'\b(20\d{2})\b', lowercased)
        y2 = re.search(r'\b(first|second|third|final)\s+year\b', lowercased)
        
        if y1:
            entities["year"] = y1.group(1)
        elif y2:
            entities["year"] = y2.group(0)

        # 5. ROLL NUMBER
        r1 = re.search(r'\b([a-z]{1,4}\d{4,8})\b', lowercased)
        r2 = re.search(r'\b(\d{4}[a-z]{2,5}\d{3})\b', lowercased)
        if r1:
            entities["roll_no"] = r1.group(1).upper()
        elif r2:
            entities["roll_no"] = r2.group(1).upper()

        return entities

    def answer_enhancer(self, base_answer: str, entities: dict) -> str:
        sem = entities.get("semester")
        crs = entities.get("course")
        dt = entities.get("date")
        yr = entities.get("year")
        
        if sem and crs:
            tpl = RESPONSE_TEMPLATES["semester+course"]
        elif sem and yr:
            tpl = RESPONSE_TEMPLATES["semester+year"]
        elif sem:
            tpl = RESPONSE_TEMPLATES["semester_only"]
        elif crs:
            tpl = RESPONSE_TEMPLATES["course_only"]
        elif yr:
            tpl = RESPONSE_TEMPLATES["year_only"]
        elif dt:
            tpl = RESPONSE_TEMPLATES["date_only"]
        else:
            tpl = RESPONSE_TEMPLATES["none"]
            
        return tpl.format(
            semester=sem or "",
            course=crs or "",
            date=dt or "",
            year=yr or "",
            base=base_answer
        ).replace("  ", " ").strip()
