import { ResourceTemplate } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

function extractName(variables: Record<string, string | string[] | undefined>): string {
  const rawName = variables.name;

  if (Array.isArray(rawName)) {
    return rawName[0] ?? 'friend';
  }

  return rawName ?? 'friend';
}

export function registerGreetingResource(server: McpServer): void {
  server.registerResource(
    'greeting',
    new ResourceTemplate('greeting://{name}', { list: undefined }),
    {
      title: 'Greeting Resource',
      description: 'Dynamic greeting generator',
    },
    async (uri, variables) => ({
      contents: [
        {
          uri: uri.href,
          text: `Hello, ${extractName(variables)}!`,
        },
      ],
    }),
  );
}
