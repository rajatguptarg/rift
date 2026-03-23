import React from "react";
import { Link } from "react-router-dom";

export const TopAppBar: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 flex h-16 items-center justify-between bg-background px-6">
      {/* Left: wordmark + search */}
      <div className="flex items-center gap-6">
        <Link
          to="/"
          className="font-headline text-xl font-extrabold uppercase tracking-widest text-primary-container"
        >
          RIFT
        </Link>
        <div className="flex items-center gap-2 rounded-full bg-surface-container-highest px-4 py-2 text-sm text-on-surface-variant">
          <span className="material-symbols-outlined text-base">search</span>
          <input
            type="text"
            placeholder="Search batch changes..."
            className="bg-transparent outline-none placeholder:text-on-surface-variant/60 text-on-surface"
            aria-label="Search"
          />
        </div>
      </div>

      {/* Right: icon buttons */}
      <div className="flex items-center gap-1">
        {["notifications", "help_outline", "account_circle"].map((icon) => (
          <button
            key={icon}
            className="flex h-10 w-10 items-center justify-center rounded-full text-on-surface-variant transition-colors hover:text-primary active:scale-90"
            aria-label={icon}
          >
            <span className="material-symbols-outlined">{icon}</span>
          </button>
        ))}
      </div>
    </header>
  );
};
