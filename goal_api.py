from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/matches", methods=["GET"])
def get_matches():
    # الحصول على البرامتر أو استخدام القيم الافتراضية
    date = request.args.get("date", default=datetime.today().strftime('%Y-%m-%d'))
    lang = request.args.get("lang", default="ar-sa")

    # تحديد اسم صفحة النتائج بناءً على اللغة
    results_slug = "النتائج" if lang == "ar-sa" else "results"

    # إنشاء الرابط الصحيح
    url = f"https://www.goal.com/{lang}/{results_slug}/{date}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

    if script_tag:
        json_data = script_tag.string.strip()
        data = json.loads(json_data)
        try:
            content = data["props"]["pageProps"]["content"]["liveScores"]
            return jsonify(content)
        except KeyError:
            return jsonify({"error": "المحتوى غير موجود في البيانات."}), 404
    else:
        return jsonify({"error": "لم يتم العثور على الوسم <script> المطلوب."}), 404

if __name__ == "__main__":
    app.run(debug=True)
