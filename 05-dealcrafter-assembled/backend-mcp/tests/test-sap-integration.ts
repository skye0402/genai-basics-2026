#!/usr/bin/env tsx
/**
 * Test script to verify SAP AI SDK integration
 * Tests OAuth2 token retrieval and deployment URL resolution
 */

import { resolveDeploymentUrl } from '@sap-ai-sdk/ai-api';
import * as dotenv from 'dotenv';

// Load environment variables from .env.local
dotenv.config({ path: '.env.local' });

interface ServiceKey {
  clientid: string;
  clientsecret: string;
  url: string;
  identityzone: string;
  identityzoneid: string;
  appname: string;
  serviceurls: {
    AI_API_URL: string;
  };
}

async function testOAuth2Token(): Promise<string> {
  console.log('\n🔐 Testing OAuth2 Token Retrieval...');
  console.log('─'.repeat(60));

  if (!process.env.AICORE_SERVICE_KEY) {
    throw new Error('❌ AICORE_SERVICE_KEY not found in environment');
  }

  let serviceKey: ServiceKey;
  try {
    serviceKey = JSON.parse(process.env.AICORE_SERVICE_KEY);
    console.log('✅ Service key parsed successfully');
    console.log(`   Client ID: ${serviceKey.clientid.substring(0, 20)}...`);
    console.log(`   OAuth URL: ${serviceKey.url}`);
  } catch (error) {
    throw new Error('❌ Failed to parse AICORE_SERVICE_KEY as JSON');
  }

  const tokenUrl = `${serviceKey.url}/oauth/token`;
  console.log(`\n📡 Requesting token from: ${tokenUrl}`);

  try {
    const tokenResponse = await fetch(tokenUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: serviceKey.clientid,
        client_secret: serviceKey.clientsecret,
      }),
    });

    if (!tokenResponse.ok) {
      const errorText = await tokenResponse.text();
      throw new Error(
        `❌ OAuth2 request failed: ${tokenResponse.status} ${tokenResponse.statusText}\n${errorText}`
      );
    }

    const tokenData = await tokenResponse.json();
    const token = tokenData.access_token;

    if (!token) {
      throw new Error('❌ No access_token in response');
    }

    console.log('✅ OAuth2 token obtained successfully');
    console.log(`   Token (first 30 chars): ${token.substring(0, 30)}...`);
    console.log(`   Token type: ${tokenData.token_type || 'bearer'}`);
    console.log(`   Expires in: ${tokenData.expires_in || 'unknown'} seconds`);

    return token;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`❌ OAuth2 token request failed: ${error.message}`);
    }
    throw error;
  }
}

async function testDeploymentResolution(): Promise<string> {
  console.log('\n🔍 Testing Deployment URL Resolution...');
  console.log('─'.repeat(60));

  const resourceGroup = process.env.SAP_AI_RESOURCE_GROUP || 'default';
  console.log(`   Resource Group: ${resourceGroup}`);
  console.log(`   Scenario ID: foundation-models`);
  console.log(`   Model: sonar (latest)`);

  try {
    const deploymentUrl = await resolveDeploymentUrl({
      scenarioId: 'foundation-models',
      model: {
        name: 'sonar',
        // Don't specify version - let SDK find any version
      },
      resourceGroup,
    });

    if (!deploymentUrl) {
      throw new Error(
        '❌ No deployment URL returned. Ensure Perplexity is deployed in SAP AI Core.'
      );
    }

    console.log('✅ Deployment URL resolved successfully');
    console.log(`   URL: ${deploymentUrl}`);

    return deploymentUrl;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`❌ Deployment resolution failed: ${error.message}`);
    }
    throw error;
  }
}

async function testFullIntegration() {
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║     SAP AI SDK Integration Test                          ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');

  try {
    // Test 1: OAuth2 Token
    const token = await testOAuth2Token();

    // Test 2: Deployment URL Resolution
    const deploymentUrl = await testDeploymentResolution();

    // Summary
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║     ✅ ALL TESTS PASSED                                   ║');
    console.log('╚═══════════════════════════════════════════════════════════╝');
    console.log('\n📋 Summary:');
    console.log(`   ✅ OAuth2 token obtained`);
    console.log(`   ✅ Deployment URL resolved`);
    console.log(`   ✅ Ready for Perplexity API calls`);
    console.log('\n🚀 Next Steps:');
    console.log('   1. Start the MCP server: pnpm dev');
    console.log('   2. Test the web_search tool with an MCP client');
    console.log('   3. Monitor logs for successful API calls');

    console.log('\n📝 Configuration Details:');
    console.log(`   Deployment URL: ${deploymentUrl}`);
    console.log(`   Token (preview): ${token.substring(0, 50)}...`);
    console.log(`   Resource Group: ${process.env.SAP_AI_RESOURCE_GROUP || 'default'}`);

    process.exit(0);
  } catch (error) {
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║     ❌ TEST FAILED                                        ║');
    console.log('╚═══════════════════════════════════════════════════════════╝');

    if (error instanceof Error) {
      console.error('\n❌ Error:', error.message);

      // Provide helpful troubleshooting tips
      console.log('\n💡 Troubleshooting Tips:');

      if (error.message.includes('AICORE_SERVICE_KEY')) {
        console.log('   • Check that .env.local contains AICORE_SERVICE_KEY');
        console.log('   • Ensure the service key is valid JSON');
        console.log('   • Remove any line breaks from the service key');
      }

      if (error.message.includes('OAuth2')) {
        console.log('   • Verify client ID and secret are correct');
        console.log('   • Check network connectivity to OAuth endpoint');
        console.log('   • Ensure service key is not expired');
      }

      if (error.message.includes('deployment')) {
        console.log('   • Verify Perplexity is deployed in SAP AI Core');
        console.log('   • Check the deployment is in the correct resource group');
        console.log('   • Ensure model name is "perplexity--sonar"');
        console.log('   • Verify you have access to the AI Core instance');
      }

      console.log('\n📚 Documentation:');
      console.log('   • README-SAP-AI-SDK-INTEGRATION.md');
      console.log('   • https://sap.github.io/ai-sdk/');
    } else {
      console.error('\n❌ Unknown error:', error);
    }

    process.exit(1);
  }
}

// Run the test
testFullIntegration();
