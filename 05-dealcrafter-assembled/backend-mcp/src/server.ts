import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import express, { type Request, type Response } from 'express';
import cors from 'cors';
import * as dotenv from 'dotenv';

// Load environment variables from .env.local (or .env)
dotenv.config({ path: '.env.local' });
dotenv.config(); // Fallback to .env if .env.local doesn't exist

import { registerGreetingResource } from './resources/greetingResource';
import { registerWebSearchTool, registerWebResearchTool } from './tools/webSearchTool';
import { registerDocumentSearchTool } from './tools/documentTools';
import { registerTimeAndPlaceTool } from './tools/timeAndPlaceTool';
import { registerStockInfoTool } from './tools/stockTool';
import documentRoutes from './api/documentRoutes';

// Log configuration status
console.log('🔧 Configuration:');
console.log(`   LOG_LEVEL: ${process.env.LOG_LEVEL || 'info'}`);
console.log(`   PORT: ${process.env.PORT || 3001}`);
console.log(`   SAP_AI_RESOURCE_GROUP: ${process.env.SAP_AI_RESOURCE_GROUP || 'default'}`);
console.log(`   AICORE_SERVICE_KEY: ${process.env.AICORE_SERVICE_KEY ? '✅ Configured' : '❌ Not configured (mock mode)'}`);

const server = new McpServer({
  name: 'backend-mcp-server',
  version: '1.0.0',
});

registerTools();
registerResources();
registerPrompts();

const app = express();

// Enable CORS for frontend (localhost:5173)
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true,
}));

app.use(express.json());

// REST API routes for document management
app.use('/api/documents', documentRoutes);

// MCP endpoint
app.post('/mcp', async (req: Request, res: Response) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  res.on('close', () => {
    transport.close();
  });

  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

const port = Number.parseInt(process.env.PORT ?? '3001', 10);

app
  .listen(port, () => {
    console.log(`Backend MCP Server running on http://localhost:${port}/mcp`);
  })
  .on('error', (error: unknown) => {
    console.error('Server error:', error);
    process.exit(1);
  });

function registerTools(): void {
  registerWebSearchTool(server);
  registerWebResearchTool(server);
  // Only search is an MCP tool - upload/delete are REST API endpoints
  registerDocumentSearchTool(server);
  registerTimeAndPlaceTool(server);
  registerStockInfoTool(server);
}

function registerResources(): void {
  registerGreetingResource(server);
}

function registerPrompts(): void {
  // No prompts registered for DealCrafter demo
}
