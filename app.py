import json

import pandas as pd
import streamlit as st

from replacement import apply_replacements, count_matches, normalize_rules


st.set_page_config(
    page_title="怪談白物語 文章置換ツール",
    page_icon="👻",
    layout="wide",
)


INITIAL_RULES = [
    {"元の単語": "", "修正後の単語": ""},
]


def init_state() -> None:
    if "rules" not in st.session_state:
        st.session_state.rules = INITIAL_RULES.copy()

    if "original_text" not in st.session_state:
        st.session_state.original_text = ""


def load_sample() -> None:
    st.session_state.original_text = (
        "放課後、私は古い学校の廊下を歩いていた。\n"
        "理科室の前で、誰もいないはずの教室から小さな声が聞こえた。\n"
        "その声は、昨日いなくなった友達の声にそっくりだった。"
    )
    st.session_state.rules = [
        {"元の単語": "学校", "修正後の単語": "病院"},
        {"元の単語": "理科室", "修正後の単語": "霊安室"},
        {"元の単語": "友達", "修正後の単語": "母"},
    ]


def reset_all() -> None:
    st.session_state.original_text = ""
    st.session_state.rules = INITIAL_RULES.copy()


init_state()


st.title("👻 怪談白物語 文章置換ツール")

st.caption(
    "元の文章に対して置換ルールを一括適用します。"
    "置換後の単語にさらに置換がかかることはありません。"
)


# -----------------------------
# 元の文章
# -----------------------------
st.subheader("元の文章")

original_text = st.text_area(
    label="ここに元の文章を入力してください",
    value=st.session_state.original_text,
    height=260,
    key="original_text_input",
    placeholder="例: 放課後、私は古い学校の廊下を歩いていた……",
)

st.session_state.original_text = original_text


# -----------------------------
# 置換ルール
# -----------------------------
st.subheader("置換ルール")

st.write("左に元の単語、右に修正後の単語を入力してください。")

rules_df = pd.DataFrame(st.session_state.rules)

edited_df = st.data_editor(
    rules_df,
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "元の単語": st.column_config.TextColumn(
            "元の単語",
            help="元の文章から探す単語",
            required=False,
        ),
        "修正後の単語": st.column_config.TextColumn(
            "修正後の単語",
            help="置き換え後の単語",
            required=False,
        ),
    },
)

edited_rows = edited_df.fillna("").to_dict(orient="records")
st.session_state.rules = edited_rows

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("＋追加", use_container_width=True):
        st.session_state.rules.append({"元の単語": "", "修正後の単語": ""})
        st.rerun()

with col2:
    if st.button("サンプル", use_container_width=True):
        load_sample()
        st.rerun()

with col3:
    if st.button("リセット", use_container_width=True):
        reset_all()
        st.rerun()


rules, warnings = normalize_rules(st.session_state.rules)

for warning in warnings:
    st.warning(warning)


# -----------------------------
# マッチ数
# -----------------------------
if original_text and rules:
    st.subheader("置換対象の確認")

    match_counts = count_matches(original_text, rules)

    match_df = pd.DataFrame(
        [
            {
                "元の単語": src,
                "修正後の単語": rules[src],
                "出現回数": count,
            }
            for src, count in match_counts.items()
        ]
    )

    st.dataframe(match_df, hide_index=True, use_container_width=True)


# -----------------------------
# 修正後の文章
# -----------------------------
st.subheader("修正後の文章")

replaced_text = apply_replacements(original_text, rules)

st.text_area(
    label="置換結果",
    value=replaced_text,
    height=260,
)


# -----------------------------
# ダウンロード
# -----------------------------
download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        label="修正後の文章をダウンロード",
        data=replaced_text,
        file_name="kaidan_replaced.txt",
        mime="text/plain",
        use_container_width=True,
    )

with download_col2:
    rules_json = json.dumps(rules, ensure_ascii=False, indent=2)

    st.download_button(
        label="置換ルールをJSONでダウンロード",
        data=rules_json,
        file_name="replacement_rules.json",
        mime="application/json",
        use_container_width=True,
    )


# -----------------------------
# 補足
# -----------------------------
with st.expander("このアプリの置換仕様"):
    st.markdown(
        """
        ### 置換仕様

        このアプリは、**元の文章**を基準にして一括置換します。

        例えば、次のルールがあるとします。

        | 元の単語 | 修正後の単語 |
        |---|---|
        | 学校 | 病院 |
        | 病院 | 墓地 |

        元の文章が「学校」だった場合、結果は「病院」です。  
        「病院」にさらに置換がかかって「墓地」になることはありません。

        つまり、置換結果に対して再置換するのではなく、
        あくまで最初の元文章だけを見て変換します。
        """
    )
