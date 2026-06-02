import re
from collections import OrderedDict
from typing import Iterable


def normalize_rules(rows: Iterable[dict]) -> tuple[dict[str, str], list[str]]:
    """
    置換ルールを正規化する。

    - 空の「元の単語」は無視
    - 同じ「元の単語」が複数ある場合は、後勝ち
    - 返り値:
        rules: {"元の単語": "修正後の単語"}
        warnings: UIに表示する注意文
    """
    rules = OrderedDict()
    warnings = []

    for i, row in enumerate(rows, start=1):
        src = str(row.get("元の単語", "")).strip()
        dst = str(row.get("修正後の単語", ""))

        if not src:
            continue

        if src in rules:
            warnings.append(f"{i}行目: 「{src}」のルールが重複しています。後の指定を優先しました。")

        rules[src] = dst

    return dict(rules), warnings


def apply_replacements(original_text: str, rules: dict[str, str]) -> str:
    """
    元の文章に対して、一括置換を行う。

    重要:
    置換後の文章に対して再度置換しない。
    そのため、以下のような連鎖置換は起きない。

    例:
        元文: A
        ルール:
            A -> B
            B -> C
        結果:
            B

    また、重なりうる語は長いものを優先する。
    例:
        学校 -> 校舎
        学校の怪談 -> 教室の噂
    の場合、「学校の怪談」を先に判定する。
    """
    if not original_text or not rules:
        return original_text

    # 長い語を先にすることで、部分一致より全体一致を優先する
    sorted_sources = sorted(rules.keys(), key=len, reverse=True)

    pattern = re.compile("|".join(re.escape(src) for src in sorted_sources))

    return pattern.sub(lambda match: rules[match.group(0)], original_text)


def count_matches(original_text: str, rules: dict[str, str]) -> dict[str, int]:
    """
    各「元の単語」が元の文章に何回出てくるか数える。
    """
    result = {}

    for src in rules:
        if not src:
            continue
        result[src] = len(re.findall(re.escape(src), original_text))

    return result
