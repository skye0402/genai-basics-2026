/**
 * REST API routes for document management
 * 
 * These endpoints are for applications to upload, delete, and manage documents.
 * They are NOT MCP tools - MCP tools are only for LLM to retrieve information.
 */

import { Router, Request, Response } from 'express';
import multer from 'multer';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { getDocumentIngestionService } from '../services/documentIngestionService.js';
import { logInfo, logError } from '../utils/logger.js';
import {
  createJob,
  getJob,
  subscribeToJob,
  JobState,
} from '../services/ingestionJobManager.js';

const router = Router();

// Configure multer for file uploads
const upload = multer({
  dest: os.tmpdir(),
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedExtensions = ['.pdf', '.txt', '.md', '.docx'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedExtensions.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${ext}. Allowed: ${allowedExtensions.join(', ')}`));
    }
  },
});

/**
 * POST /api/documents/upload
 * Upload and ingest one or more documents into HANA Cloud Vector Store
 */
router.post('/upload', upload.array('files', 10), async (req: Request, res: Response) => {
  const files = req.files as Express.Multer.File[];
  const metadata = req.body.metadata ? JSON.parse(req.body.metadata) : undefined;

  const service = getDocumentIngestionService();
  const tenantId = service.getDefaultTenantId();

  logInfo(`Document upload request: ${files?.length || 0} file(s), tenant_id: ${tenantId}`);

  if (!files || files.length === 0) {
    return res.status(400).json({
      success: false,
      error: 'No files provided',
    });
  }

  const jobs: JobState[] = [];

  try {
    await Promise.all(
      files.map(async (file) => {
        const ext = path.extname(file.originalname);
        const newPath = `${file.path}${ext}`;
        await fs.rename(file.path, newPath);

        const job = createJob({ filename: file.originalname, tenantId });
        jobs.push(job);

        const startTime = new Date();

        const perFileMetadata = {
          ...(metadata || {}),
          source_filename: file.originalname,
          original_filename: file.originalname,
        };

        service
          .ingestDocument(newPath, perFileMetadata, tenantId, job.jobId)
          .then((result) => {
            logInfo(
              `Ingestion completed for ${file.originalname} (job ${job.jobId}) with ${result.chunks_created} chunks in ${Date.now() - startTime.getTime()} ms`
            );
          })
          .catch((error) => {
            logError(`Failed to ingest ${file.originalname} (job ${job.jobId})`, error);
          })
          .finally(async () => {
            await fs.unlink(newPath).catch(() => {});
          });
      })
    );

    return res.status(202).json({
      success: true,
      message: `Accepted ${jobs.length} document(s) for ingestion`,
      jobs: jobs.map((job) => ({
        job_id: job.jobId,
        filename: job.filename,
        status: job.status,
        stage: job.stage,
        total_chunks: job.totalChunks,
        processed_chunks: job.processedChunks,
        created_at: job.createdAt,
      })),
    });
  } catch (error) {
    logError('Document upload failed', error);
    return res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * GET /api/documents
 * Returns summary information about ingested documents
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const service = getDocumentIngestionService();
    const tenantId = service.getDefaultTenantId();
    const documents = await service.listDocuments(tenantId);

    return res.status(200).json({
      success: true,
      documents,
    });
  } catch (error) {
    logError('Failed to list documents', error);
    return res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * DELETE /api/documents/:documentId
 * Deletes all chunks belonging to a specific document
 */
router.delete('/:documentId', async (req: Request, res: Response) => {
  const { documentId } = req.params;

  if (!documentId) {
    return res.status(400).json({
      success: false,
      error: 'documentId is required',
    });
  }

  try {
    const service = getDocumentIngestionService();
    const tenantId = service.getDefaultTenantId();
    const result = await service.deleteDocument(documentId, tenantId);

    return res.status(200).json({
      success: true,
      ...result,
    });
  } catch (error) {
    logError(`Failed to delete document ${documentId}`, error);
    const message = error instanceof Error ? error.message : String(error);
    const status = message.includes('not found') ? 404 : 500;
    return res.status(status).json({
      success: false,
      error: message,
    });
  }
});

/**
 * GET /api/documents/progress/:jobId
 * Returns current progress for a job
 */
router.get('/progress/:jobId', (req: Request, res: Response) => {
  const { jobId } = req.params;
  const job = getJob(jobId);

  if (!job) {
    return res.status(404).json({
      success: false,
      error: `Job ${jobId} not found`,
    });
  }

  return res.status(200).json({
    success: true,
    job,
  });
});

/**
 * GET /api/documents/progress/:jobId/stream
 * Streams job progress updates using Server-Sent Events
 */
router.get('/progress/:jobId/stream', (req: Request, res: Response) => {
  const { jobId } = req.params;
  const job = getJob(jobId);

  if (!job) {
    return res.status(404).json({
      success: false,
      error: `Job ${jobId} not found`,
    });
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache, no-transform',
    Connection: 'keep-alive',
  });

  res.write(`data: ${JSON.stringify(job)}\n\n`);

  const unsubscribe = subscribeToJob(jobId, (state) => {
    res.write(`data: ${JSON.stringify(state)}\n\n`);

    if (state.status === 'completed' || state.status === 'failed') {
      unsubscribe();
      res.write(`event: done\n`);
      res.write(`data: ${JSON.stringify({ job_id: jobId })}\n\n`);
      res.end();
    }
  });

  req.on('close', () => {
    unsubscribe();
  });
});

/**
 * POST /api/documents/search
 * Search for documents (also available as MCP tool for LLM)
 */
router.post('/search', async (req: Request, res: Response) => {
  const { query, k = 4, document_ids, document_names } = req.body as {
    query?: string;
    k?: number;
    document_ids?: string[];
    document_names?: string[];
  };

  if (!query) {
    return res.status(400).json({
      success: false,
      error: 'Query parameter is required',
    });
  }

  logInfo(
    `Document search request: query="${query}", k=${k}, document_ids=${
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
      score: doc.metadata.score,
    }));

    return res.status(200).json({
      success: true,
      query,
      count: results.length,
      results: formattedResults,
    });
  } catch (error) {
    logError('Document search failed', error);
    return res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

export default router;
