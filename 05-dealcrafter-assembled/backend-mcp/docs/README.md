# MCP Server Documentation

This folder contains all documentation for the MCP server implementation.

## Documentation Files

### Web Search Tool

#### `README-WEB-SEARCH.md`
Complete user guide for the Perplexity web search tool.

**Contents:**
- Feature overview
- Configuration instructions
- Usage examples
- Mock mode documentation
- Troubleshooting guide

#### `WEB-RESEARCH-TOOL.md`
Documentation for the deep web research tool using Sonar Pro.

**Contents:**
- When to use web_search vs web_research
- Technical differences and performance
- Usage examples and best practices
- Configuration requirements
- Workshop considerations

#### `README-SAP-AI-SDK-INTEGRATION.md`
Technical documentation for SAP AI SDK integration.

**Contents:**
- How the integration works
- OAuth2 authentication flow
- Deployment resolution process
- Configuration steps
- Architecture diagrams
- Security best practices

### Implementation Details

#### `IMPLEMENTATION-SUMMARY.md`
High-level summary of the web search tool implementation.

**Contents:**
- What was built
- Key components
- Technical decisions
- API research findings
- Build status
- Next steps

#### `TEST-RESULTS.md`
Detailed test results and findings from SAP AI SDK integration testing.

**Contents:**
- Test summary
- Issues found and fixed
- Available deployments
- Configuration details
- Performance notes
- Troubleshooting tips

#### `CACHING.md`
Documentation for the web search tool's caching implementation.

**Contents:**
- What is cached (client, token, deployment URL)
- Performance impact and benchmarks
- Cache invalidation strategies
- Workshop vs production considerations
- Testing and troubleshooting

#### `TROUBLESHOOTING.md`
Comprehensive troubleshooting guide for common issues.

**Contents:**
- Mock mode issues (environment not loaded)
- Authentication errors
- Deployment resolution problems
- Performance issues
- Testing failures
- Common gotchas and solutions

## Quick Links

### Getting Started
1. Read `README-WEB-SEARCH.md` for an overview
2. Follow `README-SAP-AI-SDK-INTEGRATION.md` for setup
3. Check `TEST-RESULTS.md` for verification

### For Developers
- Implementation details: `IMPLEMENTATION-SUMMARY.md`
- Test results: `TEST-RESULTS.md`
- SAP integration: `README-SAP-AI-SDK-INTEGRATION.md`

### For Users
- User guide: `README-WEB-SEARCH.md`
- Configuration: `README-SAP-AI-SDK-INTEGRATION.md` (Configuration Steps section)
- Troubleshooting: `README-WEB-SEARCH.md` (Troubleshooting section)

## Related Files

- **Tests**: See `../tests/` folder
- **Source Code**: See `../src/tools/webSearchTool.ts`
- **Environment Config**: See `../.env.example`
