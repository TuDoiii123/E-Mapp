-- Create users table compatible with Backend/models/user.py
DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users (
  id VARCHAR(80) PRIMARY KEY,
  cccd_number VARCHAR(50) UNIQUE,
  full_name VARCHAR(255),
  date_of_birth VARCHAR(50),
  phone VARCHAR(50),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  role VARCHAR(50) NOT NULL DEFAULT 'citizen',
  is_vneid_verified BOOLEAN NOT NULL DEFAULT FALSE,
  vneid_id VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_cccd ON public.users(cccd_number);
