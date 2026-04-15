"""
join_key_resolver.py — Strip ID prefixes and normalize join keys across DAB databases.

Usage:
    from utils.join_key_resolver import resolve_join_keys
    merged = resolve_join_keys(df_business, 'business_id', 'businessid_',
                               df_reviews,  'business_ref', 'businessref_')
"""
import pandas as pd


def strip_prefix(series: pd.Series, prefix: str) -> pd.Series:
    """Strip a known prefix and cast to int. Raises ValueError if prefix not found."""
    sample = series.dropna().iloc[0] if not series.dropna().empty else ''
    if sample and not str(sample).startswith(prefix):
        raise ValueError(f"Expected prefix '{prefix}' not found in: {sample}")
    return series.str.replace(prefix, '', regex=False).astype(int)


def resolve_join_keys(
    left: pd.DataFrame, left_col: str, left_prefix: str,
    right: pd.DataFrame, right_col: str, right_prefix: str,
    how: str = 'inner'
) -> pd.DataFrame:
    """
    Normalize prefixed ID columns and merge two DataFrames on the resolved integer key.

    Solves DAB ill-formatted join key problem (Correction 002):
      businessid_9  <-->  businessref_9  =>  join on integer 9

    Example:
        merged = resolve_join_keys(
            df_business, 'business_id', 'businessid_',
            df_reviews,  'business_ref', 'businessref_'
        )
    """
    left = left.copy()
    right = right.copy()
    left['_join_key'] = strip_prefix(left[left_col], left_prefix)
    right['_join_key'] = strip_prefix(right[right_col], right_prefix)
    merged = pd.merge(left, right, on='_join_key', how=how)
    merged.drop(columns=['_join_key'], inplace=True)
    return merged


if __name__ == '__main__':
    biz = pd.DataFrame({'business_id': ['businessid_1', 'businessid_2'], 'name': ['A', 'B']})
    rev = pd.DataFrame({'business_ref': ['businessref_1', 'businessref_3'], 'rating': [4, 5]})
    result = resolve_join_keys(biz, 'business_id', 'businessid_', rev, 'business_ref', 'businessref_')
    assert len(result) == 1
    assert result.iloc[0]['name'] == 'A'
    assert result.iloc[0]['rating'] == 4
    print('join_key_resolver: PASS')
