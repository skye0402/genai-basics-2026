#!/usr/bin/env tsx
/**
 * List all deployments in SAP AI Core to find the correct model name
 */

import { DeploymentApi } from '@sap-ai-sdk/ai-api';
import * as dotenv from 'dotenv';

// Load environment variables from .env.local
dotenv.config({ path: '.env.local' });

async function listDeployments() {
  console.log('\n📋 Listing All Deployments in SAP AI Core');
  console.log('═'.repeat(70));

  if (!process.env.AICORE_SERVICE_KEY) {
    console.error('❌ AICORE_SERVICE_KEY not found in environment');
    process.exit(1);
  }

  const resourceGroup = process.env.SAP_AI_RESOURCE_GROUP || 'default';
  console.log(`\n🔍 Resource Group: ${resourceGroup}\n`);

  try {
    const deployments = await DeploymentApi.deploymentQuery(
      {}, // query parameters (empty for all deployments)
      { 'AI-Resource-Group': resourceGroup } // header parameters - REQUIRED
    ).execute();

    if (!deployments || deployments.resources.length === 0) {
      console.log('❌ No deployments found in this resource group');
      console.log('\n💡 Tips:');
      console.log('   • Check if deployments exist in SAP AI Core');
      console.log('   • Verify the resource group name is correct');
      console.log(`   • Current resource group: ${resourceGroup}`);
      process.exit(1);
    }

    console.log(`✅ Found ${deployments.resources.length} deployment(s):\n`);

    deployments.resources.forEach((deployment, index) => {
      console.log(`${index + 1}. Deployment ID: ${deployment.id}`);
      console.log(`   Status: ${deployment.status}`);
      console.log(`   Scenario ID: ${deployment.scenarioId || 'N/A'}`);
      console.log(`   Configuration ID: ${deployment.configurationId || 'N/A'}`);
      console.log(`   Deployment URL: ${deployment.deploymentUrl || 'N/A'}`);
      console.log(`   Created: ${deployment.createdAt || 'N/A'}`);
      console.log(`   Modified: ${deployment.modifiedAt || 'N/A'}`);
      
      // Show details if available
      if (deployment.details) {
        console.log(`   Details:`);
        if (deployment.details.resources) {
          console.log(`      Resources: ${JSON.stringify(deployment.details.resources)}`);
        }
        if (deployment.details.scaling) {
          console.log(`      Scaling: ${JSON.stringify(deployment.details.scaling)}`);
        }
      }
      
      console.log('');
    });

    // Look for Perplexity-related deployments
    const perplexityDeployments = deployments.resources.filter(d => 
      d.scenarioId?.toLowerCase().includes('perplexity') ||
      d.configurationId?.toLowerCase().includes('perplexity') ||
      d.id?.toLowerCase().includes('perplexity')
    );

    if (perplexityDeployments.length > 0) {
      console.log('\n🎯 Perplexity-related deployments found:');
      perplexityDeployments.forEach(d => {
        console.log(`   • ${d.id} (${d.scenarioId})`);
        console.log(`     URL: ${d.deploymentUrl}`);
      });
    } else {
      console.log('\n⚠️  No Perplexity deployments found');
      console.log('   You may need to deploy Perplexity in SAP AI Core first');
    }

    // Show foundation model deployments
    const foundationModels = deployments.resources.filter(d => 
      d.scenarioId?.toLowerCase().includes('foundation')
    );

    if (foundationModels.length > 0) {
      console.log('\n📚 Foundation Model deployments:');
      foundationModels.forEach(d => {
        console.log(`   • ${d.id} (${d.scenarioId})`);
      });
    }

  } catch (error) {
    console.error('\n❌ Error listing deployments:', error);
    if (error instanceof Error) {
      console.error('   Message:', error.message);
    }
    process.exit(1);
  }
}

listDeployments();
