import type { Metadata } from "next";
import { ResultLoader } from "@/components/result-loader";

export const metadata: Metadata = { title: "Scan result" };

export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ResultLoader id={id} />;
}
