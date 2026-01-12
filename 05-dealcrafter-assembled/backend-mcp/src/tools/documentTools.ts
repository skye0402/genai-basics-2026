/**
 * MCP tools for document search using HANA Cloud Vector Store
 * 
 * Note: Document upload/deletion are REST API endpoints, not MCP tools.
 * MCP tools are for LLM to retrieve information during conversations.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { getDocumentIngestionService } from '../services/documentIngestionService.js';
import { imageStorageService } from '../services/imageStorageService.js';
import { logInfo } from '../utils/logger.js';

/**
 * Register document search tool (for LLM to retrieve context during conversations)
 */
export function registerDocumentSearchTool(server: McpServer): void {

  // 1) Header-level document search: operate only on summaries in the header table
  //    Returns document metadata including document_id, title, and summary.
  server.tool(
    'search_document_headers',
    'Search documents at the header level using their LLM-generated summaries. Use this to discover which documents are relevant and obtain their document_ids, titles, and summaries before doing detailed content retrieval.',
    {
      query: z.string().describe('Search query text'),
      k: z
        .number()
        .optional()
        .default(5)
        .describe('Number of documents to retrieve based on header summaries (default: 5)'),
    },
    async ({ query, k }) => {
      logInfo(`Tool: search_document_headers | query: ${query}, k: ${k}`);

      try {
        const service = getDocumentIngestionService();
        const tenantId = service.getDefaultTenantId();
        const documents = await service.searchDocumentsByHeader(query, tenantId, k);

        const formatted = documents.map((doc, idx) => ({
          rank: idx + 1,
          document: doc,
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: true,
                  query,
                  document_count: documents.length,
                  results: formatted,
                },
                null,
                2,
              ),
            },
          ],
        };
      } catch (error) {
        console.error('Header document search failed:', error);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error: error instanceof Error ? error.message : String(error),
                },
                null,
                2,
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // 2) Content-level search: search within document chunks, optionally filtered by document_ids
  server.tool(
    'search_document_content',
    'Search within document content chunks using semantic similarity. Use this to retrieve specific passages from documents. Optionally provide document_ids (from a header search) to restrict the search to particular documents. E.g. ["f66d867e225e3ca91142d3476ad93d69", "c76d867e225e3ca91142d3476ad93d69", ...] and/or document names/ titles or filenames in parameter "document_names" like ["ABC-Bank- 2024-External.docx", "Banking Expense Policies", ...]',
    {
      query: z.string().describe('Search query text'),
      k: z
        .number()
        .optional()
        .default(4)
        .describe('Number of chunks to return (default: 4)'),
      document_ids: z
        .array(z.string())
        .optional()
        .describe('Optional list of document IDs to restrict the search to specific documents'),
      document_names: z
        .array(z.string())
        .optional()
        .describe('Optional list of document names (filenames) to restrict the search when IDs are not available'),
    },
    async ({ query, k, document_ids, document_names }) => {
      logInfo(
        `Tool: search_document_content | query: ${query}, k: ${k}, document_ids=${
          Array.isArray(document_ids) ? document_ids.join(',') : '[]'
        }, document_names=${Array.isArray(document_names) ? document_names.join(',') : '[]'}`,
      );

      try {
        const service = getDocumentIngestionService();
        const tenantId = service.getDefaultTenantId();
        const results = await service.searchDocuments(query, tenantId, k, document_ids, document_names);

        const formattedResults = results.map((doc, idx) => ({
          rank: idx + 1,
          content: doc.pageContent,
          metadata: doc.metadata,
          score: (doc.metadata as any)?.score,
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: true,
                  query,
                  count: results.length,
                  results: formattedResults,
                },
                null,
                2,
              ),
            },
          ],
        };
      } catch (error) {
        console.error('Document content search failed:', error);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error:
                    error instanceof Error ? error.message : String(error),
                },
                null,
                2,
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  server.tool(
    'get_document_segment',
    'Retrieve a specific part of a document by document_id and either chunk_index (0-based, 0 = first chunk) or page_number (1-based). Use this when you want to retrieve additional context adjacent to a document chunk or page.',
    {
      document_id: z.string().describe('Document ID to retrieve from'),
      chunk_index: z
        .number()
        .int()
        .optional()
        .describe('0-based chunk index within the document (0 = first chunk). Use this when pages are not meaningful (e.g. docx).'),
      page_number: z
        .number()
        .int()
        .optional()
        .describe('1-based page number within the document. Returns all chunks for that page.'),
    },
    async ({ document_id, chunk_index, page_number }) => {
      logInfo(
        `Tool: get_document_segment | document_id=${document_id}, chunk_index=${
          chunk_index ?? 'null'
        }, page_number=${page_number ?? 'null'}`,
      );

      if ((chunk_index == null && page_number == null) || (chunk_index != null && page_number != null)) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error:
                    'You must provide exactly one of chunk_index or page_number (but not both).',
                },
                null,
                2,
              ),
            },
          ],
          isError: true,
        };
      }

      try {
        const service = getDocumentIngestionService();
        const tenantId = service.getDefaultTenantId();
        const segments = await service.getDocumentSegments(
          document_id,
          { chunkIndex: chunk_index ?? undefined, pageNumber: page_number ?? undefined },
          tenantId,
        );

        const formatted = segments.map((doc, idx) => ({
          index: idx,
          content: doc.pageContent,
          metadata: doc.metadata,
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: true,
                  document_id,
                  chunk_index,
                  page_number,
                  segment_count: segments.length,
                  segments: formatted,
                },
                null,
                2,
              ),
            },
          ],
        };
      } catch (error) {
        console.error('get_document_segment failed:', error);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error: error instanceof Error ? error.message : String(error),
                },
                null,
                2,
              ),
            },
          ],
          isError: true,
        };
      }
    },
  );

  // 4) Get document images: retrieve image metadata for a document
  //    Allows LLM to discover and reference images in responses
  server.tool(
    'get_document_images',
    'Get metadata for all images extracted from a document. Returns image IDs, descriptions, page numbers, and dimensions. Use this to discover relevant images that can be included in your response. To display an image, use markdown syntax: ![description](image:imageId)',
    {
      document_id: z.string().describe('Document ID to get images for'),
      page_number: z
        .number()
        .int()
        .optional()
        .describe('Optional: filter to images from a specific page (1-based)'),
    },
    async ({ document_id, page_number }) => {
      logInfo(
        `Tool: get_document_images | document_id=${document_id}, page_number=${page_number ?? 'all'}`,
      );

      try {
        const images = await imageStorageService.listImagesForDocument(document_id);
        
        // Filter by page if specified
        const filtered = page_number 
          ? images.filter(img => img.pageNumber === page_number)
          : images;

        const formatted = filtered.map((img) => ({
          image_id: img.imageId,
          page_number: img.pageNumber,
          description: img.description,
          width: img.width,
          height: img.height,
          mime_type: img.mimeType,
          // Include markdown syntax hint for easy copy-paste
          markdown_syntax: `![${img.description?.slice(0, 50) || 'Image'}](image:${img.imageId})`,
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: true,
                  document_id,
                  image_count: formatted.length,
                  images: formatted,
                  usage_hint: 'To display an image in your response, use: ![description](image:imageId)',
                },
                null,
                2,
              ),
            },
          ],
        };
      } catch (error) {
        console.error('get_document_images failed:', error);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  success: false,
                  error: error instanceof Error ? error.message : String(error),
                },
                null,
                2,
              ),
            },
          ],
          isError: true,
        };
      }
    },
  );
}
