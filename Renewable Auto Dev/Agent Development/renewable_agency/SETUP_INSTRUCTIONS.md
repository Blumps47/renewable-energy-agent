# 🚀 Renewable Energy RAG System Setup Instructions

## ✅ Current Status
Your API keys are configured! Now we need to complete the database setup.

## 📋 Required Steps

### 1. Set Up Supabase Database Schema

Since automatic schema creation failed, you need to set it up manually:

**Step-by-step:**

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Sign in to your account
   - Select your project: `oamlbjblbyxnyzjxxhjl`

2. **Navigate to SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Enable Required Extensions**
   - Copy and paste this first:
   ```sql
   -- Enable required extensions
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
   - Click "Run" or press Ctrl+Enter

4. **Create Database Schema**
   - Copy the entire contents of `backend/database_schema.sql`
   - Paste it into a new SQL query
   - Click "Run" or press Ctrl+Enter

5. **Verify Setup**
   - Go to "Table Editor" in the left sidebar
   - You should see these tables:
     - `users`
     - `projects` 
     - `documents`
     - `document_chunks`
     - `conversation_contexts`

### 2. Test the System

After setting up the database, run:

```bash
python test_api_keys.py
```

### 3. Start the Server

Once everything is working:

```bash
python backend/main.py
```

The server will start at: http://localhost:8000

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Troubleshooting

### If database setup fails:
1. Make sure the `vector` extension is enabled
2. Check that your Supabase service key has admin permissions
3. Try running the schema in smaller chunks

### If API keys don't work:
1. Double-check the `.env` file format
2. Ensure no extra spaces or quotes around keys
3. Restart any running processes

### If imports fail:
```bash
pip install -r requirements.txt
```

## 🎯 Next Steps After Setup

1. **Test the RAG System**: Upload documents and test queries
2. **Frontend Setup**: Configure the React frontend
3. **Production Deployment**: Set up production environment

## 📞 Need Help?

If you encounter issues:
1. Check the error messages carefully
2. Verify all API keys are correct
3. Ensure Supabase project is active
4. Make sure all dependencies are installed

---

**Current Project URL**: https://oamlbjblbyxnyzjxxhjl.supabase.co 