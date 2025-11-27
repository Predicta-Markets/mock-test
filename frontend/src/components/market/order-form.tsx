"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { placeOrder } from "@/lib/api";
import type { OrderRequestPayload } from "@/lib/types";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

interface Props {
  marketId: string;
  onSettled?: () => void;
}

const defaultPayload: OrderRequestPayload = {
  side: "YES",
  type: "BUY",
  price: 50,
  quantity: 10,
};

export function OrderForm({ marketId, onSettled }: Props) {
  const [payload, setPayload] = useState<OrderRequestPayload>(defaultPayload);

  const mutation = useMutation({
    mutationFn: () => placeOrder(marketId, payload),
    onSettled,
  });

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        mutation.mutate();
      }}
    >
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-slate-700">Side</Label>
          <Select value={payload.side} onValueChange={(value) => setPayload((prev) => ({ ...prev, side: value as "YES" | "NO" }))}>
            <SelectTrigger className="border-slate-200 bg-white text-slate-900 focus-visible:ring-slate-900/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-slate-200 bg-white text-slate-900">
              <SelectItem value="YES">YES</SelectItem>
              <SelectItem value="NO">NO</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label className="text-slate-700">Type</Label>
          <Select value={payload.type} onValueChange={(value) => setPayload((prev) => ({ ...prev, type: value as "BUY" | "SELL" }))}>
            <SelectTrigger className="border-slate-200 bg-white text-slate-900 focus-visible:ring-slate-900/30">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-slate-200 bg-white text-slate-900">
              <SelectItem value="BUY">Buy</SelectItem>
              <SelectItem value="SELL">Sell</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-slate-700">Price</Label>
          <Input
            type="number"
            min={0}
            max={100}
            step="0.5"
            value={payload.price}
            onChange={(event) => setPayload((prev) => ({ ...prev, price: Number(event.target.value) }))}
            className="border-slate-200"
          />
        </div>
        <div className="space-y-2">
          <Label className="text-slate-700">Quantity</Label>
          <Input
            type="number"
            min={1}
            max={500_000}
            step={1}
            value={payload.quantity}
            onChange={(event) => setPayload((prev) => ({ ...prev, quantity: Number(event.target.value) }))}
            className="border-slate-200"
          />
        </div>
      </div>

      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "Submitting..." : "Submit Order"}
      </Button>
      {mutation.isError && <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>}
    </form>
  );
}

