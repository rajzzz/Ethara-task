"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/projects", label: "Projects" }
];

export function TopNav() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-sm font-semibold text-slate-900">
            Ethara
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            {navItems.map((item) => {
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={active ? "text-brand-700" : "text-slate-600 hover:text-slate-900"}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <button
          type="button"
          onClick={async () => {
            await apiRequest("/auth/logout", { method: "POST" });
            router.push("/login");
            router.refresh();
          }}
          className="text-sm text-slate-500 hover:text-slate-900"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
