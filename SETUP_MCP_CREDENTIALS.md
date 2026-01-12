# MCP Setup Instructions

## 🚀 You Need to Provide These Credentials

I've configured the MCP servers, but you need to provide your credentials.

---

## 1. GitHub MCP - Personal Access Token

### Get Your Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Claude Code Memory System"
4. Select scopes:
   - `repo` (full control of private repositories)
   - `workflow` (if you want to update workflows)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Add to .env:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

---

## 2. Supabase MCP - Project Credentials

### Get Your Credentials:
1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on your project
3. Go to "Settings" → "API"
4. Copy these values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (starts with `eyJ...`)
   - **service_role key** (starts with `eyJ...`) - **KEEP THIS SECRET!**

### Add to .env:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOi...your_service_key
SUPABASE_ANON_KEY=eyJhbGciOi...your_anon_key
```

---

## 3. Update Your .env File

```bash
# Copy template if you haven't already
cp .env.template .env

# Then add your credentials to .env
nano .env
# or
code .env
```

---

## What Will Happen Next

Once you provide the credentials:

### GitHub MCP Will:
- ✅ Create a GitHub repository for this project
- ✅ Push all code to GitHub
- ✅ Enable version control and collaboration
- ✅ Track all changes with git

### Supabase MCP Will:
- ✅ Create database tables for memories
- ✅ Store all memories in the cloud
- ✅ Enable access from any machine
- ✅ Provide powerful SQL querying
- ✅ Enable real-time sync

---

## Database Schema (Supabase)

I'll create these tables:

### `memories` table:
```sql
CREATE TABLE memories (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  category TEXT NOT NULL, -- 'insights', 'learnings', 'patterns', 'context_history'
  tags TEXT[], -- Array of tags
  content JSONB NOT NULL, -- All the memory data
  transcript_length INTEGER,
  metadata JSONB
);

CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX idx_memories_created_at ON memories(created_at DESC);
```

---

## Security Notes

- **NEVER commit .env to git** (it's in .gitignore)
- **service_role key** has full database access - keep it secret!
- **anon key** is safe to expose in client apps
- GitHub token should have minimal required permissions

---

## Ready?

Once you add the credentials to `.env`, tell me and I'll:
1. Initialize the GitHub repository
2. Create the Supabase database schema
3. Migrate existing JSON memories to Supabase
4. Test the complete MCP-based system

**Sources:**
- [GitHub MCP Server | Model Context Protocol](https://glama.ai/mcp/servers/@modelcontextprotocol/github)
- [Supabase MCP | Model Context Protocol](https://supabase.com/docs/guides/getting-started/mcp)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers)
