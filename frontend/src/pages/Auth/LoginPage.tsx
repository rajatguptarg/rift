import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AuthLayout } from "../../components/auth/AuthLayout";
import { AuthForm, AuthField } from "../../components/auth/AuthForm";
import { useAuth } from "../../hooks/useAuth";
import { api } from "../../services/api";
import type { AuthSessionResponse } from "../../types/api";

const FIELDS: AuthField[] = [
  {
    name: "username",
    label: "Username",
    type: "text",
    autoComplete: "username",
    required: true,
  },
  {
    name: "password",
    label: "Password",
    type: "password",
    autoComplete: "current-password",
    required: true,
  },
];

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);

  const returnTo =
    (location.state as { returnTo?: string } | null)?.returnTo ?? "/batch-changes";

  const handleSubmit = async (values: Record<string, string>) => {
    setError(null);
    try {
      const res = await api.post<AuthSessionResponse>("/api/v1/auth/sign-in", {
        username: values.username,
        password: values.password,
      });
      login(res.data);
      navigate(returnTo, { replace: true });
    } catch {
      setError("Invalid username or password.");
    }
  };

  return (
    <AuthLayout title="Sign In" subtitle="Sign in to your Rift account.">
      <AuthForm
        fields={FIELDS}
        submitLabel="Sign In"
        onSubmit={handleSubmit}
        error={error}
        footer={
          <span className="font-mono text-xs text-on-surface-variant">
            No account?{" "}
            <Link
              to="/signup"
              className="text-primary underline-offset-2 hover:underline"
            >
              Sign up
            </Link>
          </span>
        }
      />
    </AuthLayout>
  );
};

export default LoginPage;
