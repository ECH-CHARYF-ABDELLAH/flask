from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route("/player", methods=["GET"])
def get_player_info():
    player_slug = request.args.get("player")
    player_id = request.args.get("id")
    lang = request.args.get("lang", "ar")

    if not player_slug or not player_id:
        return jsonify({"error": "يرجى تمرير player و id"}), 400

    base_url = "https://www.goal.com"
    
    # بناء الرابط حسب اللغة
    if lang == "en":
        url = f"{base_url}/en/player/{player_slug}/{player_id}"
    else:
        url = f"{base_url}/{lang}/اللاعب/{player_slug}/{player_id}"

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

        # استخراج بيانات اللاعب
        result["player"] = content.get("player", {})
        result["stats"] = content.get("stats", {})
        result["teams"] = content.get("teams", [])
        result["latestNews"] = content.get("latestNews", [])
        result["transfers"] = content.get("transfers", [])

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
