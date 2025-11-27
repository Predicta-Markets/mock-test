"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useCallback } from "react";

import { fetchMarket, fetchOrderBook, fetchPositions, resolveMarket } from "@/lib/api";
import { Breadcrumbs } from "../navigation/breadcrumbs";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../ui/table";
import { OrderForm } from "./order-form";

interface Props {
  marketId: string;
}

export function MarketDetail({ marketId }: Props) {
  const {
    data: market,
    isLoading: loadingMarket,
    error: marketError,
    refetch: refetchMarket,
  } = useQuery({
    queryKey: ["market", marketId],
    queryFn: () => fetchMarket(marketId),
  });

  const {
    data: positions,
    isLoading: loadingPositions,
    refetch: refetchPositions,
  } = useQuery({
    queryKey: ["positions", marketId],
    queryFn: () => fetchPositions(marketId),
  });

  const {
    data: orderBookLevels,
    isLoading: loadingOrderBook,
    refetch: refetchOrderBook,
  } = useQuery({
    queryKey: ["orderBook", marketId],
    queryFn: () => fetchOrderBook(marketId),
  });

  const refetchAll = useCallback(() => {
    refetchMarket();
    refetchPositions();
    refetchOrderBook();
  }, [refetchMarket, refetchOrderBook, refetchPositions]);

  const resolveMutation = useMutation({
    mutationFn: (outcome: "YES" | "NO") => resolveMarket(marketId, outcome),
    onSuccess: () => refetchAll(),
  });

  if (loadingMarket) {
    return <p className="text-muted-foreground">Loading market...</p>;
  }

  if (marketError || !market) {
    return <p className="text-destructive">Unable to load market.</p>;
  }

  const breadcrumbs = [
    { label: "Home", href: "/" },
    { label: "Markets", href: "/" },
    { label: market.question },
  ];

  return (
    <div className="grid gap-3 lg:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
      <div className="lg:col-span-2 space-y-2">
        <Breadcrumbs items={breadcrumbs} />
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-none border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            ← Back to markets
          </Link>
        </div>
      </div>
      <div className="flex flex-col gap-3">
        <Card className="border-slate-200 rounded-none">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle>{market.question}</CardTitle>
                {market.description && <CardDescription>{market.description}</CardDescription>}
              </div>
              <Badge variant={market.status === "OPEN" ? "success" : "warning"}>
                {market.status === "OPEN" ? "Open" : `Resolved (${market.outcome ?? "TBD"})`}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm sm:grid-cols-2">
            <div className="border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">YES Price</p>
              <p className="text-3xl font-semibold text-slate-900">{Number(market.yes_price).toFixed(2)}</p>
            </div>
            <div className="border border-slate-200 bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">NO Price</p>
              <p className="text-3xl font-semibold text-slate-900">{Number(market.no_price).toFixed(2)}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 rounded-none">
          <CardHeader>
            <CardTitle>Positions</CardTitle>
            <CardDescription>Weighted averages and realized P/L per side</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingPositions ? (
              <p className="text-muted-foreground text-sm">Loading positions...</p>
            ) : positions?.length ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Side</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Average Cost</TableHead>
                    <TableHead>Realized P/L</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {positions.map((position) => (
                    <TableRow key={position.side}>
                      <TableCell>{position.side}</TableCell>
                      <TableCell>{position.quantity}</TableCell>
                      <TableCell>{Number(position.average_price).toFixed(2)}</TableCell>
                      <TableCell className={position.realized_pnl >= 0 ? "text-emerald-600" : "text-rose-600"}>
                        {Number(position.realized_pnl).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-sm text-muted-foreground">No positions yet.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col gap-3">
        <Card className="border-slate-200 rounded-none">
          <CardHeader>
            <CardTitle>Order book</CardTitle>
            <CardDescription>Resting limit orders waiting for a match</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingOrderBook ? (
              <p className="text-sm text-muted-foreground">Loading book...</p>
            ) : orderBookLevels?.length ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {(["YES", "NO"] as const).map((side) => {
                  const levels = [...(orderBookLevels ?? [])]
                    .filter((level) => level.side === side)
                    .sort((a, b) => Number(b.price) - Number(a.price));
                  return (
                    <div key={side}>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{side} offers</p>
                      {levels.length ? (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Price</TableHead>
                              <TableHead>Quantity</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {levels.map((level) => (
                              <TableRow key={level.id}>
                                <TableCell>{Number(level.price).toFixed(2)}</TableCell>
                                <TableCell>{level.quantity}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      ) : (
                        <p className="text-sm text-muted-foreground">No resting orders.</p>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No resting orders yet.</p>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-200 rounded-none">
          <CardHeader>
            <CardTitle>Place order</CardTitle>
            <CardDescription>Orders update holdings immediately; sells require existing inventory.</CardDescription>
          </CardHeader>
          <CardContent>
            <OrderForm marketId={market.id} onSettled={refetchAll} />
          </CardContent>
        </Card>

        <Card className="border-slate-200 rounded-none">
          <CardHeader>
            <CardTitle>Resolve market</CardTitle>
            <CardDescription>Lock in payouts for the winning side. This cannot be undone.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button variant="outline" onClick={() => resolveMutation.mutate("YES")} disabled={resolveMutation.isPending}>
              Resolve YES
            </Button>
            <Button variant="outline" onClick={() => resolveMutation.mutate("NO")} disabled={resolveMutation.isPending}>
              Resolve NO
            </Button>
            {resolveMutation.isError && <p className="text-sm text-destructive">{(resolveMutation.error as Error).message}</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

