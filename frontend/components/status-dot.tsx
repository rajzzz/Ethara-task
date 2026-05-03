import { TaskStatus } from "@/lib/types";

const colorMap: Record<TaskStatus, string> = {
  todo: "bg-slate-400",
  in_progress: "bg-amber-500",
  done: "bg-emerald-500"
};

export function StatusDot({ status }: { status: TaskStatus }) {
  return <span className={`inline-block h-2.5 w-2.5 rounded-full ${colorMap[status]}`} aria-hidden />;
}
