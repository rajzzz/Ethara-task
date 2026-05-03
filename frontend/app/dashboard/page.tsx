"use client";

import { useEffect, useState } from "react";

import { TopNav } from "@/components/top-nav";
import { apiRequest } from "@/lib/api";
import { DashboardStats } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRequest<DashboardStats>("/dashboard")
      .then(setStats)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main className="min-h-screen bg-slate-50">
      <TopNav />
      <section className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>

        {error ? <p className="mt-4 text-sm text-rose-600">{error}</p> : null}

        {!stats ? (
          <p className="mt-4 text-sm text-slate-600">Loading stats...</p>
        ) : (
          <div className="mt-6 grid gap-4 md:grid-cols-4">
            <div className="rounded border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">Total tasks</p>
              <p className="mt-2 text-2xl font-semibold">{stats.total_tasks}</p>
            </div>
            <div className="rounded border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">Overdue</p>
              <p className="mt-2 text-2xl font-semibold text-rose-600">{stats.overdue_tasks}</p>
            </div>
            <div className="rounded border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">Todo</p>
              <p className="mt-2 text-2xl font-semibold">{stats.by_status.todo ?? 0}</p>
            </div>
            <div className="rounded border border-slate-200 bg-white p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">In Progress / Done</p>
              <p className="mt-2 text-2xl font-semibold">
                {(stats.by_status.in_progress ?? 0) + (stats.by_status.done ?? 0)}
              </p>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
