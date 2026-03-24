import React from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import { TopAppBar } from "./components/layout/TopAppBar";
import { SideNav } from "./components/layout/SideNav";
import { ContentShell } from "./components/layout/ContentShell";
import BatchChangesList from "./pages/BatchChangesList";
import BatchChangeCreate from "./pages/BatchChangeCreate";
import BatchSpecEditor from "./pages/BatchSpecEditor";
import ExecutionView from "./pages/ExecutionView";
import ChangesetDashboard from "./pages/ChangesetDashboard";
import CredentialSettings from "./pages/CredentialSettings";
import LoginPage from "./pages/Auth/LoginPage";
import SignUpPage from "./pages/Auth/SignUpPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
});

/** Wraps protected routes — redirects to /login if not authenticated. */
const ProtectedLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="font-mono text-xs uppercase tracking-widest text-on-surface-variant">
          Loading...
        </span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate to="/login" state={{ returnTo: location.pathname }} replace />
    );
  }

  return (
    <>
      <TopAppBar />
      <SideNav />
      <ContentShell>
        <Outlet />
      </ContentShell>
    </>
  );
};

/** Wraps public auth routes — redirects authenticated users to the app. */
const PublicLayout: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const returnTo =
    (location.state as { returnTo?: string } | null)?.returnTo ?? "/batch-changes";

  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to={returnTo} replace />;
  return <Outlet />;
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public auth routes */}
            <Route element={<PublicLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignUpPage />} />
            </Route>

            {/* Protected app routes */}
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<Navigate to="/batch-changes" replace />} />
              <Route path="/batch-changes" element={<BatchChangesList />} />
              <Route path="/batch-changes/new" element={<BatchChangeCreate />} />
              <Route
                path="/batch-changes/:id"
                element={<Navigate to="spec" replace />}
              />
              <Route
                path="/batch-changes/:id/spec"
                element={<BatchSpecEditor />}
              />
              <Route
                path="/batch-changes/:id/runs/:runId"
                element={<ExecutionView />}
              />
              <Route
                path="/batch-changes/:id/changesets"
                element={<ChangesetDashboard />}
              />
              <Route path="/credentials" element={<CredentialSettings />} />
              {/* Known-but-unimplemented nav targets */}
              <Route path="/changesets" element={<NotFound />} />
              <Route path="/templates" element={<NotFound />} />
              <Route path="/audit" element={<NotFound />} />
              {/* Wildcard */}
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
