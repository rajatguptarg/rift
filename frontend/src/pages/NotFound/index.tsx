import React from "react";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <span className="material-symbols-outlined mb-4 text-5xl text-on-surface-variant">
        search_off
      </span>
      <h2 className="mb-2 font-mono text-lg font-semibold uppercase tracking-widest text-on-surface">
        Page Not Found
      </h2>
      <p className="mb-6 font-mono text-xs text-on-surface-variant">
        This route is not yet available or does not exist.
      </p>
      <Link
        to="/batch-changes"
        className="font-mono text-xs uppercase tracking-wider text-primary underline-offset-2 hover:underline"
      >
        Go to Batch Changes
      </Link>
    </div>
  );
};

export default NotFound;
