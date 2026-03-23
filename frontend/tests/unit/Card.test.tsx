import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Card } from "../../src/components/ui/Card";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeDefined();
  });

  it("applies default classes", () => {
    render(<Card>Content</Card>);
    const card = screen.getByText("Content");
    expect(card.className).toContain("rounded-none");
  });

  it("applies accent border when accent=true", () => {
    render(<Card accent>Accented</Card>);
    const card = screen.getByText("Accented");
    expect(card.className).toContain("border-l-4");
  });

  it("does not apply accent border by default", () => {
    render(<Card>No accent</Card>);
    const card = screen.getByText("No accent");
    expect(card.className).not.toContain("border-l-4");
  });

  it("applies cursor-pointer when onClick is provided", () => {
    render(<Card onClick={() => {}}>Clickable</Card>);
    const card = screen.getByText("Clickable");
    expect(card.className).toContain("cursor-pointer");
  });

  it("calls onClick when clicked", () => {
    const onClick = vi.fn();
    render(<Card onClick={onClick}>Click me</Card>);
    fireEvent.click(screen.getByText("Click me"));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("applies custom className", () => {
    render(<Card className="extra-class">Styled</Card>);
    expect(screen.getByText("Styled").className).toContain("extra-class");
  });
});
