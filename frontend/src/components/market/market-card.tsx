"use client";

import Link from "next/link";

import type { Market } from "@/lib/types";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";

export function MarketCard({ market }: { market: Market }) {
  const badgeVariant = market.status === "OPEN" ? "success" : "warning";
  const badgeLabel = market.status === "OPEN" ? "Open" : `Resolved (${market.outcome ?? "TBD"})`;

  return (
    <Card className="flex flex-col justify-between border border-slate-200 bg-white shadow-sm transition hover:shadow-sm">
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-base text-slate-900 line-clamp-1">{market.question}</CardTitle>
          <Badge variant={badgeVariant}>{badgeLabel}</Badge>
        </div>
        {market.description && <CardDescription className="text-sm text-slate-500 line-clamp-2">{market.description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex items-center gap-4 text-sm">
          <div className="flex-1 border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-500">YES price</p>
            <p className="text-2xl font-semibold text-slate-900">{Number(market.yes_price).toFixed(2)}</p>
          </div>
          <div className="flex-1 border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-500">NO price</p>
            <p className="text-2xl font-semibold text-slate-900">{Number(market.no_price).toFixed(2)}</p>
          </div>
        </div>
        <Button asChild className="w-full">
          <Link href={`/markets/${market.id}`}>Open market</Link>
        </Button>
      </CardContent>
    </Card>
  );
}

