# 怪談白物語 文章置換ツール

怪談白物語をスムーズに作るためのStreamlitアプリです。

## 機能

- 元の文章を入力
- 置換ルールを表形式で入力
- 元の文章に対して一括置換
- 置換後の単語にさらに置換がかからない
- 置換結果をテキストでダウンロード
- 置換ルールをJSONでダウンロード

## ローカル実行

```bash
pip install -r requirements.txt
streamlit run app.py
