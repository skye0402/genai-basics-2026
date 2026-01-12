/**
 * Document ingestion service for HANA Cloud Vector Store.
 * 
 * This service handles:
 * 1. Document upload and parsing
 * 2. Structure-aware chunking
 * 3. Embedding and storage in HANA Cloud Vector Store
 */

import { AzureOpenAiEmbeddingClient, AzureOpenAiChatClient } from '@sap-ai-sdk/langchain';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { Document } from '@langchain/core/documents';
import * as hdb from 'hdb';
import * as fs from 'fs/promises';
import * as path from 'path';
import { updateJob } from './ingestionJobManager.js';

type MammothModule = {
  extractRawText: (options: { buffer: Buffer }) => Promise<{ value?: string }>;
};

let mammothCache: MammothModule | null = null;

async function loadMammoth(): Promise<MammothModule> {
  if (!mammothCache) {
    const mod = await import('mammoth');
    mammothCache = (mod.default || mod) as MammothModule;
  }
  return mammothCache;
}

interface HanaConfig {
  host: string;
  port: number;
  user: string;
  password: string;
}

interface DocumentMetadata {
  document_id: string;
  source_filename: string;
  created_at: string;
  document_type: string;
  tenant_id: string;
  title?: string;
  summary?: string;
  language?: string;
  chunk_id?: string;
  chunk_index?: number;
  total_chunks?: number;
  page_number?: number;
  total_pages?: number;
  source?: string;
  filename?: string;
  [key: string]: any;
}

export interface DocumentSummary {
  document_id: string;
  filename: string;
  document_type: string;
  tenant_id: string;
  total_pages: number;
  chunk_count: number;
  created_at: string;
  title?: string;
  summary?: string;
  score?: number;
}

interface IngestionResult {
  success: boolean;
  document_id: string;
  filename: string;
  chunks_created: number;
  tenant_id: string;
  timestamp: string;
  error?: string;
}

export class DocumentIngestionService {
  private hanaClient: any = null;
  private embeddingClient: AzureOpenAiEmbeddingClient | null = null;
  private textSplitter: RecursiveCharacterTextSplitter | null = null;
  private metadataClient: AzureOpenAiChatClient | null = null;

  private readonly config: {
    hana: HanaConfig;
    vectorTableName: string;
    headerTableName: string;
    chunkSize: number;
    chunkOverlap: number;
    summaryInputMaxPages: number;
    summaryInputMaxChars: number;
    embeddingBatchSize: number;
    defaultTenantId: string;
    embeddingModel: string;
    metadataModel: string;
    resourceGroup: string;
  };

  constructor() {
    this.config = {
      hana: {
        host: process.env.HANA_DB_ADDRESS || '',
        port: parseInt(process.env.HANA_DB_PORT || '443', 10),
        user: process.env.HANA_DB_USER || '',
        password: process.env.HANA_DB_PASSWORD || '',
      },
      vectorTableName: process.env.HANA_VECTOR_TABLE || 'LANGCHAIN_DEMO_DOCS',
      headerTableName: process.env.HANA_HEADER_TABLE || 'LANGCHAIN_DEMO_DOCS_HEADER',
      chunkSize: parseInt(process.env.CHUNK_SIZE || '2000', 10),
      chunkOverlap: parseInt(process.env.CHUNK_OVERLAP || '200', 10),
      summaryInputMaxPages: parseInt(process.env.SUMMARY_INPUT_MAX_PAGES || '3', 10),
      summaryInputMaxChars: parseInt(process.env.SUMMARY_INPUT_MAX_CHARS || '4000', 10),
      embeddingBatchSize: parseInt(process.env.EMBEDDING_BATCH_SIZE || '16', 10),
      defaultTenantId: process.env.DEFAULT_TENANT_ID || 'default-tenant',
      embeddingModel: process.env.EMBEDDING_MODEL || 'text-embedding-3-small',
      metadataModel: process.env.METADATA_MODEL || 'gpt-4.1',
      resourceGroup: process.env.SAP_AI_RESOURCE_GROUP || 'default',
    };
  }

  /**
   * Initialize HANA database connection
   */
  private async initHanaConnection(): Promise<void> {
    if (this.hanaClient) {
      return;
    }

    return new Promise((resolve, reject) => {
      this.hanaClient = hdb.createClient({
        host: this.config.hana.host,
        port: this.config.hana.port,
        user: this.config.hana.user,
        password: this.config.hana.password,
      });

      this.hanaClient.connect((err: Error) => {
        if (err) {
          console.error('Failed to connect to HANA:', err);
          reject(err);
        } else {
          console.log('✅ Connected to HANA Cloud');
          resolve();
        }
      });
    });
  }

  /**
   * Get or initialize the embedding client
   */
  private getEmbeddingClient(): AzureOpenAiEmbeddingClient {
    if (!this.embeddingClient) {
      console.log(`Initializing embedding client with model: ${this.config.embeddingModel}`);
      this.embeddingClient = new AzureOpenAiEmbeddingClient({
        modelName: this.config.embeddingModel, resourceGroup: this.config.resourceGroup
      });
    }
    return this.embeddingClient;
  }

  /**
   * Get or initialize the metadata LLM client
   */
  private getMetadataClient(): AzureOpenAiChatClient {
    if (!this.metadataClient) {
      console.log(`Initializing metadata LLM client with model: ${this.config.metadataModel}`);
      this.metadataClient = new AzureOpenAiChatClient({
        modelName: this.config.metadataModel,
        resourceGroup: this.config.resourceGroup,
        temperature: 0.2,
        max_tokens: 1024,
      });
    }
    return this.metadataClient;
  }

  /**
   * Get or initialize the text splitter
   */
  private getTextSplitter(): RecursiveCharacterTextSplitter {
    if (!this.textSplitter) {
      this.textSplitter = new RecursiveCharacterTextSplitter({
        chunkSize: this.config.chunkSize,
        chunkOverlap: this.config.chunkOverlap,
      });
    }
    return this.textSplitter;
  }

  /**
   * Load document from file path
   */
  private async loadDocument(filePath: string): Promise<Document[]> {
    const ext = path.extname(filePath).toLowerCase();
    switch (ext) {
      case '.pdf':
        return this.loadPdfDocument(filePath);
      case '.docx':
        return this.loadDocxDocument(filePath);
      default:
        return this.loadTextDocument(filePath);
    }
  }

  private async loadPdfDocument(filePath: string): Promise<Document[]> {
    const buffer = await fs.readFile(filePath);
    const filename = path.basename(filePath);

    // pdf-parse v2 uses class-based API
    const { PDFParse } = await import('pdf-parse');
    const parser = new PDFParse({ data: buffer });
    
    try {
      const textResult = await parser.getText();
      const infoResult = await parser.getInfo();
      
      const totalPages = infoResult.total || 1;
      const rawPages = (textResult.text || '').split('\f');

      const pageDocuments = rawPages
        .map((pageContent: string, index: number) => {
          const cleanedContent = pageContent.replace(/\r\n/g, '\n').trim();
          return new Document({
            pageContent: cleanedContent,
            metadata: {
              source: filePath,
              filename,
              page_number: index + 1,
              total_pages: totalPages,
            },
          });
        })
        .filter((doc: Document) => doc.pageContent.length > 0);

      if (pageDocuments.length > 0) {
        return pageDocuments;
      }

      const fallbackText = (textResult.text || '').trim();
      if (!fallbackText) {
        throw new Error(`PDF document ${filename} did not contain extractable text`);
      }

      return [
        new Document({
          pageContent: fallbackText,
          metadata: {
            source: filePath,
            filename,
            page_number: 1,
            total_pages: 1,
          },
        }),
      ];
    } finally {
      await parser.destroy();
    }
  }

  private async loadDocxDocument(filePath: string): Promise<Document[]> {
    const buffer = await fs.readFile(filePath);
    const mammoth = await loadMammoth();
    const result = await mammoth.extractRawText({ buffer });
    const text = (result.value || '').replace(/\r\n/g, '\n').trim();
    const filename = path.basename(filePath);

    if (!text) {
      throw new Error(`Word document ${filename} did not contain extractable text`);
    }

    return [
      new Document({
        pageContent: text,
        metadata: {
          source: filePath,
          filename,
          page_number: 1,
          total_pages: 1,
        },
      }),
    ];
  }

  private async loadTextDocument(filePath: string): Promise<Document[]> {
    const content = (await fs.readFile(filePath, 'utf-8')).replace(/\r\n/g, '\n');
    const trimmed = content.trim();
    const filename = path.basename(filePath);

    if (!trimmed) {
      throw new Error(`Document ${filename} appears to be empty`);
    }

    return [
      new Document({
        pageContent: trimmed,
        metadata: {
          source: filePath,
          filename,
          page_number: 1,
          total_pages: 1,
        },
      }),
    ];
  }

  /**
   * Infer document type from file extension
   */
  private inferDocumentType(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    const typeMap: Record<string, string> = {
      '.pdf': 'pdf_document',
      '.txt': 'text_document',
      '.md': 'markdown_document',
      '.docx': 'word_document',
      '.xlsx': 'excel_document',
    };
    return typeMap[ext] || 'unknown';
  }

  /**
   * Store document chunks in HANA Cloud Vector Store
   */
  private async storeInHana(
    chunks: Document[],
    embeddings: number[][]
  ): Promise<void> {
    await this.initHanaConnection();

    // Ensure table exists with correct schema
    try {
      // Check if table exists by trying to query it
      const checkSQL = `SELECT TOP 1 * FROM "${this.config.vectorTableName}"`;
      await this.executeSQL(checkSQL);
      console.log(`✅ Table ${this.config.vectorTableName} exists`);
    } catch (error: any) {
      // Table doesn't exist or has wrong schema, create it
      console.log(`Creating table ${this.config.vectorTableName}...`);
      
      // Drop table if it exists with wrong schema
      try {
        await this.executeSQL(`DROP TABLE "${this.config.vectorTableName}"`);
        console.log(`Dropped existing table ${this.config.vectorTableName}`);
      } catch (dropError) {
        // Table doesn't exist, that's fine
      }
      
      // Create table with correct schema
      const createTableSQL = `
        CREATE TABLE "${this.config.vectorTableName}" (
          "id" NVARCHAR(255) PRIMARY KEY,
          "content" NCLOB,
          "metadata" NCLOB,
          "embedding" REAL_VECTOR(1536)
        )
      `;
      await this.executeSQL(createTableSQL);
      console.log(`✅ Created table ${this.config.vectorTableName}`);
    }

    // Insert chunks with embeddings
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      const embedding = embeddings[i];
      const metadata = chunk.metadata as DocumentMetadata;

      const vectorString = `[${embedding.join(',')}]`;
      const insertSQL = `
        INSERT INTO "${this.config.vectorTableName}" 
        ("id", "content", "metadata", "embedding")
        VALUES (?, ?, ?, TO_REAL_VECTOR(?))
      `;

      await this.executePreparedSQL(insertSQL, [
        metadata.chunk_id,
        chunk.pageContent,
        JSON.stringify(metadata),
        vectorString,
      ]);
    }

    console.log(`✅ Stored ${chunks.length} chunks in HANA`);
  }

  /**
   * Ensure the document header table exists with the expected schema
   */
  private async ensureHeaderTable(): Promise<void> {
    await this.initHanaConnection();

    try {
      const checkSQL = `SELECT TOP 1 * FROM "${this.config.headerTableName}"`;
      await this.executeSQL(checkSQL);
      console.log(`✅ Header table ${this.config.headerTableName} exists`);
    } catch (error: any) {
      console.log(`Creating header table ${this.config.headerTableName}...`);

      try {
        await this.executeSQL(`DROP TABLE "${this.config.headerTableName}"`);
        console.log(`Dropped existing header table ${this.config.headerTableName}`);
      } catch (dropError) {
        // Table doesn't exist, that's fine
      }

      const createHeaderTableSQL = `
        CREATE TABLE "${this.config.headerTableName}" (
          "tenant_id" NVARCHAR(255) NOT NULL,
          "document_id" NVARCHAR(255) NOT NULL,
          "source_filename" NVARCHAR(512),
          "document_type" NVARCHAR(64),
          "language" NVARCHAR(16),
          "title" NVARCHAR(512),
          "summary" NCLOB,
          "total_pages" INTEGER,
          "chunk_count" INTEGER,
          "created_at" NVARCHAR(64),
          "summary_embedding" REAL_VECTOR(1536),
          PRIMARY KEY ("tenant_id", "document_id")
        )
      `;
      await this.executeSQL(createHeaderTableSQL);
      console.log(`✅ Created header table ${this.config.headerTableName}`);
    }
  }

  /**
   * Resolve flexible document handles (IDs, filenames, titles) to canonical document_ids
   * using the header table and HANA fuzzy search.
   */
  private async resolveDocumentHandlesToIds(
    handles: string[],
    tenantId?: string | null,
  ): Promise<string[]> {
    await this.initHanaConnection();
    await this.ensureHeaderTable();

    const resolvedIds = new Set<string>();
    const headerTable = this.config.headerTableName;

    for (const rawHandle of handles) {
      const handle = (rawHandle || '').trim();
      if (!handle) continue;

      const paramsBase: any[] = [];
      const whereTenant = tenantId
        ? '"tenant_id" = ? AND '
        : '';
      if (tenantId) {
        paramsBase.push(tenantId);
      }

      // 1) If it looks like a 32-char hex string, try direct document_id match first
      const looksLikeId = /^[0-9a-f]{32}$/i.test(handle);
      if (looksLikeId) {
        const idParams = [...paramsBase, handle];
        const idSql = `
          SELECT TOP 1 "document_id"
          FROM "${headerTable}"
          WHERE ${whereTenant}"document_id" = ?
        `;
        try {
          const rows = await this.executePreparedSQL(idSql, idParams);
          if (rows && rows.length > 0) {
            const docId = rows[0].DOCUMENT_ID ?? rows[0].document_id;
            if (docId) {
              resolvedIds.add(String(docId));
              continue; // already resolved, no need to try other strategies
            }
          }
        } catch (err) {
          console.error('Error resolving handle as document_id:', err);
        }
      }

      // 2) Try to detect filenames by extension
      const looksLikeFilename = /\.[a-zA-Z0-9]{2,4}$/.test(handle);

      if (looksLikeFilename) {
        // 2a) Exact match on source_filename
        const exactParams = [...paramsBase, handle];
        const exactSql = `
          SELECT TOP 3 "document_id"
          FROM "${headerTable}"
          WHERE ${whereTenant}"source_filename" = ?
        `;
        try {
          const rows = await this.executePreparedSQL(exactSql, exactParams);
          if (rows && rows.length > 0) {
            for (const row of rows) {
              const docId = row.DOCUMENT_ID ?? row.document_id;
              if (docId) {
                resolvedIds.add(String(docId));
              }
            }
            continue;
          }
        } catch (err) {
          console.error('Error resolving handle as exact filename:', err);
        }

        // 2b) Fuzzy match on source_filename
        const fuzzyParams = [...paramsBase, handle];
        const fuzzySql = `
          SELECT TOP 3 "document_id"
          FROM "${headerTable}"
          WHERE ${whereTenant}CONTAINS("source_filename", ?, FUZZY(0.7))
        `;
        try {
          const rows = await this.executePreparedSQL(fuzzySql, fuzzyParams);
          if (rows && rows.length > 0) {
            for (const row of rows) {
              const docId = row.DOCUMENT_ID ?? row.document_id;
              if (docId) {
                resolvedIds.add(String(docId));
              }
            }
            continue;
          }
        } catch (err) {
          console.error('Error resolving handle as fuzzy filename:', err);
        }
      }

      // 3) Treat remaining handles primarily as titles
      // 3a) Exact match on title
      const titleExactParams = [...paramsBase, handle];
      const titleExactSql = `
        SELECT TOP 3 "document_id"
        FROM "${headerTable}"
        WHERE ${whereTenant}"title" = ?
      `;
      try {
        const rows = await this.executePreparedSQL(titleExactSql, titleExactParams);
        if (rows && rows.length > 0) {
          for (const row of rows) {
            const docId = row.DOCUMENT_ID ?? row.document_id;
            if (docId) {
              resolvedIds.add(String(docId));
            }
          }
          continue;
        }
      } catch (err) {
        console.error('Error resolving handle as exact title:', err);
      }

      // 3b) Fuzzy match on title and source_filename to catch truncated or modified titles
      const titleFuzzyParams = [...paramsBase, handle, handle];
      const titleFuzzySql = `
        SELECT TOP 3 "document_id"
        FROM "${headerTable}"
        WHERE ${whereTenant}(
          CONTAINS("title", ?, FUZZY(0.7))
          OR CONTAINS("source_filename", ?, FUZZY(0.7))
        )
      `;
      try {
        const rows = await this.executePreparedSQL(titleFuzzySql, titleFuzzyParams);
        if (rows && rows.length > 0) {
          for (const row of rows) {
            const docId = row.DOCUMENT_ID ?? row.document_id;
            if (docId) {
              resolvedIds.add(String(docId));
            }
          }
        }
      } catch (err) {
        console.error('Error resolving handle as fuzzy title:', err);
      }
    }

    return Array.from(resolvedIds);
  }

  /**
   * Create a preview string from the first pages of the document
   */
  private createPreviewText(documents: Document[], maxPages: number = 3, maxChars: number = 4000): string {
    const pieces: string[] = [];
    for (let i = 0; i < documents.length && i < maxPages; i++) {
      const content = documents[i].pageContent || '';
      if (!content) continue;
      pieces.push(content);
      const joined = pieces.join('\n\n');
      if (joined.length >= maxChars) {
        return joined.slice(0, maxChars);
      }
    }
    return pieces.join('\n\n').slice(0, maxChars);
  }

  /**
   * Generate document-level metadata (title, summary, language) and a summary embedding
   */
  private async generateDocumentSummaryMetadata(
    documents: Document[],
    opts: {
      tenantId: string;
      documentId: string;
      sourceFilename: string;
      documentType: string;
      createdAt: string;
    }
  ): Promise<{ title: string; summary: string; language?: string; summaryEmbedding: number[] | null }> {
    const preview = this.createPreviewText(
      documents,
      this.config.summaryInputMaxPages,
      this.config.summaryInputMaxChars,
    );

    if (!preview) {
      const fallbackTitle = opts.sourceFilename || opts.documentId;
      return {
        title: fallbackTitle,
        summary: '',
        language: undefined,
        summaryEmbedding: null,
      };
    }

    const metadataClient = this.getMetadataClient();

    const prompt = `You are a service that summarizes enterprise documents and generates metadata.

Return ONLY a strict JSON object with the following keys:
- title: short, descriptive English title for the document (string)
- summary: concise English summary of what the document is about (string). You may append free-form tags or labels at the end of the summary which represent the domain or topic of the document.
- language: ISO language code of the original document content, for example "en" or "de" (string).

Do not include any additional keys or explanations.

Document filename: ${opts.sourceFilename}
Document type: ${opts.documentType}

Document preview (first pages):
"""
${preview}
"""`;

    let rawContent: any;
    try {
      const response = await metadataClient.invoke(prompt);
      rawContent = (response as any)?.content;
    } catch (err) {
      console.error('Metadata LLM call failed, falling back to simple title/summary:', err);
      const fallbackTitle = opts.sourceFilename || opts.documentId;
      const fallbackSummary = preview.slice(0, 2000);
      const embeddingClient = this.getEmbeddingClient();
      const summaryEmbedding = await embeddingClient.embedQuery(fallbackSummary);
      return {
        title: fallbackTitle,
        summary: fallbackSummary,
        language: undefined,
        summaryEmbedding,
      };
    }

    let parsed: any;
    try {
      const contentString = typeof rawContent === 'string'
        ? rawContent
        : Array.isArray(rawContent)
          ? rawContent.map((c: any) => (typeof c === 'string' ? c : c?.text ?? '')).join('')
          : String(rawContent ?? '');
      parsed = JSON.parse(contentString);
    } catch (parseErr) {
      console.error('Failed to parse metadata JSON, falling back to preview-based summary:', parseErr);
      const fallbackTitle = opts.sourceFilename || opts.documentId;
      const fallbackSummary = preview.slice(0, 2000);
      const embeddingClient = this.getEmbeddingClient();
      const summaryEmbedding = await embeddingClient.embedQuery(fallbackSummary);
      return {
        title: fallbackTitle,
        summary: fallbackSummary,
        language: undefined,
        summaryEmbedding,
      };
    }

    const title = typeof parsed?.title === 'string' && parsed.title.trim().length > 0
      ? parsed.title.trim()
      : (opts.sourceFilename || opts.documentId);
    const summary = typeof parsed?.summary === 'string' && parsed.summary.trim().length > 0
      ? parsed.summary.trim()
      : this.createPreviewText(documents, 3, 2000);
    const language = typeof parsed?.language === 'string' && parsed.language.trim().length > 0
      ? parsed.language.trim()
      : undefined;

    const embeddingClient = this.getEmbeddingClient();
    const summaryEmbedding = await embeddingClient.embedQuery(summary.slice(0, 8000));

    return { title, summary, language, summaryEmbedding };
  }

  /**
   * Store or update a document header row in HANA
   */
  private async storeHeaderRow(params: {
    tenantId: string;
    documentId: string;
    sourceFilename: string;
    documentType: string;
    language?: string;
    title: string;
    summary: string;
    totalPages: number;
    chunkCount: number;
    createdAt: string;
    summaryEmbedding: number[] | null;
  }): Promise<void> {
    await this.ensureHeaderTable();

    const vectorString = params.summaryEmbedding ? `[${params.summaryEmbedding.join(',')}]` : '[]';

    const deleteSQL = `
      DELETE FROM "${this.config.headerTableName}"
      WHERE "tenant_id" = ? AND "document_id" = ?
    `;
    await this.executePreparedSQL(deleteSQL, [params.tenantId, params.documentId]);

    const insertSQL = `
      INSERT INTO "${this.config.headerTableName}"
      ("tenant_id", "document_id", "source_filename", "document_type", "language", "title", "summary",
       "total_pages", "chunk_count", "created_at", "summary_embedding")
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TO_REAL_VECTOR(?))
    `;

    await this.executePreparedSQL(insertSQL, [
      params.tenantId,
      params.documentId,
      params.sourceFilename,
      params.documentType,
      params.language ?? null,
      params.title,
      params.summary,
      params.totalPages,
      params.chunkCount,
      params.createdAt,
      vectorString,
    ]);
  }

  /**
   * Execute SQL query on HANA
   */
  private async executeSQL(sql: string, params: any[] = []): Promise<any> {
    return new Promise((resolve, reject) => {
      this.hanaClient.exec(sql, params, (err: Error, rows: any) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  /**
   * Execute prepared SQL statement on HANA
   */
  private async executePreparedSQL(sql: string, params: any[]): Promise<any> {
    return new Promise((resolve, reject) => {
      this.hanaClient.prepare(sql, (prepareErr: Error, statement: any) => {
        if (prepareErr) {
          reject(prepareErr);
          return;
        }

        statement.exec(params, (execErr: Error, rows: any) => {
          // Always drop statement to avoid leaks
          statement.drop(() => {});

          if (execErr) {
            reject(execErr);
          } else {
            resolve(rows);
          }
        });
      });
    });
  }

  /**
   * Ingest a single document into HANA Cloud Vector Store
   */
  async ingestDocument(
    filePath: string,
    documentMetadata?: Record<string, any>,
    tenantId?: string,
    jobId?: string
  ): Promise<IngestionResult> {
    try {
      console.log(`Starting ingestion of document: ${path.basename(filePath)}`);

      if (jobId) {
        updateJob(jobId, {
          status: 'running',
          stage: 'parsing',
          message: `Loading document ${path.basename(filePath)}`,
        });
      }

      const tenant = tenantId || this.config.defaultTenantId;
      const timestamp = new Date().toISOString();

      // Load document
      const documents = await this.loadDocument(filePath);

      const totalPagesFromDocs = documents.reduce((max, doc) => {
        const docTotalPages = Number((doc.metadata as Record<string, any>)?.total_pages) || 0;
        return Math.max(max, docTotalPages);
      }, documents.length || 1);

      const documentId = path.parse(filePath).name;
      const fallbackSourceFilename = path.basename(filePath);
      const documentType = this.inferDocumentType(filePath);

      // Generate document-level metadata using the first pages
      if (jobId) {
        updateJob(jobId, {
          stage: 'parsing',
          message: 'Generating document metadata (title, summary)',
        });
      }

      const { title, summary, language, summaryEmbedding } = await this.generateDocumentSummaryMetadata(documents, {
        tenantId: tenant,
        documentId,
        sourceFilename: fallbackSourceFilename,
        documentType,
        createdAt: timestamp,
      });

      // Prefer original filename from metadata (provided by frontend) over temp path basename
      const headerSourceFilename = (documentMetadata?.source_filename as string) || fallbackSourceFilename;

      // Base metadata (after loading so we know page counts)
      const baseMetadata: DocumentMetadata = {
        document_id: documentId,
        source_filename: headerSourceFilename,
        created_at: timestamp,
        document_type: documentType,
        tenant_id: tenant,
        total_pages: totalPagesFromDocs,
        title,
        summary,
        language,
        ...documentMetadata,
      };

      if (jobId) {
        updateJob(jobId, {
          stage: 'chunking',
          message: 'Splitting document into chunks',
        });
      }

      // Split into chunks
      const textSplitter = this.getTextSplitter();
      const chunks = await textSplitter.splitDocuments(documents);
      console.log(`Split document into ${chunks.length} chunks`);

      if (jobId) {
        updateJob(jobId, {
          stage: 'embedding',
          totalChunks: chunks.length,
          processedChunks: 0,
          message: `Embedding ${chunks.length} chunk(s)`
        });
      }

      // Enrich chunks with metadata
      const enrichedChunks = chunks.map((chunk: Document, idx: number) => {
        // Preserve page_number and total_pages from source document if present
        const sourceMetadata = chunk.metadata as Record<string, any>;
        const chunkMetadata: DocumentMetadata = {
          ...baseMetadata,
          ...(sourceMetadata || {}),
          chunk_id: `${baseMetadata.document_id}#chunk_${idx.toString().padStart(3, '0')}`,
          chunk_index: idx,
          total_chunks: chunks.length,
          // Ensure page metadata is preserved from source
          page_number: sourceMetadata?.page_number || baseMetadata.page_number || 1,
          total_pages: sourceMetadata?.total_pages || baseMetadata.total_pages || 1,
        };

        const pageContentForEmbedding = baseMetadata.title
          ? `Title: ${baseMetadata.title}\n\n${chunk.pageContent}`
          : chunk.pageContent;

        return new Document({
          pageContent: pageContentForEmbedding,
          metadata: chunkMetadata,
        });
      });

      // Generate embeddings (batched)
      const embeddingClient = this.getEmbeddingClient();
      const texts = enrichedChunks.map((c: Document) => c.pageContent);
      const embeddings: number[][] = [];
      const batchSize = Math.max(1, this.config.embeddingBatchSize || 16);

      for (let start = 0; start < texts.length; start += batchSize) {
        const end = Math.min(start + batchSize, texts.length);
        const batch = texts.slice(start, end);
        const batchEmbeddings = await embeddingClient.embedDocuments(batch);

        for (let i = 0; i < batchEmbeddings.length; i++) {
          embeddings.push(batchEmbeddings[i]);
        }

        if (jobId) {
          updateJob(jobId, {
            processedChunks: embeddings.length,
            message: `Embedding chunk ${embeddings.length} of ${chunks.length}`,
          });
        }
      }

      if (jobId) {
        updateJob(jobId, {
          stage: 'storing',
          message: 'Storing chunks and embeddings',
        });
      }

      // Store in HANA (chunk-level)
      await this.storeInHana(enrichedChunks, embeddings);

      // Store or update header row (document-level)
      await this.storeHeaderRow({
        tenantId: tenant,
        documentId,
        sourceFilename: headerSourceFilename,
        documentType,
        language,
        title,
        summary,
        totalPages: totalPagesFromDocs,
        chunkCount: enrichedChunks.length,
        createdAt: timestamp,
        summaryEmbedding,
      });

      if (jobId) {
        updateJob(jobId, {
          status: 'completed',
          stage: 'completed',
          processedChunks: enrichedChunks.length,
          totalChunks: enrichedChunks.length,
          documentId,
          message: 'Ingestion completed successfully',
        });
      }

      return {
        success: true,
        document_id: documentId,
        filename: path.basename(filePath),
        chunks_created: enrichedChunks.length,
        tenant_id: tenant,
        timestamp,
      };
    } catch (error) {
      console.error(`Failed to ingest document: ${error}`);

      if (jobId) {
        updateJob(jobId, {
          status: 'failed',
          stage: 'failed',
          error: error instanceof Error ? error.message : String(error),
          message: 'Ingestion failed',
        });
      }
      return {
        success: false,
        document_id: path.parse(filePath).name,
        filename: path.basename(filePath),
        chunks_created: 0,
        tenant_id: tenantId || this.config.defaultTenantId,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Search chunks in HANA Cloud Vector Store (chunk-first RAG search)
   */
  async searchDocuments(
    query: string,
    tenantId?: string,
    k: number = 4,
    documentIds?: string[],
    documentNames?: string[],
  ): Promise<Document[]> {
    try {
      await this.initHanaConnection();

      const tenantFilter = tenantId ?? null;

      // Generate query embedding
      const embeddingClient = this.getEmbeddingClient();
      const queryEmbedding = await embeddingClient.embedQuery(query);

      const vectorString = `[${queryEmbedding.join(',')}]`;

      // Search in HANA using cosine similarity on chunk table
      let searchSQL = `
        SELECT TOP ${k}
          "content",
          "metadata",
          COSINE_SIMILARITY("embedding", TO_REAL_VECTOR(?)) as "score"
        FROM "${this.config.vectorTableName}"
      `;

      const params: any[] = [vectorString];
      const whereClauses: string[] = [];

      if (tenantFilter) {
        whereClauses.push(`JSON_VALUE("metadata", '$.tenant_id') = ?`);
        params.push(tenantFilter);
      }

      // Resolve any flexible documentNames (IDs, filenames, titles) into canonical document_ids
      const resolvedFromNames: string[] =
        documentNames && documentNames.length > 0
          ? await this.resolveDocumentHandlesToIds(documentNames, tenantFilter)
          : [];

      const allDocumentIds: string[] = Array.from(
        new Set([...(documentIds || []), ...resolvedFromNames]),
      );

      if (allDocumentIds.length > 0) {
        const placeholders = allDocumentIds.map(() => '?').join(',');
        whereClauses.push(`JSON_VALUE("metadata", '$.document_id') IN (${placeholders})`);
        for (const id of allDocumentIds) {
          params.push(id);
        }
      }

      if (whereClauses.length > 0) {
        searchSQL += `
          WHERE ${whereClauses.join(' AND ')}
        `;
      }

      searchSQL += `
        ORDER BY "score" DESC
      `;

      const results = await this.executePreparedSQL(searchSQL, params);

      return results.map((row: any) => {
        return new Document({
          pageContent: row.content,
          metadata: {
            ...JSON.parse(row.metadata),
            score: row.score,
          },
        });
      });
    } catch (error) {
      console.error(`Search failed: ${error}`);
      throw error;
    }
  }

  async getDocumentSegments(
    documentId: string,
    options: { chunkIndex?: number; pageNumber?: number },
    tenantId?: string,
  ): Promise<Document[]> {
    await this.initHanaConnection();

    const { chunkIndex, pageNumber } = options || {};
    if ((chunkIndex == null && pageNumber == null) || (chunkIndex != null && pageNumber != null)) {
      throw new Error('You must provide either chunkIndex or pageNumber (but not both).');
    }

    const tenantFilter = tenantId ?? null;
    const params: any[] = [];
    const whereClauses: string[] = [];

    if (tenantFilter) {
      whereClauses.push(`JSON_VALUE("metadata", '$.tenant_id') = ?`);
      params.push(tenantFilter);
    }

    whereClauses.push(`JSON_VALUE("metadata", '$.document_id') = ?`);
    params.push(documentId);

    let orderClause = '';

    if (chunkIndex != null) {
      whereClauses.push(`JSON_VALUE("metadata", '$.chunk_index') = ?`);
      params.push(String(chunkIndex));
    } else if (pageNumber != null) {
      whereClauses.push(`JSON_VALUE("metadata", '$.page_number') = ?`);
      params.push(String(pageNumber));
      orderClause = "ORDER BY CAST(JSON_VALUE(\"metadata\", '$.chunk_index') AS INTEGER)";
    }

    let sql = `
      SELECT "content", "metadata"
      FROM "${this.config.vectorTableName}"
      WHERE ${whereClauses.join(' AND ')}
    `;

    if (orderClause) {
      sql += `\n      ${orderClause}`;
    }

    const rows = await this.executePreparedSQL(sql, params);

    return rows.map((row: any) => {
      return new Document({
        pageContent: row.content,
        metadata: JSON.parse(row.metadata),
      });
    });
  }

  /**
   * Get the default tenant ID configured for this service.
   *
   * This is useful for callers (like MCP tools) that want to scope
   * searches to a tenant without exposing an explicit tenant_id parameter.
   */
  getDefaultTenantId(): string {
    return this.config.defaultTenantId;
  }

  /**
   * Search documents by header summaries (document-level search on summary_embedding)
   */
  async searchDocumentsByHeader(
    query: string,
    tenantId?: string,
    k: number = 4,
  ): Promise<DocumentSummary[]> {
    await this.initHanaConnection();
    await this.ensureHeaderTable();

    const embeddingClient = this.getEmbeddingClient();
    const queryEmbedding = await embeddingClient.embedQuery(query);
    const vectorString = `[${queryEmbedding.join(',')}]`;

    const params: any[] = [vectorString];
    const whereParts: string[] = [];

    if (tenantId) {
      whereParts.push(`"tenant_id" = ?`);
      params.push(tenantId);
    }

    const whereClause = whereParts.length ? `WHERE ${whereParts.join(' AND ')}` : '';

    const sql = `
      SELECT TOP ${k}
        "document_id",
        "source_filename" AS filename,
        "document_type",
        "tenant_id",
        "total_pages",
        "chunk_count",
        "created_at",
        "title",
        "summary",
        COSINE_SIMILARITY("summary_embedding", TO_REAL_VECTOR(?)) AS "score"
      FROM "${this.config.headerTableName}"
      ${whereClause}
      ORDER BY "score" DESC
    `;

    const rows = await this.executePreparedSQL(sql, params);
    return rows.map((row: any) => {
      const rawTitle = row.TITLE ?? row.title ?? undefined;
      const rawSummary = row.SUMMARY ?? row.summary ?? undefined;

      const title =
        typeof rawTitle === 'string'
          ? rawTitle
          : rawTitle && Buffer.isBuffer(rawTitle)
            ? rawTitle.toString('utf-8')
            : undefined;

      const summary =
        typeof rawSummary === 'string'
          ? rawSummary
          : rawSummary && Buffer.isBuffer(rawSummary)
            ? rawSummary.toString('utf-8')
            : undefined;

      return {
        document_id: row.DOCUMENT_ID ?? row.document_id ?? '',
        filename: row.FILENAME ?? row.filename ?? '',
        document_type: row.DOCUMENT_TYPE ?? row.document_type ?? 'unknown',
        tenant_id: row.TENANT_ID ?? row.tenant_id ?? this.config.defaultTenantId,
        total_pages: Number(row.TOTAL_PAGES ?? row.total_pages ?? 0),
        chunk_count: Number(row.CHUNK_COUNT ?? row.chunk_count ?? 0),
        created_at: row.CREATED_AT ?? row.created_at ?? '',
        title,
        summary,
        score: Number(row.SCORE ?? row.score ?? 0),
      };
    });
  }

  /**
   * Hybrid two-step search: first search headers by summary, then search chunks within top documents.
   */
  async searchDocumentsHybrid(
    query: string,
    tenantId?: string,
    headerK: number = 5,
    chunkKPerDocument: number = 2,
  ): Promise<{
    document: DocumentSummary;
    chunks: Document[];
  }[]> {
    const headerResults = await this.searchDocumentsByHeader(query, tenantId, headerK);

    if (headerResults.length === 0) {
      // Fallback: just do a normal chunk search
      const chunks = await this.searchDocuments(query, tenantId, headerK * chunkKPerDocument);
      return chunks.map((chunk) => ({
        document: {
          document_id: (chunk.metadata as any)?.document_id ?? '',
          filename: (chunk.metadata as any)?.source_filename ?? '',
          document_type: (chunk.metadata as any)?.document_type ?? 'unknown',
          tenant_id: (chunk.metadata as any)?.tenant_id ?? (tenantId || this.config.defaultTenantId),
          total_pages: (chunk.metadata as any)?.total_pages ?? 0,
          chunk_count: 0,
          created_at: (chunk.metadata as any)?.created_at ?? '',
          title: (chunk.metadata as any)?.title,
          summary: (chunk.metadata as any)?.summary,
          score: (chunk.metadata as any)?.score,
        },
        chunks: [chunk],
      }));
    }

    const results: {
      document: DocumentSummary;
      chunks: Document[];
    }[] = [];

    for (const header of headerResults) {
      const docId = header.document_id;
      if (!docId) {
        continue;
      }

      const chunksForDoc = await this.searchDocuments(
        query,
        tenantId,
        chunkKPerDocument,
        [docId],
      );

      results.push({
        document: header,
        chunks: chunksForDoc,
      });
    }

    return results;
  }

  async listDocuments(tenantId?: string): Promise<DocumentSummary[]> {
    await this.initHanaConnection();
    // Ensure header table exists so listing works even before first ingestion
    await this.ensureHeaderTable();

    const whereParts: string[] = [];
    const params: any[] = [];

    if (tenantId) {
      whereParts.push(`"tenant_id" = ?`);
      params.push(tenantId);
    }

    const whereClause = whereParts.length ? `WHERE ${whereParts.join(' AND ')}` : '';

    const summarySQL = `
      SELECT
        "document_id",
        "source_filename" AS filename,
        "document_type",
        "tenant_id",
        "total_pages",
        "chunk_count",
        "created_at",
        "title",
        "summary"
      FROM "${this.config.headerTableName}"
      ${whereClause}
      ORDER BY "created_at" DESC
    `;

    const rows = await this.executePreparedSQL(summarySQL, params);
    return rows.map((row: any) => {
      const rawTitle = row.TITLE ?? row.title ?? undefined;
      const rawSummary = row.SUMMARY ?? row.summary ?? undefined;

      const title =
        typeof rawTitle === 'string'
          ? rawTitle
          : rawTitle && Buffer.isBuffer(rawTitle)
            ? rawTitle.toString('utf-8')
            : undefined;

      const summary =
        typeof rawSummary === 'string'
          ? rawSummary
          : rawSummary && Buffer.isBuffer(rawSummary)
            ? rawSummary.toString('utf-8')
            : undefined;

      return {
        document_id: row.DOCUMENT_ID ?? row.document_id ?? '',
        filename: row.FILENAME ?? row.filename ?? '',
        document_type: row.DOCUMENT_TYPE ?? row.document_type ?? 'unknown',
        tenant_id: row.TENANT_ID ?? row.tenant_id ?? this.config.defaultTenantId,
        total_pages: Number(row.TOTAL_PAGES ?? row.total_pages ?? 0),
        chunk_count: Number(row.CHUNK_COUNT ?? row.chunk_count ?? 0),
        created_at: row.CREATED_AT ?? row.created_at ?? '',
        title,
        summary,
      };
    });
  }

  async deleteDocument(documentId: string, tenantId?: string): Promise<{
    document_id: string;
    tenant_id?: string;
    chunks_deleted: number;
  }> {
    if (!documentId) {
      throw new Error('documentId is required');
    }

    await this.initHanaConnection();

    // --- Path 1: try header-based deletion using source_filename + tenant ---
    let totalChunksDeleted = 0;
    let resolvedTenantId: string | undefined = tenantId;

    try {
      const headerWhereParts = [`"document_id" = ?`];
      const headerParams: any[] = [documentId];
      if (tenantId) {
        headerWhereParts.push(`"tenant_id" = ?`);
        headerParams.push(tenantId);
      }

      const headerWhereClause = `WHERE ${headerWhereParts.join(' AND ')}`;
      const lookupSQL = `
        SELECT TOP 1 "source_filename", "tenant_id"
        FROM "${this.config.headerTableName}"
        ${headerWhereClause}
      `;
      const lookupRows = await this.executePreparedSQL(lookupSQL, headerParams);
      const sourceFilename = lookupRows?.[0]?.SOURCE_FILENAME ?? lookupRows?.[0]?.source_filename;
      resolvedTenantId = lookupRows?.[0]?.TENANT_ID ?? lookupRows?.[0]?.tenant_id ?? tenantId;

      if (sourceFilename && resolvedTenantId) {
        const deleteWhereParts = [
          `JSON_VALUE("metadata", '$.source_filename') = ?`,
          `JSON_VALUE("metadata", '$.tenant_id') = ?`,
        ];
        const deleteParamsBase: any[] = [sourceFilename, resolvedTenantId];

        const deleteWhereClause = `WHERE ${deleteWhereParts.join(' AND ')}`;

        const countSQL = `
          SELECT COUNT(*) AS chunk_count
          FROM "${this.config.vectorTableName}"
          ${deleteWhereClause}
        `;
        const countRows = await this.executePreparedSQL(countSQL, [...deleteParamsBase]);
        const chunkCount = Number(countRows?.[0]?.CHUNK_COUNT ?? countRows?.[0]?.chunk_count ?? 0);

        if (chunkCount > 0) {
          const deleteChunksSQL = `
            DELETE FROM "${this.config.vectorTableName}"
            ${deleteWhereClause}
          `;
          await this.executePreparedSQL(deleteChunksSQL, [...deleteParamsBase]);
          totalChunksDeleted += chunkCount;

          const deleteHeaderSQL = `
            DELETE FROM "${this.config.headerTableName}"
            WHERE "tenant_id" = ? AND "document_id" = ?
          `;
          await this.executePreparedSQL(deleteHeaderSQL, [resolvedTenantId, documentId]);

          return {
            document_id: documentId,
            tenant_id: resolvedTenantId,
            chunks_deleted: totalChunksDeleted,
          };
        }
      }
    } catch (headerError) {
      // If header lookup or deletion fails, fall back to document_id-based deletion below
      console.warn('Header-based deletion did not succeed, falling back to document_id-based deletion:', headerError);
    }

    // --- Path 2: fallback deletion based on metadata.document_id (supports older ingestions) ---
    const docIdWhereParts = [`JSON_VALUE("metadata", '$.document_id') = ?`];
    const docIdParams: any[] = [documentId];
    if (tenantId) {
      docIdWhereParts.push(`JSON_VALUE("metadata", '$.tenant_id') = ?`);
      docIdParams.push(tenantId);
    }

    const docIdWhereClause = `WHERE ${docIdWhereParts.join(' AND ')}`;

    const countByIdSQL = `
      SELECT COUNT(*) AS chunk_count
      FROM "${this.config.vectorTableName}"
      ${docIdWhereClause}
    `;
    const countByIdRows = await this.executePreparedSQL(countByIdSQL, [...docIdParams]);
    const chunkCountById = Number(countByIdRows?.[0]?.CHUNK_COUNT ?? countByIdRows?.[0]?.chunk_count ?? 0);

    if (chunkCountById === 0) {
      throw new Error(`Document ${documentId} not found`);
    }

    const deleteByIdSQL = `
      DELETE FROM "${this.config.vectorTableName}"
      ${docIdWhereClause}
    `;
    await this.executePreparedSQL(deleteByIdSQL, [...docIdParams]);
    totalChunksDeleted += chunkCountById;

    // Try to clean up any header rows for this document as well, but don't fail if table/rows are missing
    try {
      const deleteHeaderByIdSQL = `
        DELETE FROM "${this.config.headerTableName}"
        WHERE "document_id" = ?
        ${tenantId ? ' AND "tenant_id" = ?' : ''}
      `;
      await this.executePreparedSQL(deleteHeaderByIdSQL, tenantId ? [documentId, tenantId] : [documentId]);
    } catch (ignoreHeaderDeleteError) {
      console.warn('Header cleanup during fallback deletion failed (ignored):', ignoreHeaderDeleteError);
    }

    return {
      document_id: documentId,
      tenant_id: tenantId,
      chunks_deleted: totalChunksDeleted,
    };
  }
}

// Singleton instance
let documentIngestionService: DocumentIngestionService | null = null;

export function getDocumentIngestionService(): DocumentIngestionService {
  if (!documentIngestionService) {
    documentIngestionService = new DocumentIngestionService();
  }
  return documentIngestionService;
}
