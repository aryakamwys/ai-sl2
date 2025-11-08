"""
AI recommendation endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import (
    QueryRequest,
    AIResponse,
    RetrievalResult,
    PerplexityRequest,
    PerplexityResponse,
    ErrorResponse
)
from app.services.gemini_client import gemini_client
from app.services.perplexity_client import perplexity_client
from app.services.rag_engine import rag_engine
from app.services.sheets_reader import sheets_reader
from app.core.logger import logger

router = APIRouter()


@router.post("/query", response_model=AIResponse)
async def ai_query(request: QueryRequest):
    """
    Main AI query endpoint using RAG
    Retrieves relevant documents and generates AI response
    """
    try:
        logger.info(f"Received AI query: {request.query}")
        
        # Initialize RAG if not already done
        if not rag_engine.documents:
            logger.info("Initializing RAG with Google Sheets data...")
            sheet_data = sheets_reader.get_all_text()
            
            # Split into chunks (simple line-based splitting)
            documents = [line.strip() for line in sheet_data.split('\n') if line.strip()]
            rag_engine.index_documents(documents)
        
        # Retrieve relevant documents
        retrieved = rag_engine.retrieve(request.query, top_k=request.top_k)
        
        # Format retrieved documents
        retrieved_docs = [
            RetrievalResult(
                content=doc,
                score=score,
                metadata={"rank": i + 1}
            )
            for i, (doc, score) in enumerate(retrieved)
        ]
        
        # Generate AI response using Gemini with RAG
        doc_contents = [doc.content for doc in retrieved_docs]
        answer = gemini_client.generate_with_rag(
            query=request.query,
            retrieved_docs=doc_contents
        )
        
        # Calculate average confidence
        avg_confidence = sum(doc.score for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0.0
        
        return AIResponse(
            query=request.query,
            answer=answer,
            retrieved_docs=retrieved_docs,
            confidence=avg_confidence,
            source="gemini"
        )
        
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/perplexity", response_model=PerplexityResponse)
async def perplexity_query(request: PerplexityRequest):
    """
    Query using Perplexity AI
    """
    try:
        logger.info(f"Received Perplexity query: {request.query}")
        
        result = await perplexity_client.query(
            prompt=request.query,
            context=request.context
        )
        
        return PerplexityResponse(
            query=request.query,
            answer=result["answer"],
            sources=result.get("sources")
        )
        
    except Exception as e:
        logger.error(f"Error processing Perplexity query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex")
async def reindex_documents():
    """
    Reindex documents from Google Sheets
    """
    try:
        logger.info("Reindexing documents...")
        
        # Clear existing index
        rag_engine.clear_index()
        
        # Get fresh data from sheets
        sheet_data = sheets_reader.get_all_text()
        
        # Split into chunks
        documents = [line.strip() for line in sheet_data.split('\n') if line.strip()]
        
        # Reindex
        rag_engine.index_documents(documents)
        
        return {
            "status": "success",
            "message": f"Reindexed {len(documents)} documents",
            "document_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error reindexing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get RAG engine statistics
    """
    return {
        "indexed_documents": len(rag_engine.documents),
        "model": rag_engine.model.get_sentence_embedding_dimension() if rag_engine.model else None,
        "index_size": rag_engine.index.ntotal if rag_engine.index else 0
    }

