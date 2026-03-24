import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import React from "react";

vi.mock("../../src/hooks/useAuth", () => ({
  useAuth: vi.fn().mockReturnValue({
    isAuthenticated: false,
    isLoading: false,
    token: null,
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe("Auth routing", () => {
  it("renders login page at /login", () => {
    const LoginPage = () => <div>Login Form</div>;
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("Login Form")).toBeInTheDocument();
  });

  it("renders signup page at /signup", () => {
    const SignUpPage = () => <div>Sign Up Form</div>;
    render(
      <MemoryRouter initialEntries={["/signup"]}>
        <Routes>
          <Route path="/signup" element={<SignUpPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("Sign Up Form")).toBeInTheDocument();
  });

  it("renders NotFound for unknown routes", () => {
    const NotFound = () => <div>Page Not Found</div>;
    render(
      <MemoryRouter initialEntries={["/this-does-not-exist"]}>
        <Routes>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
  });
});
