// Display metadata for the swing phases returned by the API.
export const PHASES = {
  setup: { label: "Setup", classes: "bg-sky-500/15 text-sky-300 border-sky-500/30" },
  takeaway: { label: "Takeaway", classes: "bg-teal-500/15 text-teal-300 border-teal-500/30" },
  backswing: { label: "Backswing", classes: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30" },
  top_of_swing: { label: "Top of Swing", classes: "bg-lime-500/15 text-lime-300 border-lime-500/30" },
  downswing: { label: "Downswing", classes: "bg-amber-500/15 text-amber-300 border-amber-500/30" },
  impact: { label: "Impact", classes: "bg-orange-500/15 text-orange-300 border-orange-500/30" },
  follow_through: { label: "Follow-Through", classes: "bg-violet-500/15 text-violet-300 border-violet-500/30" },
};

export function phaseInfo(phase) {
  return PHASES[phase] ?? { label: phase, classes: "bg-zinc-500/15 text-zinc-300 border-zinc-500/30" };
}
