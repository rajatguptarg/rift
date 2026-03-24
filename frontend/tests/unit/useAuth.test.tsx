import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import React from "react";
import { AuthProvider, useAuth } from "../../src/hooks/useAuth";

// Mock the api module
vi.mock("../../src/services/api", () => ({
  api: {
    get: vi.fn(),
  },
}));

const wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe("useAuth", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("starts unauthenticated when no token is stored", async () => {
    const { api } = await import("../../src/services/api");
    (api.get as ReturnType<typeof vi.fn>).mockRejectedValue(new Error("no token"));

    const { result, unmount } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    unmount();
  });

  it("login stores token and sets user", async () => {
    const { api } = await import("../../src/services/api");
    (api.get as ReturnType<typeof vi.fn>).mockRejectedValue(new Error("no token"));

    const { result, unmount } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.login({
        access_token: "test-token",
        token_type: "Bearer",
        expires_at: new Date().toISOString(),
        user: {
          id: "usr_001",
          username: "alice",
          display_name: "Alice",
          email: null,
          role: "STANDARD",
          bootstrap_managed: false,
          created_at: new Date().toISOString(),
        },
      });
    });

    expect(result.current.token).toBe("test-token");
    expect(result.current.user?.username).toBe("alice");
    expect(localStorage.getItem("rift_token")).toBe("test-token");
    unmount();
  });

  it("logout clears token and user", async () => {
    const { api } = await import("../../src/services/api");
    (api.get as ReturnType<typeof vi.fn>).mockRejectedValue(new Error());

    const { result, unmount } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.login({
        access_token: "tok",
        token_type: "Bearer",
        expires_at: new Date().toISOString(),
        user: {
          id: "usr_001",
          username: "alice",
          display_name: "Alice",
          email: null,
          role: "STANDARD",
          bootstrap_managed: false,
          created_at: new Date().toISOString(),
        },
      });
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();
    expect(localStorage.getItem("rift_token")).toBeNull();
    unmount();
  });
});
