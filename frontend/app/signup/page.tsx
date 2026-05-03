"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const form = new FormData(event.currentTarget);
    const name = String(form.get("name") ?? "");
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");

    try {
      await apiRequest("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ name, email, password })
      });
      await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Signup failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto mt-20 max-w-md px-4">
      <h1 className="text-2xl font-semibold text-slate-900">Create account</h1>
      <p className="mt-2 text-sm text-slate-600">Start managing projects in minutes.</p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <label className="block text-sm">
          <span className="mb-1 block text-slate-700">Name</span>
          <input
            required
            type="text"
            name="name"
            className="w-full rounded border border-slate-300 bg-white px-3 py-2"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-700">Email</span>
          <input
            required
            type="email"
            name="email"
            className="w-full rounded border border-slate-300 bg-white px-3 py-2"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-1 block text-slate-700">Password</span>
          <input
            required
            minLength={8}
            type="password"
            name="password"
            className="w-full rounded border border-slate-300 bg-white px-3 py-2"
          />
        </label>

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <button
          disabled={loading}
          type="submit"
          className="w-full rounded bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="mt-4 text-sm text-slate-600">
        Already have one? <Link href="/login" className="text-brand-700">Sign in</Link>
      </p>
    </main>
  );
}
