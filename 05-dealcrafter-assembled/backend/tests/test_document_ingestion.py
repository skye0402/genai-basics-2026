"""
Tests for document ingestion service.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from pathlib import Path
from app.services.document_ingestion import DocumentIngestionService


@pytest.fixture
def mock_llm():
    """Create a mock LLM."""
    mock = Mock()
    mock.ainvoke = AsyncMock(return_value=Mock(content='{"summary": "Test summary", "keywords": ["test", "document"], "hypothetical_questions": ["What is this about?"]}'))
    return mock


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    mock = Mock()
    mock.add_documents = Mock()
    mock.similarity_search = Mock(return_value=[])
    return mock


@pytest.fixture
def service(mock_llm, mock_vector_store):
    """Create document ingestion service with mocks."""
    service = DocumentIngestionService()
    service._enrichment_llm = mock_llm
    service._vector_store = mock_vector_store
    return service


@pytest.fixture
def sample_text_file(tmp_path):
    """Create a sample text file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test document about financial analysis and revenue projections.")
    return file_path


class TestDocumentIngestionService:
    """Test document ingestion service."""
    
    @pytest.mark.asyncio
    async def test_enrich_chunk_metadata(self, service, mock_llm):
        """Test metadata enrichment."""
        text = "This is a test document about financial analysis."
        base_metadata = {"document_id": "test_doc"}
        
        enriched = await service._enrich_chunk_metadata(text, base_metadata)
        
        assert "document_id" in enriched
        assert "summary" in enriched
        assert "keywords" in enriched
        assert isinstance(enriched["keywords"], list)
    
    @pytest.mark.asyncio
    async def test_process_single_document(self, service, mock_vector_store, sample_text_file):
        """Test processing a single document."""
        result = await service.ingest_document(
            file_path=sample_text_file,
            tenant_id="test-tenant"
        )
        
        assert result["success"] is True
        assert result["chunks_created"] > 0
        assert result["tenant_id"] == "test-tenant"
        assert "document_id" in result
        mock_vector_store.add_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_multiple_documents(self, service, mock_vector_store, tmp_path):
        """Test processing multiple documents."""
        file1 = tmp_path / "doc1.txt"
        file1.write_text("First document about revenue.")
        file2 = tmp_path / "doc2.txt"
        file2.write_text("Second document about expenses.")
        
        results = await service.ingest_documents(
            file_paths=[file1, file2],
            tenant_id="test-tenant"
        )
        
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert mock_vector_store.add_documents.call_count == 2
    
    @pytest.mark.asyncio
    async def test_metadata_enrichment_disabled(self, service, sample_text_file):
        """Test ingestion with enrichment disabled."""
        from app.core.config import settings
        original_setting = settings.enable_metadata_enrichment
        settings.enable_metadata_enrichment = False
        
        try:
            result = await service.ingest_document(
                file_path=sample_text_file,
                tenant_id="test-tenant"
            )
            
            assert result["success"] is True
        finally:
            settings.enable_metadata_enrichment = original_setting
    
    @pytest.mark.asyncio
    async def test_chunk_creation(self, service, tmp_path):
        """Test that documents are properly chunked."""
        # Create a longer document that will require chunking
        content = " ".join(["This is sentence number {}.".format(i) for i in range(100)])
        file_path = tmp_path / "long.txt"
        file_path.write_text(content)
        
        result = await service.ingest_document(
            file_path=file_path,
            tenant_id="test-tenant"
        )
        
        assert result["success"] is True
        assert result["chunks_created"] > 1  # Should create multiple chunks
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(self, service, mock_vector_store, sample_text_file):
        """Test that tenant_id is properly added to metadata."""
        tenant_id = "tenant-123"
        
        await service.ingest_document(
            file_path=sample_text_file,
            tenant_id=tenant_id
        )
        
        # Verify the vector store was called with documents containing tenant_id
        call_args = mock_vector_store.add_documents.call_args
        documents = call_args[0][0]
        
        for doc in documents:
            assert doc.metadata["tenant_id"] == tenant_id
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for invalid file."""
        invalid_path = Path("/nonexistent/file.txt")
        
        with pytest.raises(Exception):
            await service.ingest_document(
                file_path=invalid_path,
                tenant_id="test-tenant"
            )
    
    @pytest.mark.asyncio
    async def test_structural_metadata_preservation(self, service, mock_vector_store, sample_text_file):
        """Test that custom metadata is preserved in chunks."""
        custom_metadata = {
            "author": "Finance Team",
            "department": "CFO",
            "year": 2024
        }
        
        await service.ingest_document(
            file_path=sample_text_file,
            document_metadata=custom_metadata,
            tenant_id="test-tenant"
        )
        
        # Verify custom metadata is in the documents
        call_args = mock_vector_store.add_documents.call_args
        documents = call_args[0][0]
        
        for doc in documents:
            assert doc.metadata["author"] == "Finance Team"
            assert doc.metadata["department"] == "CFO"
            assert doc.metadata["year"] == 2024
    
    @pytest.mark.asyncio
    async def test_document_type_inference(self, service):
        """Test document type inference from file extension."""
        test_cases = [
            (Path("test.pdf"), "pdf_document"),
            (Path("test.txt"), "text_document"),
            (Path("test.md"), "markdown_document"),
            (Path("test.unknown"), "unknown"),
        ]
        
        for file_path, expected_type in test_cases:
            inferred_type = service._infer_document_type(file_path)
            assert inferred_type == expected_type
