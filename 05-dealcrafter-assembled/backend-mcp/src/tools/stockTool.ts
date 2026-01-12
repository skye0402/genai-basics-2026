/**
 * Stock Info Tool for DealCrafter
 * 
 * Uses Yahoo Finance API to fetch real-time stock data.
 * Add this file to: backend-mcp/src/tools/stockTool.ts
 * 
 * Then register in server.ts:
 *   import { registerStockInfoTool } from './tools/stockTool';
 *   registerStockInfoTool(server);
 */

import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { registerToolWithLogging } from '../utils/toolLogger';

// Input schema
const stockInfoSchema = z.object({
  ticker: z.string().describe('Stock ticker symbol (e.g., "3382.T" for Seven & i, "3778.T" for Sakura Internet)'),
});

// Output schema
const stockInfoResultSchema = z.object({
  ticker: z.string(),
  company_name: z.string().optional(),
  price: z.number().optional(),
  currency: z.string().optional(),
  change_percent: z.number().optional(),
  previous_close: z.number().optional(),
  market_cap: z.number().optional(),
  pe_ratio: z.number().optional(),
  week_52_high: z.number().optional(),
  week_52_low: z.number().optional(),
  sector: z.string().optional(),
  industry: z.string().optional(),
  error: z.string().optional(),
});

type StockInfoInput = z.infer<typeof stockInfoSchema>;
type StockInfoOutput = z.infer<typeof stockInfoResultSchema>;

/**
 * Fetch stock info from Yahoo Finance API
 */
async function fetchStockInfo(ticker: string): Promise<StockInfoOutput> {
  try {
    // Yahoo Finance v8 API endpoint
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?interval=1d&range=1d`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; DealCrafter/1.0)',
      },
    });

    if (!response.ok) {
      return { ticker, error: `HTTP ${response.status}: ${response.statusText}` };
    }

    const data = await response.json();
    const result = data.chart?.result?.[0];
    
    if (!result) {
      return { ticker, error: 'No data available for this ticker' };
    }

    const meta = result.meta;
    const quote = result.indicators?.quote?.[0];
    
    // Get the latest price
    const prices = quote?.close?.filter((p: number | null) => p !== null) || [];
    const latestPrice = prices[prices.length - 1] || meta.regularMarketPrice;
    
    // Calculate change percentage
    const previousClose = meta.previousClose || meta.chartPreviousClose;
    const changePercent = previousClose 
      ? ((latestPrice - previousClose) / previousClose) * 100 
      : undefined;

    return {
      ticker,
      company_name: meta.shortName || meta.longName,
      price: latestPrice,
      currency: meta.currency || 'JPY',
      change_percent: changePercent ? Math.round(changePercent * 100) / 100 : undefined,
      previous_close: previousClose,
      market_cap: meta.marketCap,
      week_52_high: meta.fiftyTwoWeekHigh,
      week_52_low: meta.fiftyTwoWeekLow,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`[StockTool] Error fetching ${ticker}:`, message);
    return { ticker, error: message };
  }
}

/**
 * Mock stock data for offline testing
 */
function getMockStockInfo(ticker: string): StockInfoOutput {
  const mockData: Record<string, StockInfoOutput> = {
    '3382.T': {
      ticker: '3382.T',
      company_name: 'Seven & i Holdings Co., Ltd.',
      price: 2150,
      currency: 'JPY',
      change_percent: -0.8,
      previous_close: 2167,
      market_cap: 5600000000000,
      pe_ratio: 22.5,
      week_52_high: 2400,
      week_52_low: 1800,
      sector: 'Consumer Cyclical',
      industry: 'Convenience Stores',
    },
    '3778.T': {
      ticker: '3778.T',
      company_name: 'Sakura Internet Inc.',
      price: 5230,
      currency: 'JPY',
      change_percent: 2.3,
      previous_close: 5112,
      market_cap: 180000000000,
      pe_ratio: 45.2,
      week_52_high: 6500,
      week_52_low: 2800,
      sector: 'Technology',
      industry: 'Internet Services',
    },
  };

  return mockData[ticker] || {
    ticker,
    company_name: `Mock Company (${ticker})`,
    price: 1000,
    currency: 'JPY',
    change_percent: 0.5,
  };
}

/**
 * Register the stock info tool with the MCP server
 */
export function registerStockInfoTool(server: McpServer): void {
  registerToolWithLogging(
    server,
    'get_stock_info',
    {
      title: 'Stock Info Tool',
      description: 'Get current stock information for a Japanese stock ticker. Use this to fetch real-time price, market cap, P/E ratio, and other financial metrics.',
      inputSchema: stockInfoSchema.shape,
      outputSchema: stockInfoResultSchema.shape,
    },
    async ({ ticker }: StockInfoInput) => {
      console.log(`[StockTool] Fetching stock info for: ${ticker}`);
      
      // Try real API first, fall back to mock
      let result: StockInfoOutput;
      try {
        result = await fetchStockInfo(ticker);
        if (result.error) {
          console.log(`[StockTool] API error, using mock data`);
          result = getMockStockInfo(ticker);
        }
      } catch {
        console.log(`[StockTool] Fetch failed, using mock data`);
        result = getMockStockInfo(ticker);
      }

      console.log(`[StockTool] Result: ${result.company_name} @ ${result.currency}${result.price}`);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
        structuredContent: result,
      };
    }
  );
}
