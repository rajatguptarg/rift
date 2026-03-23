import React from "react";
import clsx from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}) => {
  const base =
    "inline-flex items-center justify-center font-body font-semibold rounded-full transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-fixed disabled:opacity-50 disabled:cursor-not-allowed";

  const sizes = {
    sm: "px-4 py-1.5 text-sm",
    md: "px-8 py-3 text-base",
    lg: "px-10 py-4 text-lg",
  };

  const variants = {
    primary:
      "kinetic-gradient text-on-primary-container hover:scale-105 active:scale-95 hover:ring-4 hover:ring-primary-fixed",
    ghost:
      "bg-transparent text-primary border border-outline-variant/20 hover:scale-105 active:scale-95 hover:ring-2 hover:ring-primary/30",
  };

  return (
    <button className={clsx(base, sizes[size], variants[variant], className)} {...props}>
      {children}
    </button>
  );
};
