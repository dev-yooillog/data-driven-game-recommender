import pandas as pd
import numpy as np


def get_user_profile(df: pd.DataFrame, user_genre: str, user_platform: str) -> dict:
    return {
        "preferred_genre": user_genre,
        "platform": user_platform,
    }

# 동일 장르 내 composite_score 상위 20% 필터 후 정렬
def recommend_by_genre(df: pd.DataFrame, genre: str, top_n: int = 10) -> pd.DataFrame:
    genre_df = df[df["genre"] == genre].copy()
    threshold = genre_df["composite_score"].quantile(0.8)
    filtered = genre_df[genre_df["composite_score"] >= threshold]
    return filtered.sort_values("composite_score", ascending=False).head(top_n)


def recommend_by_platform(df: pd.DataFrame, platform: str, genre: str, top_n: int = 10) -> pd.DataFrame:
    return (
        df[(df["platform"] == platform) & (df["genre"] == genre)]
        .sort_values("composite_score", ascending=False)
        .head(top_n)
    )


def inject_hidden_gems(recommendations: pd.DataFrame, hidden_gems: pd.DataFrame,
                       inject_ratio: float = 0.1) -> pd.DataFrame:
# 추천 목록의 inject_ratio 비율만큼 숨겨진 보석으로 교체.
# 다양성 확보 및 롱테일 매출 기여 가설 검증용.
    n_inject = max(1, int(len(recommendations) * inject_ratio))

    already_recommended = recommendations["game_id"].values
    gems_pool = hidden_gems[~hidden_gems["game_id"].isin(already_recommended)]

    gems_sample = gems_pool.sample(n=min(n_inject, len(gems_pool)), random_state=42)

    result = pd.concat([
        recommendations.iloc[:-n_inject],
        gems_sample
    ], ignore_index=True)

    return result


def build_recommendation_list(df: pd.DataFrame, hidden_gems: pd.DataFrame,
                               user_genre: str, user_platform: str,
                               top_n: int = 10, inject_ratio: float = 0.1) -> pd.DataFrame:
    step1 = recommend_by_genre(df, user_genre, top_n)
    step2 = recommend_by_platform(df, user_platform, user_genre, top_n)

    combined = pd.concat([step1, step2]).drop_duplicates(subset="game_id")
    combined = combined.sort_values("composite_score", ascending=False).head(top_n)

    final = inject_hidden_gems(combined, hidden_gems, inject_ratio)
    return final