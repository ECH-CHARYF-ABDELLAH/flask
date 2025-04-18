from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route("/team", methods=["GET"])
def get_team_info():
    team_slug = request.args.get("team")
    team_id = request.args.get("id")
    lang = request.args.get("lang", "ar-sa")

    if not team_slug or not team_id:
        return jsonify({"error": "يرجى تمرير team و id"}), 400

    # Construct the URL based on the selected language
    base_url = "https://www.goal.com"
    if lang == "en":
        url = f"{base_url}/en/team/{team_slug}/{team_id}"
    else:
        url = f"{base_url}/{lang}/الفريق/{team_slug}/{team_id}"

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

        # استخراج بيانات الفريق
        team_data = content.get("team", {})
        if "image" in team_data:
            del team_data["image"]
        result["team"] = team_data

        # الأقسام الأخرى
        result["bigMatch"] = content.get("bigMatch", {})
        result["latestNews"] = content.get("latestNews", [])
        result["latestShoppingNews"] = content.get("latestShoppingNews", [])
        result["summaryMatches"] = content.get("summaryMatches", [])
        result["summaryStandings"] = content.get("summaryStandings", [])

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
