from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route("/league", methods=["GET"])
def get_league_info():
    league_slug = request.args.get("league")
    league_id = request.args.get("id")
    lang = request.args.get("lang", "ar-sa")

    if not league_slug or not league_id:
        return jsonify({"error": "يرجى تمرير league و id"}), 400

    # Construct the URL based on the selected language
    base_url = "https://www.goal.com"
    if lang == "en":
        url = f"{base_url}/en/{league_slug}/fixtures-results/{league_id}"
    else:
        url = f"{base_url}/{lang}/{league_slug}/مواعيد-نتائج/{league_id}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

        if not script_tag:
            return jsonify({"error": "لم يتم العثور على الوسم <script> المطلوب."}), 404

        json_data = script_tag.string.strip()
        data = json.loads(json_data)
        content = data["props"]["pageProps"]["content"]

        result = {}

        # استخراج بيانات البطولة
        competition_data = content.get("competition", {})
        result["competition"] = competition_data

        # الأقسام الأخرى
        result["seasons"] = content.get("seasons", [])
        result["competition"] = content.get("competition", {})
        result["topCompetitions"] = content.get("topCompetitions", [])
        result["gamesets"] = content.get("gamesets", [])

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
