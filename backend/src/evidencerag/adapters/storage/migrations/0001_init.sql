
-- Enable pgvector for future vector storage and similarity search.
CREATE EXTENSION IF NOT EXISTS vector;


-- Collections contain groups of uploaded documents.
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Documents belong to a collection.
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuidv7(),

    collection_id UUID NOT NULL,

    filename TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    text TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_documents_collection
        FOREIGN KEY (collection_id)
        REFERENCES collections (id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_documents_collection_content_hash
        UNIQUE (collection_id, content_hash)
);
