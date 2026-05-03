"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { TopNav } from "@/components/top-nav";
import { apiRequest } from "@/lib/api";
import { ProjectMember, ProjectRole, User } from "@/lib/types";

export default function ProjectSettingsPage() {
  const params = useParams<{ id: string }>();
  const projectId = Number(params.id);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadMembers() {
    try {
      const data = await apiRequest<ProjectMember[]>(`/projects/${projectId}/members`);
      setMembers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load members");
    }
  }

  useEffect(() => {
    apiRequest<User>("/auth/me")
      .then(setCurrentUser)
      .catch(() => setCurrentUser(null));
    loadMembers();
  }, [projectId]);

  const currentMembership = members.find((member) => member.user_id === currentUser?.id);
  const isAdmin = currentMembership?.role === "admin";

  async function onInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formEl = event.currentTarget;
    const form = new FormData(formEl);
    const email = String(form.get("email") ?? "");
    const role = String(form.get("role") ?? "member") as ProjectRole;

    try {
      await apiRequest(`/projects/${projectId}/members`, {
        method: "POST",
        body: JSON.stringify({ email, role })
      });
      formEl.reset();
      await loadMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add member");
    }
  }

  async function updateRole(userId: number, role: ProjectRole) {
    try {
      await apiRequest(`/projects/${projectId}/members/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ role })
      });
      await loadMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
    }
  }

  async function removeMember(userId: number) {
    try {
      await apiRequest(`/projects/${projectId}/members/${userId}`, { method: "DELETE" }, { skipJson: true });
      await loadMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove member");
    }
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <TopNav />
      <section className="mx-auto max-w-5xl px-4 py-8">
        <h1 className="text-2xl font-semibold">Project Settings</h1>
        <p className="mt-1 text-sm text-slate-600">Admins can manage member roles here.</p>

        {isAdmin ? (
          <form onSubmit={onInvite} className="mt-6 grid gap-3 rounded border border-slate-200 bg-white p-4 md:grid-cols-4">
            <input required name="email" type="email" placeholder="Member email" className="rounded border border-slate-300 px-3 py-2 text-sm md:col-span-2" />
            <select name="role" className="rounded border border-slate-300 px-3 py-2 text-sm">
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
            <button type="submit" className="rounded bg-brand-600 px-3 py-2 text-sm font-medium text-white">Add</button>
          </form>
        ) : (
          <p className="mt-6 rounded border border-slate-200 bg-white p-4 text-sm text-slate-600">
            You can view members but only admins can change access.
          </p>
        )}

        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}

        <div className="mt-6 overflow-hidden rounded border border-slate-200 bg-white">
          <table className="w-full border-collapse text-sm">
            <thead className="bg-slate-100 text-left text-slate-600">
              <tr>
                <th className="px-3 py-2 font-medium">User ID</th>
                <th className="px-3 py-2 font-medium">Role</th>
                <th className="px-3 py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.user_id} className="border-t border-slate-200">
                  <td className="px-3 py-2">{member.user_id}</td>
                  <td className="px-3 py-2">
                    <select
                      value={member.role}
                      onChange={(event) => updateRole(member.user_id, event.target.value as ProjectRole)}
                      disabled={!isAdmin}
                      className="rounded border border-slate-300 px-2 py-1"
                    >
                      <option value="member">Member</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => removeMember(member.user_id)}
                      disabled={!isAdmin}
                      className="text-rose-600 hover:text-rose-700"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
              {!members.length ? (
                <tr>
                  <td colSpan={3} className="px-3 py-6 text-center text-slate-500">
                    No members found.
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
