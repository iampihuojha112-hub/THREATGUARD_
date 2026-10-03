export type ScanType = "email" | "url" | "sms";
/** "phishing" means "threat" for every scan type: phishing email, malicious URL or scam SMS. */
export type Prediction = "phishing" | "safe";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type Severity = "low" | "medium" | "high";

export interface Factor {
  type: string;
  title: string;
  severity: Severity;
  detail: string;
  evidence: string[];
}

export interface TermContribution {
  term: string;
  weight: number;
  direction: "phishing" | "legitimate";
}

export interface Explanation {
  summary: string;
  factors: Factor[];
  top_terms: TermContribution[];
}

export interface ScanResult {
  id: string;
  scan_type: ScanType;
  subject: string;
  sender: string;
  body: string;
  prediction: Prediction;
  probability: number;
  risk_score: number;
  confidence_score: number;
  risk_level: RiskLevel;
  explanation: Explanation;
  created_at: string;
}

export interface ScanSummary {
  id: string;
  scan_type: ScanType;
  title: string;
  subject: string;
  sender: string;
  prediction: Prediction;
  risk_score: number;
  confidence_score: number;
  created_at: string;
}

export interface HistoryResponse {
  items: ScanSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HistoryQuery {
  page: number;
  pageSize: number;
  search: string;
  prediction: "" | Prediction;
  scanType: "" | ScanType;
  sort: "newest" | "oldest" | "risk_desc" | "risk_asc";
}

export interface DashboardData {
  metrics: {
    total_scans: number;
    phishing_detected: number;
    safe_emails: number;
    average_risk_score: number;
    email_scans: number;
    url_scans: number;
    sms_scans: number;
  };
  weekly_trend: { week: string; phishing: number; safe: number }[];
  daily_activity: { date: string; scans: number }[];
  risk_distribution: { range: string; count: number }[];
  phishing_vs_safe: { name: string; value: number }[];
  type_distribution: { type: ScanType; name: string; value: number; threats: number }[];
  recent_activity: RecentScan[];
}

export interface RecentScan {
  id: string;
  scan_type: ScanType;
  title: string;
  prediction: Prediction;
  risk_score: number;
  created_at: string;
}

export interface AnalyzePayload {
  subject: string;
  sender: string;
  body: string;
}

export interface AnalyzeUrlPayload {
  url: string;
}

export interface AnalyzeSmsPayload {
  message: string;
  sender: string;
}
