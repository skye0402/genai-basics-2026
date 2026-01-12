#!/usr/bin/env python3
"""
Test script for real document ingestion into HANA Cloud Vector Store.
This script creates sample documents and tests the ingestion pipeline.

Run with: cd backend && uv run python test_real_ingestion.py
"""
import asyncio
import os
from pathlib import Path

# Create sample documents directory
SAMPLE_DOCS_DIR = Path("sample_documents")
SAMPLE_DOCS_DIR.mkdir(exist_ok=True)


def create_sample_documents():
    """Create sample documents for testing."""
    print("📝 Creating sample documents...")
    
    # Sample 1: SAP Fiori Overview
    doc1_path = SAMPLE_DOCS_DIR / "sap_fiori_overview.txt"
    doc1_path.write_text("""
SAP Fiori Overview

SAP Fiori is SAP's user experience (UX) design approach for creating applications that are simple, intuitive, and consistent across devices. 

Key Features:
- Role-based, personalized user experience
- Responsive design that works on any device
- Simple, intuitive interface
- Consistent user experience across applications

Benefits:
- Increased productivity through simplified processes
- Improved user adoption with modern UX
- Reduced training costs
- Better decision-making with real-time insights

SAP Fiori applications are built using modern web technologies including HTML5, CSS3, and JavaScript.
The framework uses UI5 (SAPUI5 or OpenUI5) as the underlying technology.
""")
    print(f"✓ Created: {doc1_path}")
    
    # Sample 2: Finance Process
    doc2_path = SAMPLE_DOCS_DIR / "finance_process.txt"
    doc2_path.write_text("""
Financial Planning and Analysis Process

Overview:
Financial Planning and Analysis (FP&A) is a critical function that supports strategic planning and performance management.

Key Processes:
1. Budgeting: Annual budget preparation and allocation
2. Forecasting: Rolling forecasts updated quarterly
3. Reporting: Monthly financial reporting and variance analysis
4. Planning: Strategic planning and scenario modeling

Tools and Technologies:
- SAP Analytics Cloud for planning and reporting
- SAP BW for data warehousing
- SAP S/4HANA for financial transactions

Best Practices:
- Use driver-based forecasting models
- Implement rolling forecasts (12-18 months)
- Automate data collection and reporting
- Focus on variance analysis and actionable insights
""")
    print(f"✓ Created: {doc2_path}")
    
    # Sample 3: AI in Finance
    doc3_path = SAMPLE_DOCS_DIR / "ai_in_finance.txt"
    doc3_path.write_text("""
Artificial Intelligence in Finance

AI is transforming the finance industry by automating processes, improving accuracy, and enabling new insights.

Use Cases:
1. Fraud Detection: Real-time anomaly detection in transactions
2. Credit Scoring: AI-powered risk assessment models
3. Process Automation: Automated invoice processing and reconciliation
4. Predictive Analytics: Cash flow forecasting and demand planning
5. Chatbots: AI assistants for finance queries

Technologies:
- Machine Learning for pattern recognition
- Natural Language Processing for document analysis
- Computer Vision for invoice scanning
- Large Language Models for conversational AI

Implementation Considerations:
- Data quality and governance
- Model explainability and compliance
- Integration with existing systems
- Change management and user adoption
""")
    print(f"✓ Created: {doc3_path}")
    
    return [doc1_path, doc2_path, doc3_path]


async def test_ingestion():
    """Test document ingestion with real HANA connection."""
    from app.services.document_ingestion import DocumentIngestionService
    from app.core.config import settings
    
    print("\n🔧 Initializing Document Ingestion Service...")
    print(f"HANA Address: {settings.hana_db_address}")
    print(f"HANA Table: {settings.hana_table}")
    print(f"Using Internal Embeddings: {settings.hana_use_internal_embeddings}")
    print(f"Metadata Enrichment: {settings.enable_metadata_enrichment}")
    
    try:
        service = DocumentIngestionService()
        print("✓ Service initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing service: {e}")
        return
    
    # Create sample documents
    doc_paths = create_sample_documents()
    
    print(f"\n📤 Ingesting {len(doc_paths)} documents...")
    
    # Test ingestion
    for doc_path in doc_paths:
        print(f"\n📄 Processing: {doc_path.name}")
        
        try:
            result = await service.ingest_document(
                file_path=doc_path,
                document_metadata={"document_type": "documentation"},
                tenant_id="test-tenant-001"
            )
            
            print(f"✓ Ingested successfully!")
            print(f"  - Document ID: {result['document_id']}")
            print(f"  - Chunks created: {result['chunks_created']}")
            print(f"  - Processing time: {result['processing_time_seconds']:.2f}s")
            
            if result.get('enriched_metadata'):
                print(f"  - Metadata enrichment: ✓")
            
        except Exception as e:
            print(f"❌ Error ingesting {doc_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🔍 Testing search functionality...")
    
    # Test search
    try:
        search_results = await service.search_documents(
            query="What is SAP Fiori?",
            tenant_id="test-tenant-001",
            k=3
        )
        
        print(f"✓ Search completed!")
        print(f"  - Found {len(search_results)} results")
        
        for i, doc in enumerate(search_results, 1):
            print(f"\n  Result {i}:")
            print(f"    - Document: {doc.metadata.get('source_filename', 'N/A')}")
            print(f"    - Chunk ID: {doc.metadata.get('chunk_id', 'N/A')}")
            print(f"    - Text preview: {doc.page_content[:100]}...")
            
            if doc.metadata.get('summary'):
                print(f"    - Summary: {doc.metadata['summary'][:80]}...")
            
    except Exception as e:
        print(f"❌ Error searching documents: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Testing completed!")
    print("\nNext steps:")
    print("1. Start backend: cd backend && uv run uvicorn app.main:app --reload")
    print("2. Test via API: curl -X POST http://localhost:8000/api/documents/ingest \\")
    print("                      -F 'file=@sample_documents/sap_fiori_overview.txt' \\")
    print("                      -F 'tenant_id=demo-tenant'")


if __name__ == "__main__":
    asyncio.run(test_ingestion())
