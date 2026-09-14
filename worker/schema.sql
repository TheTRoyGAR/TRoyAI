-- TRoyAI E-Automation Agency — D1 Database Schema

CREATE TABLE IF NOT EXISTS departments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  agent_count INTEGER DEFAULT 5,
  status TEXT DEFAULT 'active',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  department TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  goal TEXT,
  status TEXT DEFAULT 'active',
  tasks_completed INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  department TEXT NOT NULL,
  agent TEXT,
  task TEXT NOT NULL,
  input TEXT,
  output TEXT,
  status TEXT DEFAULT 'queued',
  created_at TEXT,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  department TEXT,
  content TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Seed departments
INSERT OR IGNORE INTO departments (id, name, description) VALUES
  ('ops', 'Operations', 'CEO Command Centre — 5 agents'),
  ('sales', 'Sales', 'Revenue generation — 5 agents'),
  ('marketing', 'Marketing', 'Brand and growth — 5 agents'),
  ('finance', 'Finance', 'Financial health — 5 agents'),
  ('cto', 'CTO', 'Technology and infrastructure — 5 agents');

-- Seed agents
INSERT OR IGNORE INTO agents (id, department, name, role) VALUES
  ('ops-1', 'ops', 'executive_assistant', 'Executive Assistant'),
  ('ops-2', 'ops', 'project_manager', 'Project Manager'),
  ('ops-3', 'ops', 'resource_manager', 'Resource Manager'),
  ('ops-4', 'ops', 'report_generator', 'Report Generator'),
  ('ops-5', 'ops', 'process_optimizer', 'Process Optimizer'),
  ('sales-1', 'sales', 'lead_generator', 'Lead Generator'),
  ('sales-2', 'sales', 'lead_qualifier', 'Lead Qualifier'),
  ('sales-3', 'sales', 'proposal_writer', 'Proposal Writer'),
  ('sales-4', 'sales', 'deal_closer', 'Deal Closer'),
  ('sales-5', 'sales', 'crm_manager', 'CRM Manager'),
  ('mkt-1', 'marketing', 'content_creator', 'Content Creator'),
  ('mkt-2', 'marketing', 'seo_optimizer', 'SEO Optimizer'),
  ('mkt-3', 'marketing', 'social_manager', 'Social Media Manager'),
  ('mkt-4', 'marketing', 'campaign_manager', 'Campaign Manager'),
  ('mkt-5', 'marketing', 'analytics_reporter', 'Analytics Reporter'),
  ('fin-1', 'finance', 'bookkeeper', 'Bookkeeper'),
  ('fin-2', 'finance', 'budget_planner', 'Budget Planner'),
  ('fin-3', 'finance', 'invoice_manager', 'Invoice Manager'),
  ('fin-4', 'finance', 'financial_reporter', 'Financial Reporter'),
  ('fin-5', 'finance', 'cost_optimizer', 'Cost Optimizer'),
  ('cto-1', 'cto', 'developer', 'Software Developer'),
  ('cto-2', 'cto', 'code_reviewer', 'Code Reviewer'),
  ('cto-3', 'cto', 'architect', 'System Architect'),
  ('cto-4', 'cto', 'security_auditor', 'Security Auditor'),
  ('cto-5', 'cto', 'devops', 'DevOps Engineer');
