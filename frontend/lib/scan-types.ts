import { Link2, Mail, MessageSquare, type LucideIcon } from "lucide-react";
import type { Prediction, ScanType } from "@/types";

interface ScanMeta {
  label: string;
  /** What a positive verdict is called for this type. */
  threat: string;
  /** Singular noun for the analyzed content. */
  noun: string;
  href: string;
  icon: LucideIcon;
  /** Chart / badge color for this type. */
  color: string;
}

export const SCAN_TYPES: ScanType[] = ["email", "url", "sms"];

export const SCAN_META: Record<ScanType, ScanMeta> = {
  email: { label: "Email", threat: "Phishing", noun: "email", href: "/analyze", icon: Mail, color: "#8b5cf6" },
  url: { label: "URL", threat: "Malicious", noun: "URL", href: "/analyze/url", icon: Link2, color: "#3b82f6" },
  sms: { label: "SMS", threat: "Scam", noun: "message", href: "/analyze/sms", icon: MessageSquare, color: "#14b8a6" },
};

export function verdictLabel(type: ScanType, prediction: Prediction) {
  return prediction === "safe" ? "Safe" : SCAN_META[type].threat;
}
