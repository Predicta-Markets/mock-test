"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { CreateMarketForm } from "@/components/market/create-market-form";
import { MarketCard } from "@/components/market/market-card";
import { Breadcrumbs } from "@/components/navigation/breadcrumbs";
import { fetchMarkets } from "@/lib/api";

export default function HomePage() {
    const { data: markets, isLoading, error, refetch } = useQuery({
        queryKey: ["markets"],
        queryFn: fetchMarkets,
    });
    const [isCreateOpen, setCreateOpen] = useState(false);

    const totalMarkets = markets?.length ?? 0;
    const openMarkets = markets?.filter((market) => market.status === "OPEN").length ?? 0;
    const resolvedMarkets = totalMarkets - openMarkets;

    const breadcrumbs = [
        { label: "Home", href: "/" },
        { label: "Markets" },
    ];

    const heroStats = [
        { label: "Open markets", value: openMarkets },
        { label: "Resolved", value: resolvedMarkets },
        { label: "Total listed", value: totalMarkets },
    ];

    const handleMarketCreated = () => {
        refetch();
        setCreateOpen(false);
    };

    return (
        <main className="flex w-full flex-col gap-4 px-6 py-6">
            <Breadcrumbs items={breadcrumbs} />
            <section className="border border-slate-200 bg-white p-8 shadow-sm">
                <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-4">
                        <div>
                            <h1 className="text-3xl font-semibold text-slate-900 md:text-4xl">Create and trade binary markets.</h1>
                        </div>
                        <div className="flex flex-wrap items-center gap-3">
                            <button
                                className="inline-flex items-center rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
                                onClick={() => refetch()}
                            >
                                Refresh markets
                            </button>
                            {error && <span className="text-sm text-rose-500">Unable to load markets. Try again?</span>}
                        </div>
                    </div>
                    <div className="grid w-full max-w-md grid-cols-3 gap-3 rounded-2xl p-2">
                        <button
                            className="mt-4 inline-flex items-center justify-center border border-slate-200 bg-white px-5 py-2 text-sm font-medium text-slate-900 shadow-sm transition hover:border-slate-300"
                            onClick={() => setCreateOpen(true)}
                        >
                            New Market
                        </button>
                    </div>

                </div>
            </section>

            <section className="grid gap-6">
                <div className="border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="mb-6 flex items-center justify-between">
                        <div>
                            <p className="text-xs uppercase tracking-wide text-slate-500">Live markets</p>
                            <h2 className="text-xl font-semibold text-slate-900">Order book overview</h2>
                        </div>
                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                            {isLoading ? "Loading..." : `${openMarkets} open`}
                        </span>
                    </div>

                    {isLoading && <p className="text-sm text-slate-500">Fetching markets...</p>}
                    {!isLoading && !markets?.length && <p className="text-sm text-slate-500">No markets created yet.</p>}

                    <div className="grid gap-3 md:grid-cols-3">
                        {markets?.map((market) => (
                            <MarketCard key={market.id} market={market} />
                        ))}
                    </div>
                </div>
            </section>

            {isCreateOpen && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4 py-10"
                    role="dialog"
                    aria-modal="true"
                    aria-label="Create market dialog"
                >
                    <div className="relative w-full max-w-2xl">
                        <button
                            aria-label="Close create market dialog"
                            className="absolute -right-2 -top-2 inline-flex h-10 w-10 items-center justify-center rounded-full bg-white text-slate-600 shadow-md transition hover:text-slate-900"
                            onClick={() => setCreateOpen(false)}
                        >
                            ×
                        </button>
                        <CreateMarketForm onCreated={handleMarketCreated} />
                    </div>
                </div>
            )}
        </main>
    );
}

