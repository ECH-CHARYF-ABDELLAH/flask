from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

app = Flask(__name__)

@app.route("/match-details", methods=["GET"])
def get_match_details():
    team_a = request.args.get("team_a")
    team_b = request.args.get("team_b")
    match_id = request.args.get("match_id")
    lang = request.args.get("lang", "ar-sa")

    if not team_a or not team_b or not match_id:
        return jsonify({"error": "يرجى تمرير team_a و team_b و match_id"}), 400

    # ترميز أسماء الفرق بشكل آمن للرابط
    team_a_encoded = urllib.parse.quote(team_a)
    team_b_encoded = urllib.parse.quote(team_b)

    # بناء الرابط حسب اللغة
    if lang == "en":
        url = f"https://www.goal.com/en/match/{team_a_encoded}-vs-{team_b_encoded}/{match_id}"
    else:
        url = f"https://www.goal.com/{lang}/المباراة/{team_a_encoded}-v-{team_b_encoded}/{match_id}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

        if script_tag:
            json_data = script_tag.string.strip()
            data = json.loads(json_data)
            match_data = data["props"]["pageProps"]["content"]["match"]
            return jsonify(match_data)

        else:
            return jsonify({"error": "لم يتم العثور على الوسم <script> المطلوب."}), 404

    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء المعالجة: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
