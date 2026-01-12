#!/usr/bin/env tsx
import { DeploymentApi } from '@sap-ai-sdk/ai-api';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

async function findSonar() {
  const resourceGroup = process.env.SAP_AI_RESOURCE_GROUP || 'default';
  console.log(`\n🔍 Searching for Sonar/Perplexity in resource group: ${resourceGroup}\n`);

  const deployments = await DeploymentApi.deploymentQuery(
    {},
    { 'AI-Resource-Group': resourceGroup }
  ).execute();
  
  console.log(`Total deployments: ${deployments.resources.length}\n`);
  
  deployments.resources.forEach((d, i) => {
    const modelName = d.details?.resources?.backendDetails?.model?.name || 
                     d.details?.resources?.backend_details?.model?.name || 
                     'N/A';
    
    console.log(`${i + 1}. ID: ${d.id}`);
    console.log(`   Status: ${d.status}`);
    console.log(`   Scenario: ${d.scenarioId}`);
    console.log(`   Model: ${modelName}`);
    console.log(`   URL: ${d.deploymentUrl}`);
    console.log('');
  });
}

findSonar();
