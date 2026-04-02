import os
import re
import sqlite3
import pickle
import numpy as np
from datetime import datetime
from config import CLASSIFICATION_DB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# تعريف الأنواع
DATA_TYPES = ["admin", "param", "keys", "cookies", "headers", "vuln", "other"]

# أنماط regex الأساسية (كحل أخير)
FALLBACK_PATTERNS = {
    "admin": re.compile(r'https?://[^/]+/(admin|login|dashboard|wp-admin|administrator|manage)', re.IGNORECASE),
    "param": re.compile(r'.*\?.*=.*'),
    "keys": re.compile(r'(?i)(api[_-]?key|secret|token|apikey|access_token|private_key)'),
    "cookies": re.compile(r'(?i)(cookie|set-cookie)'),
    "headers": re.compile(r'(?i)(x-|header|content-type|authorization)'),
    "vuln": re.compile(r'(?i)(vuln|exploit|cve-|xss|sql|injection)'),
}

def init_db():
    """إنشاء قاعدة البيانات وجداولها إذا لم تكن موجودة."""
    conn = sqlite3.connect(CLASSIFICATION_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS known_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            url_type TEXT,
            source TEXT,
            timestamp REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT,
            url_type TEXT,
            weight REAL,
            is_regex BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def add_training_example(url, url_type, source="user"):
    """إضافة مثال تدريبي إلى قاعدة البيانات."""
    conn = sqlite3.connect(CLASSIFICATION_DB)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO known_urls (url, url_type, source, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (url, url_type, source, time.time()))
        conn.commit()
    except Exception as e:
        print(f"Error adding training example: {e}")
    finally:
        conn.close()
    # إعادة تدريب النموذج
    train_model()

def train_model():
    """تدريب نموذج Naive Bayes على البيانات المتاحة."""
    conn = sqlite3.connect(CLASSIFICATION_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT url, url_type FROM known_urls")
    data = cursor.fetchall()
    conn.close()
    
    if len(data) < 10:
        print("⚠️ Not enough training data (need at least 10 examples). Using fallback patterns only.")
        return None, None
    
    urls = [row[0] for row in data]
    labels = [row[1] for row in data]
    
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3,5))
    X = vectorizer.fit_transform(urls)
    y = np.array(labels)
    
    model = MultinomialNB()
    model.fit(X, y)
    
    # حفظ النموذج
    joblib.dump((vectorizer, model), os.path.join(os.path.dirname(CLASSIFICATION_DB), "model.pkl"))
    return vectorizer, model

def load_model():
    """تحميل النموذج المدرب."""
    model_path = os.path.join(os.path.dirname(CLASSIFICATION_DB), "model.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None, None

def classify_with_ml(url):
    """تصنيف URL باستخدام النموذج (إن وُجد)."""
    vectorizer, model = load_model()
    if vectorizer is None or model is None:
        return None, 0.0
    X = vectorizer.transform([url])
    proba = model.predict_proba(X)[0]
    pred_class = model.predict(X)[0]
    confidence = max(proba)
    return pred_class, confidence

def classify_with_fallback(url):
    """استخدام الأنماط الاحتياطية (regex) كحل أخير."""
    line_lower = url.lower()
    matches = []
    for typ, pattern in FALLBACK_PATTERNS.items():
        if pattern.search(url):
            matches.append(typ)
    if len(matches) == 1:
        return matches[0], 0.8
    elif len(matches) > 1:
        return matches[0], 0.6
    else:
        return "other", 0.4

def classify_url(url):
    """تصنيف URL باستخدام النموذج أولاً ثم الاحتياطي."""
    # محاولة ML
    ml_type, ml_conf = classify_with_ml(url)
    if ml_type and ml_conf > 0.7:
        return ml_type, ml_conf, "ml"
    
    # الرجوع إلى fallback
    fb_type, fb_conf = classify_with_fallback(url)
    return fb_type, fb_conf, "fallback"

# تهيئة قاعدة البيانات عند الاستيراد
init_db()