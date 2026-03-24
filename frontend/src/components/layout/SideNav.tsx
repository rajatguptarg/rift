import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { Button } from "../ui/Button.tsx";
import { useAuth } from "../../hooks/useAuth.tsx";

const NAV_ITEMS = [
  { label: "OVERVIEW", to: "/", icon: "dashboard" },
  { label: "BATCH CHANGES", to: "/batch-changes", icon: "code_blocks" },
  { label: "CHANGESETS", to: "/changesets", icon: "merge_type" },
  { label: "CREDENTIALS", to: "/credentials", icon: "key" },
  { label: "TEMPLATES", to: "/templates", icon: "auto_fix_high" },
  { label: "AUDIT", to: "/audit", icon: "history" },
];

export const SideNav: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleSignOut = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <nav className="fixed left-0 top-16 bottom-0 z-30 flex w-64 flex-col bg-background">
      <ul className="flex-1 overflow-y-auto px-2 pt-4">
        {NAV_ITEMS.map(({ label, to, icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-4 py-3 font-mono text-xs uppercase tracking-widest transition-colors",
                  isActive
                    ? "border-l-4 border-primary-container bg-surface-container-low text-primary-container"
                    : "text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface"
                )
              }
            >
              <span className="material-symbols-outlined text-base">{icon}</span>
              {label}
            </NavLink>
          </li>
        ))}
      </ul>

      <div className="p-4 space-y-2">
        {user && (
          <div className="px-2 py-1">
            <p className="font-mono text-xs text-on-surface-variant truncate">
              {user.display_name}
            </p>
            {user.role === "SUPER_USER" && (
              <span className="inline-block mt-0.5 rounded bg-primary px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-on-primary">
                Super User
              </span>
            )}
          </div>
        )}
        <Button
          variant="primary"
          className="w-full"
          onClick={() => navigate("/batch-changes/new")}
        >
          <span className="material-symbols-outlined mr-2 text-base">add</span>
          CREATE
        </Button>
        <button
          onClick={handleSignOut}
          className="w-full px-4 py-2 font-mono text-xs uppercase tracking-widest text-on-surface-variant hover:text-on-surface transition-colors text-left"
        >
          <span className="material-symbols-outlined mr-2 text-base align-middle">logout</span>
          Sign Out
        </button>
      </div>
    </nav>
  );
};
