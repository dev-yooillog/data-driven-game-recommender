import pandas as pd
import numpy as np


def load_data(raw_dir: str) -> dict:
    files = ["games", "genre_summary", "platform_summary", "publisher_summary", "yearly_trends"]
    return {f: pd.read_csv(f"{raw_dir}/{f}.csv") for f in files}


def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

# 장르별 중앙값으로 대체
    cleaned["user_score"] = cleaned.groupby("genre")["user_score"].transform(
        lambda x: x.fillna(x.median())
    )

    sales_cols = ["na_sales_million", "eu_sales_million", "jp_sales_million",
                  "other_sales_million", "global_sales_million"]
    for col in sales_cols:
        cleaned[col] = cleaned[col].clip(lower=0)

# 출시연도 범위 필터 <-- 데이터 이상치 제거
    cleaned = cleaned[(cleaned["year"] >= 1985) & (cleaned["year"] <= 2026)]

    return cleaned.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["composite_score"] = df["metacritic_score"] * 0.7 + df["user_score"] * 10 * 0.3

    df["is_hidden_gem"] = (
        (df["metacritic_score"] >= 80) & (df["global_sales_million"] < 5)
    ).astype(int)

    df["has_online_features"] = (
        (df["online_multiplayer"] == 1) | (df["dlc_released"] == 1)
    ).astype(int)

    df["sales_tier"] = pd.cut(
        df["global_sales_million"],
        bins=[0, 1, 5, 20, 50, float("inf")],
        labels=["micro", "niche", "mid", "hit", "blockbuster"]
    )

    return df

def extract_hidden_gems(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["is_hidden_gem"] == 1][
        ["game_id", "title", "genre", "platform", "metacritic_score",
         "user_score", "global_sales_million", "composite_score"]
    ].sort_values("composite_score", ascending=False).reset_index(drop=True)