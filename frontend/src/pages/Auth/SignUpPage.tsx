import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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
    minLength: 3,
    maxLength: 32,
  },
  {
    name: "display_name",
    label: "Display Name",
    type: "text",
    autoComplete: "name",
    required: true,
    maxLength: 64,
  },
  {
    name: "email",
    label: "Email (optional)",
    type: "email",
    autoComplete: "email",
    required: false,
  },
  {
    name: "password",
    label: "Password",
    type: "password",
    autoComplete: "new-password",
    required: true,
    minLength: 8,
  },
];

const SignUpPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (values: Record<string, string>) => {
    setError(null);
    try {
      const res = await api.post<AuthSessionResponse>("/api/v1/auth/sign-up", {
        username: values.username,
        display_name: values.display_name,
        email: values.email || undefined,
        password: values.password,
      });
      login(res.data);
      navigate("/batch-changes", { replace: true });
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Registration failed. Please try again.");
    }
  };

  return (
    <AuthLayout title="Create Account" subtitle="Create a new Rift account.">
      <AuthForm
        fields={FIELDS}
        submitLabel="Create Account"
        onSubmit={handleSubmit}
        error={error}
        footer={
          <span className="font-mono text-xs text-on-surface-variant">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-primary underline-offset-2 hover:underline"
            >
              Sign in
            </Link>
          </span>
        }
      />
    </AuthLayout>
  );
};

export default SignUpPage;
