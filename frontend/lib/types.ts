export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high";
export type ProjectRole = "admin" | "member";

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
}

export interface ProjectMember {
  project_id: number;
  user_id: number;
  role: ProjectRole;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  project_id: number;
  assignee_id: number | null;
  created_by: number;
  created_at: string;
}

export interface DashboardStats {
  total_tasks: number;
  overdue_tasks: number;
  by_status: Record<TaskStatus, number>;
}
