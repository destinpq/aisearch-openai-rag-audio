#!/usr/bin/env python3
"""
Test client for the PDF processing endpoint.
This script demonstrates how to use the /process-pdf endpoint.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pdf_test_client")

async def process_pdf(pdf_path: Path, server_url: str) -> dict:
    """
    Send a PDF file to the processing endpoint and return the response.
    
    Args:
        pdf_path: Path to the PDF file
        server_url: URL of the server
        
    Returns:
        dict: The response from the server
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    endpoint = f"{server_url}/process-pdf"
    logger.info(f"Sending PDF to {endpoint}")
    
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file',
                      open(pdf_path, 'rb'),
                      filename=pdf_path.name,
                      content_type='application/pdf')
        
        async with session.post(endpoint, data=data) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Error: {response.status} - {error_text}")
                return {"error": f"Server returned status {response.status}", "details": error_text}
                
            result = await response.json()
            return result

def save_results(results: dict, output_path: Path) -> None:
    """
    Save the results to a JSON file.
    
    Args:
        results: The results to save
        output_path: Path to save the results to
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_path}")

async def main():
    parser = argparse.ArgumentParser(description="Test client for PDF processing endpoint")
    parser.add_argument("pdf_file", type=Path, help="Path to the PDF file to process")
    parser.add_argument("--server", type=str, default="http://localhost:8765",
                       help="URL of the server (default: http://localhost:8765)")
    parser.add_argument("--output", type=Path, default=None,
                       help="Path to save the results (default: <pdf_name>_results.json)")
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if args.output is None:
        args.output = args.pdf_file.with_name(f"{args.pdf_file.stem}_results.json")
    
    try:
        logger.info(f"Processing PDF: {args.pdf_file}")
        results = await process_pdf(args.pdf_file, args.server)
        
        # Print summary
        if "error" in results:
            logger.error(f"Error processing PDF: {results['error']}")
            return 1
            
        chunks = results.get("chunks", [])
        logger.info(f"Successfully processed PDF into {len(chunks)} chunks")
        
        # Print first few chunks as preview
        if chunks:
            logger.info("Preview of first 3 chunks:")
            for i, chunk in enumerate(chunks[:3]):
                logger.info(f"  Chunk {i+1}: '{chunk['title']}'")
                content_preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
                logger.info(f"    Content: {content_preview}")
        
        # Save results
        save_results(results, args.output)
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 