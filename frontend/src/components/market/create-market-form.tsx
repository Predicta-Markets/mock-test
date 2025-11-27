"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { createMarket } from "@/lib/api";
import type { Market } from "@/lib/types";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";

type FormState = {
  question: string;
  description: string;
  initialPrice: number;
};

const defaultState: FormState = {
  question: "",
  description: "",
  initialPrice: 50,
};

export function CreateMarketForm({ onCreated }: { onCreated?: (market: Market) => void }) {
  const [form, setForm] = useState<FormState>(defaultState);

  const mutation = useMutation({
    mutationFn: () =>
      createMarket({
        question: form.question,
        description: form.description,
        initial_price_yes: Number(form.initialPrice),
      }),
    onSuccess: (market) => {
      setForm(defaultState);
      onCreated?.(market);
    },
  });

  const disabled = mutation.isPending;

  return (
    <Card className="border-slate-200 bg-white text-slate-900 shadow-sm">
      <CardHeader className="space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Creator tools</p>
        <CardTitle className="text-xl text-slate-900">Create a market</CardTitle>
        <CardDescription className="text-slate-500">
          Define your question, add optional context, and choose a starting YES price. NO is derived automatically.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            mutation.mutate();
          }}
        >
          <div className="space-y-2">
            <Label htmlFor="question" className="text-slate-700">
              Question
            </Label>
            <Input
              id="question"
              placeholder="Will BTC close above $80k on Dec 31?"
              value={form.question}
              onChange={(event) => setForm((prev) => ({ ...prev, question: event.target.value }))}
              className="border-slate-200 bg-white text-slate-900 placeholder:text-slate-400 focus-visible:ring-slate-900/30"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="text-slate-700">
              Description
            </Label>
            <Textarea
              id="description"
              placeholder="Add resolution criteria or links"
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              className="border-slate-200 bg-white text-slate-900 placeholder:text-slate-400 focus-visible:ring-slate-900/30"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="price" className="text-slate-700">
              Initial YES price (0-100)
            </Label>
            <Input
              id="price"
              type="number"
              min={1}
              max={99}
              step={1}
              value={form.initialPrice}
              onChange={(event) => setForm((prev) => ({ ...prev, initialPrice: Number(event.target.value) }))}
              className="border-slate-200 bg-white text-slate-900 placeholder:text-slate-400 focus-visible:ring-slate-900/30"
              required
            />
          </div>

          <Button type="submit" disabled={disabled} className="w-full">
            {disabled ? "Creating..." : "Create market"}
          </Button>
          {mutation.isError && <p className="text-sm text-rose-500">{(mutation.error as Error).message}</p>}
        </form>
      </CardContent>
    </Card>
  );
}

