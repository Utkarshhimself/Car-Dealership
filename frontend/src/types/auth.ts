export type User = {
  id: string;
  email: string;
  role: "customer" | "admin";
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};
