import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

def fetch_gemini_data(api_key, topic, is_sub_node=False):
    client = genai.Client(api_key=api_key)
    
    # プロンプトの構築（元のロジックを継承）
    prompt = f"""
    「{topic}」について、多角的な視点から深く掘り下げたマインドマップ構造をJSONで出力してください。
    
    【出力フォーマット】
    {{
      "text": "{topic}",
      "children": [
        {{
          "text": "子要素1(30文字以内)",
          "children": [
            {{"text": "孫要素1-1(30文字以内)", "children": []}},
            {{"text": "孫要素1-2(30文字以内)", "children": []}}
          ]
        }}
      ]
    }}
    【条件】
    - JSONのみ出力すること。
    - 子要素は5つ、それぞれの孫要素は3〜5つ作成すること。
    - 日本語で具体的に記述すること。
    """

    config = types.GenerateContentConfig(
        temperature=0.7,
        response_mime_type="application/json",
        system_instruction="You are an expert business consultant. Output MUST be pure JSON."
    )

    try:
        # モデルは最新の 2.0 Flash を優先使用
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt,
            config=config
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    api_key = data.get('api_key')
    topic = data.get('topic')
    
    if not api_key or not topic:
        return jsonify({"error": "APIキーとテーマを入力してください"}), 400
    
    result = fetch_gemini_data(api_key, topic)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "AI生成に失敗しました"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
