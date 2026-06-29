from vector_db.chroma_store import ChromaVectorStore


def test_vector_store_count(tmp_path):
    store = ChromaVectorStore(persist_directory=tmp_path / "vectors")
    assert store.count() == 0
