-- ThreatGuard schema. Run in Supabase SQL Editor.

create extension if not exists "pgcrypto";

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.scans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  subject text not null default '',
  sender text not null,
  body text not null,
  prediction text not null check (prediction in ('phishing', 'safe')),
  probability double precision not null check (probability between 0 and 1),
  risk_score double precision not null check (risk_score between 0 and 100),
  confidence_score double precision not null check (confidence_score between 0 and 100),
  explanation jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists scans_user_created_idx on public.scans (user_id, created_at desc);
create index if not exists scans_user_prediction_idx on public.scans (user_id, prediction);

-- Create a profile automatically when a user registers.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, coalesce(new.email, ''))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Row level security
alter table public.profiles enable row level security;
alter table public.scans enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles for select using (auth.uid() = id);

drop policy if exists "scans_select_own" on public.scans;
create policy "scans_select_own" on public.scans for select using (auth.uid() = user_id);

drop policy if exists "scans_insert_own" on public.scans;
create policy "scans_insert_own" on public.scans for insert with check (auth.uid() = user_id);

drop policy if exists "scans_delete_own" on public.scans;
create policy "scans_delete_own" on public.scans for delete using (auth.uid() = user_id);
