import { logDebug, logError } from './logger';

let cachedToken: string | null = null;
let cachedTokenExpiry: number | null = null;

function getEnvVar(name: string, optional = false): string | undefined {
  const value = process.env[name];
  if (!value && !optional) {
    throw new Error(`Missing required environment variable ${name} for OData proxy`);
  }
  return value;
}

function getMaxTop(): number | null {
  const raw = getEnvVar('ODATA_MAX_TOP', true);
  if (!raw || raw === '0') {
    return null;
  }
  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

async function getAccessToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && cachedTokenExpiry && now < cachedTokenExpiry - 30000) {
    return cachedToken;
  }

  const tokenUrl = getEnvVar('ODATA_TOKEN_URL')!;
  const clientId = getEnvVar('ODATA_CLIENT_ID')!;
  const clientSecret = getEnvVar('ODATA_CLIENT_SECRET')!;

  const body = new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: clientId,
    client_secret: clientSecret,
  });

  const response = await fetch(tokenUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body,
  });

  const text = await response.text();
  if (!response.ok) {
    logError('OData token request failed', new Error(`${response.status} ${response.statusText}: ${text}`));
    throw new Error(`Failed to obtain OData access token: ${response.status} ${response.statusText}`);
  }

  let json: any = null;
  try {
    json = text ? JSON.parse(text) : {};
  } catch {
    json = {};
  }

  const accessToken = typeof json.access_token === 'string' ? json.access_token : undefined;
  if (!accessToken) {
    throw new Error('OData token response did not contain access_token');
  }

  const expiresIn = typeof json.expires_in === 'number' ? json.expires_in : 300;
  cachedToken = accessToken;
  cachedTokenExpiry = now + expiresIn * 1000;
  logDebug('Obtained new OData access token');
  return accessToken;
}

export type ODataQueryOptions = {
  top?: number;
  skip?: number;
  select?: string;
  filter?: string;
  orderby?: string;
  inlinecount?: boolean;
};

export type ODataResponse = {
  url: string;
  status: number;
  statusText: string;
  json: unknown;
};

export async function queryODataJson(path: string, options: ODataQueryOptions = {}): Promise<ODataResponse> {
  const baseUrl = getEnvVar('ODATA_PROXY_BASE_URL')!;
  const maxTop = getMaxTop();

  let top = options.top;
  if (typeof top === 'number' && maxTop && top > maxTop) {
    top = maxTop;
  }

  const params = new URLSearchParams();
  if (top != null) {
    params.set('$top', String(top));
  }
  if (options.skip != null) {
    params.set('$skip', String(options.skip));
  }
  if (options.select) {
    params.set('$select', options.select);
  }
  if (options.filter) {
    params.set('$filter', options.filter);
  }
  if (options.orderby) {
    params.set('$orderby', options.orderby);
  }
  if (options.inlinecount) {
    params.set('$inlinecount', 'allpages');
  }

  const queryString = params.toString();
  const urlBase = baseUrl.replace(/\/$/, '');
  const url = `${urlBase}/odata/sap/opu/odata/sap/${path}${queryString ? `?${queryString}` : ''}`;

  const token = await getAccessToken();

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    },
  });

  const text = await response.text();
  let json: unknown = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = text;
  }

  if (!response.ok) {
    logError('OData request failed', new Error(`${response.status} ${response.statusText}`));
  } else {
    logDebug(`OData request succeeded: ${url}`);
  }

  return {
    url,
    status: response.status,
    statusText: response.statusText,
    json,
  };
}
