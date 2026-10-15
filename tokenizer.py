"""
وحدة تحليل وتصنيف النصوص (Advanced Text Tokenizer & Normalizer)
مسؤولة عن تنظيف النصوص وفهم العامية والمصطلحات العربية والإنجليزية.
"""

import re
from typing import List
from config import logger

class AdvancedTokenizer:
    def __init__(self):
        logger.info("جاري تهيئة محلل النصوص والكلمات (AdvancedTokenizer)...")
        # قاموس متطور لربط العامية بالمفردات الأساسية لفهم لغة البشر
        self.arabic_synonyms = {
            "نت": "إنترنت",
            "net": "internet",
            "ابغى": "أريد",
            "بدي": "أريد",
            "كود": "برمجة",
            "عطيني": "اعرض",
            "ازاي": "كيف",
            "ليه": "لماذا",
            "وين": "أين",
            "شلون": "كيف",
            "عشان": "لأن",
            "معليش": "عفوا",
            "شو": "ماذا",
            "ايه": "ماذا",
            "سوي": "نفذ",
            "هات": "أعطني"
        }

    def clean_raw_text(self, text: str) -> str:
        """تنظيف النص من الحروف الزائدة والرموز المزعجة مع الحفاظ على البنية"""
        if not isinstance(text, str):
            return ""
        # إزالة علامات التحكم والمسافات الزائدة
        cleaned = re.sub(r'[\r\t\v\f]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    def tokenize(self, text: str, normalize: bool = True) -> List[str]:
        """تقطيع النص إلى رموز (Tokens) مع تطبيق المعالجة المترادفة"""
        cleaned_text = self.clean_raw_text(text)
        # استخراج الكلمات والرموز البرمجية بدقة باللغتين العربية والإنجليزية
        tokens = re.findall(r'\w+|[^\w\s]', cleaned_text, re.UNICODE)
        
        if not normalize:
            return tokens

        processed_tokens = []
        for token in tokens:
            lower_token = token.lower()
            if lower_token in self.arabic_synonyms:
                processed_tokens.append(self.arabic_synonyms[lower_token])
            else:
                processed_tokens.append(token)

        return processed_tokens