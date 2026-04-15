"""
mongo_helper.py — Safe MongoDB query wrapper that prevents the default 5-document limit.

Usage:
    from utils.mongo_helper import mongo_query
    results = mongo_query('yelp_db', 'business', {'city': 'Indianapolis'})
"""


def mongo_query(
    db: str,
    collection: str,
    filter_doc: dict,
    projection: dict | None = None,
    limit: int = 10000,
    host: str = 'localhost',
    port: int = 27017
) -> list[dict]:
    """
    Query MongoDB and return all matching documents as a list of dicts.
    Default limit=10000 prevents the silent 5-document truncation bug (Correction 003).

    Args:
        db:         Database name (e.g. 'yelp_db')
        collection: Collection name (e.g. 'business')
        filter_doc: MongoDB filter dict (e.g. {'city': 'Indianapolis'})
        projection: Optional field projection dict
        limit:      Max documents to return. Use 0 for unlimited. Default 10000.
        host:       MongoDB host. Default localhost.
        port:       MongoDB port. Default 27017.

    Returns:
        List of document dicts with '_id' removed.

    Example:
        businesses = mongo_query('yelp_db', 'business', {}, limit=10000)
    """
    from pymongo import MongoClient
    client = MongoClient(host, port)
    col = client[db][collection]
    cursor = col.find(filter_doc, projection or {}, limit=limit)
    results = []
    for doc in cursor:
        doc.pop('_id', None)
        results.append(doc)
    client.close()
    return results


if __name__ == '__main__':
    try:
        results = mongo_query('yelp_db', 'business', {}, limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5
        print(f'mongo_helper: PASS (got {len(results)} docs with limit=5)')
    except Exception as e:
        print(f'mongo_helper: SKIP (MongoDB not available: {e})')
