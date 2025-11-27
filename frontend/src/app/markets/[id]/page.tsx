import { MarketDetail } from "@/components/market/market-detail";

interface Props {
  params: { id: string };
}

export default function MarketPage({ params }: Props) {
  return (
    <main className="flex w-full flex-col gap-4 px-6 py-6">
      <MarketDetail marketId={params.id} />
    </main>
  );
}

