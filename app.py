import json

import pandas as pd
import streamlit as st

from replacement import apply_replacements, normalize_rules


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

    if "replaced_text" not in st.session_state:
        st.session_state.replaced_text = ""

    if "last_rules_json" not in st.session_state:
        st.session_state.last_rules_json = "{}"


def reset_all() -> None:
    st.session_state.rules = INITIAL_RULES.copy()
    st.session_state.original_text = ""
    st.session_state.replaced_text = ""
    st.session_state.last_rules_json = "{}"


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
    key="rules_editor",
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


# -----------------------------
# 操作ボタン
# -----------------------------
col1, col2, col3 = st.columns([1.5, 1, 4])

with col1:
    replace_clicked = st.button(
        "一括置換",
        type="primary",
        use_container_width=True,
    )

with col2:
    reset_clicked = st.button(
        "リセット",
        use_container_width=True,
    )

if reset_clicked:
    reset_all()
    st.rerun()


# -----------------------------
# 一括置換処理
# -----------------------------
if replace_clicked:
    st.session_state.original_text = original_text
    st.session_state.rules = edited_rows

    rules, warnings = normalize_rules(edited_rows)

    for warning in warnings:
        st.warning(warning)

    st.session_state.replaced_text = apply_replacements(
        original_text=original_text,
        rules=rules,
    )

    st.session_state.last_rules_json = json.dumps(
        rules,
        ensure_ascii=False,
        indent=2,
    )

    st.success("一括置換しました。")


# -----------------------------
# 修正後の文章
# -----------------------------
st.subheader("修正後の文章")

st.text_area(
    label="置換結果",
    value=st.session_state.replaced_text,
    height=260,
)


# -----------------------------
# ダウンロード
# -----------------------------
download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        label="修正後の文章をダウンロード",
        data=st.session_state.replaced_text,
        file_name="kaidan_replaced.txt",
        mime="text/plain",
        use_container_width=True,
    )

with download_col2:
    st.download_button(
        label="置換ルールをJSONでダウンロード",
        data=st.session_state.last_rules_json,
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
