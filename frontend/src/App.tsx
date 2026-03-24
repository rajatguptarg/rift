import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./hooks/useAuth";
import { TopAppBar } from "./components/layout/TopAppBar";
import { SideNav } from "./components/layout/SideNav";
import { ContentShell } from "./components/layout/ContentShell";
import BatchChangesList from "./pages/BatchChangesList";
import BatchChangeCreate from "./pages/BatchChangeCreate";
import BatchSpecEditor from "./pages/BatchSpecEditor";
import ExecutionView from "./pages/ExecutionView";
import ChangesetDashboard from "./pages/ChangesetDashboard";
import CredentialSettings from "./pages/CredentialSettings";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <TopAppBar />
          <SideNav />
          <ContentShell>
            <Routes>
              <Route path="/" element={<Navigate to="/batch-changes" replace />} />
              <Route path="/batch-changes" element={<BatchChangesList />} />
              <Route path="/batch-changes/new" element={<BatchChangeCreate />} />
              <Route path="/batch-changes/:id/spec" element={<BatchSpecEditor />} />
              <Route path="/batch-changes/:id/runs/:runId" element={<ExecutionView />} />
              <Route path="/batch-changes/:id/changesets" element={<ChangesetDashboard />} />
              <Route path="/credentials" element={<CredentialSettings />} />
            </Routes>
          </ContentShell>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
