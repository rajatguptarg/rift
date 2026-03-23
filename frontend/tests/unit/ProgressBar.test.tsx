import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ProgressBar } from "../../src/components/ui/ProgressBar";

describe("ProgressBar", () => {
  it("renders a progressbar role element", () => {
    render(<ProgressBar value={50} />);
    expect(screen.getByRole("progressbar")).toBeDefined();
  });

  it("sets aria-valuenow to the clamped value", () => {
    render(<ProgressBar value={42} />);
    const bar = screen.getByRole("progressbar");
    expect(bar.getAttribute("aria-valuenow")).toBe("42");
  });

  it("sets aria-valuemin to 0", () => {
    render(<ProgressBar value={50} />);
    expect(screen.getByRole("progressbar").getAttribute("aria-valuemin")).toBe("0");
  });

  it("sets aria-valuemax to 100", () => {
    render(<ProgressBar value={50} />);
    expect(screen.getByRole("progressbar").getAttribute("aria-valuemax")).toBe("100");
  });

  it("clamps value below 0 to 0", () => {
    render(<ProgressBar value={-10} />);
    expect(screen.getByRole("progressbar").getAttribute("aria-valuenow")).toBe("0");
  });

  it("clamps value above 100 to 100", () => {
    render(<ProgressBar value={150} />);
    expect(screen.getByRole("progressbar").getAttribute("aria-valuenow")).toBe("100");
  });

  it("applies custom className", () => {
    render(<ProgressBar value={50} className="my-bar" />);
    expect(screen.getByRole("progressbar").className).toContain("my-bar");
  });

  it("inner fill has correct width style", () => {
    render(<ProgressBar value={75} />);
    const bar = screen.getByRole("progressbar");
    const fill = bar.firstElementChild as HTMLElement;
    expect(fill.style.width).toBe("75%");
  });
});
