from enum import Enum


class ProcessingStage(str, Enum):
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    ENRICHING = "enriching"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
