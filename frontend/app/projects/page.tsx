"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { TopNav } from "@/components/top-nav";
import { apiRequest } from "@/lib/api";
import { Project } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    try {
      const data = await apiRequest<Project[]>("/projects");
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const formEl = event.currentTarget;
    const formData = new FormData(formEl);
    const name = String(formData.get("name") ?? "");
    const description = String(formData.get("description") ?? "");

    try {
      await apiRequest("/projects", {
        method: "POST",
        body: JSON.stringify({ name, description: description || null })
      });
      formEl.reset();
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    }
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <TopNav />
      <section className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Projects</h1>

        <form onSubmit={onCreate} className="mt-6 grid gap-3 rounded border border-slate-200 bg-white p-4 md:grid-cols-4">
          <input required name="name" placeholder="Project name" className="rounded border border-slate-300 px-3 py-2 text-sm" />
          <input name="description" placeholder="Description" className="rounded border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
          <button type="submit" className="rounded bg-brand-600 px-3 py-2 text-sm font-medium text-white">Create</button>
        </form>

        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}

        <div className="mt-6 overflow-hidden rounded border border-slate-200 bg-white">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-slate-100 text-left text-slate-600">
              <tr>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Description</th>
                <th className="px-3 py-2 font-medium">Created</th>
                <th className="px-3 py-2 font-medium">Open</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id} className="border-t border-slate-200">
                  <td className="px-3 py-2">{project.name}</td>
                  <td className="px-3 py-2 text-slate-600">{project.description ?? "-"}</td>
                  <td className="px-3 py-2 text-slate-600">{new Date(project.created_at).toLocaleDateString()}</td>
                  <td className="px-3 py-2">
                    <Link className="text-brand-700" href={`/projects/${project.id}`}>
                      View
                    </Link>
                  </td>
                </tr>
              ))}
              {!projects.length ? (
                <tr>
                  <td colSpan={4} className="px-3 py-6 text-center text-slate-500">
                    No projects yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
