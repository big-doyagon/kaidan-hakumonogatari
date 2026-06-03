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
col1, col2, col3, col4 = st.columns([1.2, 1.2, 1, 3.6])

with col1:
    replace_clicked = st.button(
        "一括置換",
        type="primary",
        use_container_width=True,
    )

with col2:
    add_clicked = st.button(
        "＋追加",
        use_container_width=True,
    )

with col3:
    reset_clicked = st.button(
        "リセット",
        use_container_width=True,
    )

if add_clicked:
    st.session_state.original_text = original_text
    st.session_state.rules = edited_rows
    st.session_state.rules.append({"元の単語": "", "修正後の単語": ""})
    st.rerun()

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
