import React from "react";
import clsx from "clsx";

interface CardProps {
  children?: React.ReactNode;
  className?: string;
  accent?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  accent = false,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={clsx(
        "rounded-none bg-secondary-fixed p-6 transition-colors duration-150",
        "hover:bg-secondary-fixed-hover",
        accent && "border-l-4 border-primary-container",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </div>
  );
};
