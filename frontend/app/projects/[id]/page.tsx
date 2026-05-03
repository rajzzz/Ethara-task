"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { StatusDot } from "@/components/status-dot";
import { TopNav } from "@/components/top-nav";
import { apiRequest } from "@/lib/api";
import { Task, TaskPriority, TaskStatus } from "@/lib/types";

const statuses: TaskStatus[] = ["todo", "in_progress", "done"];

export default function ProjectBoardPage() {
  const params = useParams<{ id: string }>();
  const projectId = Number(params.id);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadTasks() {
    try {
      const data = await apiRequest<Task[]>(`/projects/${projectId}/tasks`);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    }
  }

  useEffect(() => {
    loadTasks();
  }, [projectId]);

  async function onCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formEl = event.currentTarget;
    const form = new FormData(formEl);

    const payload = {
      title: String(form.get("title") ?? ""),
      description: String(form.get("description") ?? "") || null,
      priority: String(form.get("priority") ?? "medium") as TaskPriority,
      due_date: String(form.get("due_date") ?? "") || null
    };

    try {
      await apiRequest(`/projects/${projectId}/tasks`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      formEl.reset();
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    }
  }

  async function moveStatus(taskId: number, status: TaskStatus) {
    const previous = tasks;
    setTasks((curr) => curr.map((task) => (task.id === taskId ? { ...task, status } : task)));

    try {
      await apiRequest(`/tasks/${taskId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status })
      });
    } catch (err) {
      setTasks(previous);
      setError(err instanceof Error ? err.message : "Failed to update status");
    }
  }

  const grouped = useMemo(() => {
    return {
      todo: tasks.filter((task) => task.status === "todo"),
      in_progress: tasks.filter((task) => task.status === "in_progress"),
      done: tasks.filter((task) => task.status === "done")
    };
  }, [tasks]);

  return (
    <main className="min-h-screen bg-slate-50">
      <TopNav />
      <section className="mx-auto max-w-7xl px-4 py-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold">Project Board</h1>
          <Link href={`/projects/${projectId}/settings`} className="text-sm text-brand-700">
            Project settings
          </Link>
        </div>

        <form onSubmit={onCreateTask} className="mt-6 grid gap-2 rounded border border-slate-200 bg-white p-3 md:grid-cols-5">
          <input required name="title" placeholder="Task title" className="rounded border border-slate-300 px-2 py-1.5 text-sm" />
          <input name="description" placeholder="Description" className="rounded border border-slate-300 px-2 py-1.5 text-sm md:col-span-2" />
          <select name="priority" className="rounded border border-slate-300 px-2 py-1.5 text-sm">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <div className="flex gap-2">
            <input type="date" name="due_date" className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
            <button className="rounded bg-brand-600 px-3 py-1.5 text-sm font-medium text-white">Add</button>
          </div>
        </form>

        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}

        <div className="mt-6 hidden gap-4 md:grid md:grid-cols-3">
          {statuses.map((status) => (
            <div key={status} className="rounded border border-slate-200 bg-white">
              <div className="border-b border-slate-200 px-3 py-2 text-sm font-semibold capitalize">
                {status.replace("_", " ")}
              </div>
              <div className="space-y-2 p-3">
                {grouped[status].map((task) => (
                  <div key={task.id} className="rounded border border-slate-200 p-2">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium">{task.title}</p>
                      <StatusDot status={task.status} />
                    </div>
                    <p className="mt-1 text-xs text-slate-600">{task.description ?? "No description"}</p>
                    <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                      <span className="uppercase">{task.priority}</span>
                      <select
                        value={task.status}
                        onChange={(event) => moveStatus(task.id, event.target.value as TaskStatus)}
                        className="rounded border border-slate-300 px-1 py-1"
                      >
                        {statuses.map((next) => (
                          <option key={next} value={next}>
                            {next}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
                {!grouped[status].length ? <p className="text-xs text-slate-500">No tasks</p> : null}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 overflow-hidden rounded border border-slate-200 bg-white md:hidden">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-slate-100 text-left text-slate-600">
              <tr>
                <th className="px-2 py-2 font-medium">Task</th>
                <th className="px-2 py-2 font-medium">Status</th>
                <th className="px-2 py-2 font-medium">Priority</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-t border-slate-200">
                  <td className="px-2 py-2">{task.title}</td>
                  <td className="px-2 py-2">
                    <div className="flex items-center gap-2">
                      <StatusDot status={task.status} />
                      <select
                        value={task.status}
                        onChange={(event) => moveStatus(task.id, event.target.value as TaskStatus)}
                        className="rounded border border-slate-300 px-1 py-1 text-xs"
                      >
                        {statuses.map((next) => (
                          <option key={next} value={next}>
                            {next}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                  <td className="px-2 py-2 uppercase">{task.priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
