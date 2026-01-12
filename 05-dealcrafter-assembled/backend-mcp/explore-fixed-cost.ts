/**
 * Deep Exploration of Fixed Cost OData Service - Monthly Aggregations
 * Goal: Reverse-engineer how monthly aggregations work
 * 
 * KEY INSIGHT: This service uses PARAMETERIZED ENTITY PATH:
 * ZFCGCFC02_Q2(ZFCDFISCYEAR='2024',ZFCDFISCYEARTo='2024',ZF_VAR_JMO1='JPY')/Results
 */

import { queryODataJson } from './src/utils/odataClient';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const SERVICE = 'ZFCGCFC02_Q2_SRV';

function getPath(fiscYear: string = '2024', fiscYearTo?: string, variant: string = 'JPY'): string {
  const toYear = fiscYearTo || fiscYear;
  return `${SERVICE}/ZFCGCFC02_Q2(ZFCDFISCYEAR='${fiscYear}',ZFCDFISCYEARTo='${toYear}',ZF_VAR_JMO1='${variant}')/Results`;
}

interface QueryResult {
  testName: string;
  filter: string;
  select?: string;
  rows: any[];
  elapsed: number;
  error?: string;
}

async function runQuery(
  testName: string,
  filter: string,
  select?: string,
  top: number = 100,
  orderby?: string,
  fiscYear: string = '2024'
): Promise<QueryResult> {
  const path = getPath(fiscYear);
  console.log(`\n${'='.repeat(70)}`);
  console.log(`TEST: ${testName}`);
  console.log(`${'='.repeat(70)}`);
  console.log(`Path: ${path}`);
  console.log(`Filter: ${filter}`);
  if (select) console.log(`Select: ${select}`);
  if (orderby) console.log(`OrderBy: ${orderby}`);
  console.log(`Top: ${top}`);
  
  const startTime = Date.now();
  
  try {
    const response = await queryODataJson(path, {
      top,
      select,
      filter,
      orderby,
    });

    const elapsed = Date.now() - startTime;
    console.log(`Response time: ${elapsed}ms`);

    if (response.status >= 300) {
      console.log(`❌ Error: ${response.status} ${response.statusText}`);
      const body = JSON.stringify(response.json).substring(0, 500);
      console.log(`Body: ${body}`);
      return { testName, filter, select, rows: [], elapsed, error: response.statusText };
    }

    const rows = (response.json as any)?.d?.results || [];
    console.log(`✅ Success: ${rows.length} rows`);
    
    return { testName, filter, select, rows, elapsed };
  } catch (error) {
    const elapsed = Date.now() - startTime;
    console.log(`❌ Exception: ${error}`);
    return { testName, filter, select, rows: [], elapsed, error: String(error) };
  }
}

function analyzeResults(result: QueryResult): void {
  if (result.rows.length === 0) return;
  
  const fiscPerValues = new Set<string>();
  const quarterValues = new Set<string>();
  const costCenterValues = new Set<string>();
  const costElementValues = new Set<string>();
  const amountByPeriod: Record<string, number> = {};
  
  for (const row of result.rows) {
    if (row.A0FISCPER_T) fiscPerValues.add(row.A0FISCPER_T);
    if (row.A0CALQUARTER_T) quarterValues.add(row.A0CALQUARTER_T);
    if (row.A0COSTCENTER) costCenterValues.add(row.A0COSTCENTER);
    if (row.ZFC_COEL1_T) costElementValues.add(row.ZFC_COEL1_T);
    
    const period = row.A0FISCPER_T || 'Unknown';
    const amount = parseFloat(row.ZF_CKF_MILLION) || 0;
    amountByPeriod[period] = (amountByPeriod[period] || 0) + amount;
  }
  
  console.log(`\n--- Analysis ---`);
  console.log(`Fiscal Periods: [${Array.from(fiscPerValues).sort().join(', ')}]`);
  console.log(`Quarters: [${Array.from(quarterValues).join(', ')}]`);
  console.log(`Cost Centers: ${costCenterValues.size} unique`);
  console.log(`Cost Elements: ${costElementValues.size} unique (non-blank)`);
  
  if (Object.keys(amountByPeriod).length > 0 && Object.keys(amountByPeriod).length <= 20) {
    console.log(`\nAmount by Period (ZF_CKF_MILLION sum):`);
    for (const [period, sum] of Object.entries(amountByPeriod).sort()) {
      console.log(`  ${period}: ${sum.toLocaleString()}`);
    }
  }
  
  // Show sample row
  console.log(`\nSample Row (key fields):`);
  const row = result.rows[0];
  const fields = [
    'A0FISCYEAR_T', 'A0FISCPER_T', 'A0CALQUARTER_T', 
    'A0COSTCENTER', 'A0COSTCENTER_T',
    'ZFC_COEL1_T', 'ZFC_COEL1_T_L', 'ZFC_OFF08_T',
    'ZF_CKF_MILLION', 'ZF_CKF_MILLION_F', 'TotaledProperties'
  ];
  for (const f of fields) {
    if (row[f] !== undefined) {
      console.log(`  ${f}: "${row[f]}"`);
    }
  }
}

async function exploreMonthlyAggregations(): Promise<void> {
  // PHASE 1: Basic query to confirm service works
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 1: Confirm Service Works with Parameterized Path');
  console.log('#'.repeat(70));
  
  let result = await runQuery(
    '1.1 Basic query - single cost center',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'A0FISCYEAR_T,A0FISCPER_T,A0CALQUARTER_T,A0COSTCENTER,A0COSTCENTER_T,ZFC_COEL1_T,ZFC_OFF08_T,ZF_CKF_MILLION,ZF_CKF_MILLION_F',
    200
  );
  analyzeResults(result);

  // PHASE 2: Understand period behavior
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 2: Period Field Behavior');
  console.log('#'.repeat(70));
  
  // Test 2.1: Filter by specific period
  result = await runQuery(
    '2.1 Filter by January 2024',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531' and A0FISCPER_T eq 'January 2024'",
    'A0FISCPER_T,A0COSTCENTER,ZFC_COEL1_T,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // Test 2.2: Filter by Q1
  result = await runQuery(
    '2.2 Filter by Q1 2024',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531' and A0CALQUARTER_T eq 'Q1 2024'",
    'A0FISCPER_T,A0CALQUARTER_T,ZFC_COEL1_T,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // PHASE 3: Aggregation patterns
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 3: Aggregation Patterns');
  console.log('#'.repeat(70));

  // Test 3.1: Without period in select - does it aggregate?
  result = await runQuery(
    '3.1 Select WITHOUT period field',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'A0COSTCENTER,ZFC_COEL1_T,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // Test 3.2: Select only amount - maximally aggregated?
  result = await runQuery(
    '3.2 Select only cost center and amount',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'A0COSTCENTER,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // Test 3.3: Check TotaledProperties
  result = await runQuery(
    '3.3 Include TotaledProperties field',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'TotaledProperties,A0FISCPER_T,A0COSTCENTER,ZFC_COEL1_T,ZF_CKF_MILLION',
    50
  );
  if (result.rows.length > 0) {
    console.log('\nTotaledProperties unique values:');
    const totaled = new Set(result.rows.map(r => r.TotaledProperties));
    for (const t of totaled) {
      console.log(`  "${t}"`);
    }
  }

  // PHASE 4: Cost Element hierarchy
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 4: Cost Element Hierarchy Levels');
  console.log('#'.repeat(70));

  // Test 4.1: Level 0 (root)
  result = await runQuery(
    '4.1 Cost Element Level 0 only',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531' and ZFC_COEL1_T_L eq 0",
    'A0FISCPER_T,ZFC_COEL1_T,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // Test 4.2: Level 1
  result = await runQuery(
    '4.2 Cost Element Level 1',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531' and ZFC_COEL1_T_L eq 1",
    'A0FISCPER_T,ZFC_COEL1_T,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    100
  );
  analyzeResults(result);

  // Test 4.3: Level 2 (leaf)
  result = await runQuery(
    '4.3 Cost Element Level 2 (leaf)',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531' and ZFC_COEL1_T_L eq 2",
    'A0FISCPER_T,ZFC_COEL1_T,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    200
  );
  analyzeResults(result);

  // PHASE 5: Monthly totals calculation
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 5: Monthly Total Calculation');
  console.log('#'.repeat(70));

  // Get all data and calculate monthly totals client-side
  result = await runQuery(
    '5.1 All data for cost center - large fetch',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'A0FISCPER_T,ZFC_COEL1_T,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    2000
  );
  
  if (result.rows.length > 0) {
    // Calculate monthly totals by hierarchy level
    const monthlyByLevel: Record<number, Record<string, number>> = {};
    
    for (const row of result.rows) {
      const month = row.A0FISCPER_T || 'Unknown';
      const level = row.ZFC_COEL1_T_L ?? -1;
      const amount = parseFloat(row.ZF_CKF_MILLION) || 0;
      
      if (!monthlyByLevel[level]) monthlyByLevel[level] = {};
      monthlyByLevel[level][month] = (monthlyByLevel[level][month] || 0) + amount;
    }
    
    console.log('\n=== MONTHLY TOTALS BY HIERARCHY LEVEL ===');
    for (const [level, months] of Object.entries(monthlyByLevel).sort((a, b) => Number(a[0]) - Number(b[0]))) {
      console.log(`\nLevel ${level}:`);
      const sortedMonths = Object.entries(months).sort();
      for (const [month, total] of sortedMonths) {
        console.log(`  ${month}: ${total.toLocaleString()}`);
      }
    }

    // Sum only leaf-level to avoid double counting
    console.log('\n=== LEAF LEVEL (2) MONTHLY TOTALS ===');
    if (monthlyByLevel[2]) {
      let grandTotal = 0;
      for (const [month, total] of Object.entries(monthlyByLevel[2]).sort()) {
        console.log(`  ${month}: ${total.toLocaleString()}`);
        grandTotal += total;
      }
      console.log(`  TOTAL: ${grandTotal.toLocaleString()}`);
    }
  }

  // PHASE 6: Office hierarchy impact
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 6: Office Hierarchy and Aggregation');
  console.log('#'.repeat(70));

  result = await runQuery(
    '6.1 By Office L1 (CEO)',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and ZFC_OFF08_T eq 'CEO'",
    'A0FISCPER_T,ZFC_OFF08_T,A0COSTCENTER,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    500
  );
  
  if (result.rows.length > 0) {
    // Monthly by office
    const monthlyTotals: Record<string, number> = {};
    const costCentersInOffice = new Set<string>();
    
    for (const row of result.rows) {
      const month = row.A0FISCPER_T || 'Unknown';
      const amount = parseFloat(row.ZF_CKF_MILLION) || 0;
      monthlyTotals[month] = (monthlyTotals[month] || 0) + amount;
      if (row.A0COSTCENTER) costCentersInOffice.add(row.A0COSTCENTER);
    }
    
    console.log(`\nCost Centers in CEO office: ${costCentersInOffice.size}`);
    console.log(`Sample: ${Array.from(costCentersInOffice).slice(0, 5).join(', ')}`);
    
    console.log('\nMonthly totals for CEO office:');
    for (const [month, total] of Object.entries(monthlyTotals).sort()) {
      console.log(`  ${month}: ${total.toLocaleString()}`);
    }
  }

  // PHASE 7: Cross-year comparison
  console.log('\n' + '#'.repeat(70));
  console.log('# PHASE 7: Year Comparison');
  console.log('#'.repeat(70));

  result = await runQuery(
    '7.1 FY2023 data for same cost center',
    "A0CO_AREA eq '6004' and A0COMP_CODE eq '6200' and A0COSTCENTER eq '6202-5531'",
    'A0FISCPER_T,ZFC_COEL1_T_L,ZF_CKF_MILLION',
    1000,
    undefined,
    '2023'
  );
  
  if (result.rows.length > 0) {
    const monthly2023: Record<string, number> = {};
    for (const row of result.rows) {
      if (row.ZFC_COEL1_T_L === 2) { // Leaf level only
        const month = row.A0FISCPER_T || 'Unknown';
        const amount = parseFloat(row.ZF_CKF_MILLION) || 0;
        monthly2023[month] = (monthly2023[month] || 0) + amount;
      }
    }
    
    console.log('\n2023 Monthly (Leaf Level):');
    for (const [month, total] of Object.entries(monthly2023).sort()) {
      console.log(`  ${month}: ${total.toLocaleString()}`);
    }
  }
}

async function main(): Promise<void> {
  console.log('============================================================');
  console.log('FIXED COST SERVICE - MONTHLY AGGREGATION DEEP DIVE');
  console.log('============================================================');
  console.log('');
  
  await exploreMonthlyAggregations();
  
  console.log('\n' + '='.repeat(70));
  console.log('EXPLORATION COMPLETE');
  console.log('='.repeat(70));
}

main().catch(console.error);
