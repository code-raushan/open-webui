# Database Migration Summary: Peewee to Alembic

## Overview
This document summarizes the migration from Peewee migrations to Alembic migrations for the Open WebUI project. The migration was necessary because the project was transitioning from Peewee ORM to SQLAlchemy, and all database tables needed to be properly represented in Alembic.

## Migration Process

### 1. Analysis of Peewee Migrations
Analyzed all 18 Peewee migration files to identify all tables that were created:
- `001_initial_schema.py` - Initial tables (auth, chat, chatidtag, document, modelfile, prompt, tag, user)
- `002_add_local_sharing.py` - Added share_id to chat table
- `003_add_auth_api_key.py` - Added api_key to user table
- `004_add_archived.py` - Added archived to chat table
- `005_add_updated_at.py` - Added created_at/updated_at to chat table
- `006_migrate_timestamps_and_charfields.py` - Updated field types
- `007_add_user_last_active_at.py` - Added timestamp fields to user table
- `008_add_memory.py` - Created memory table
- `009_add_models.py` - Created model table
- `010_migrate_modelfiles_to_models.py` - Migrated modelfile data to model table
- `011_add_user_settings.py` - Added settings to user table
- `012_add_tools.py` - Created tool table
- `013_add_user_info.py` - Added info to user table
- `014_add_files.py` - Created file table
- `015_add_functions.py` - Created function table
- `016_add_valves_and_is_active.py` - Added valves and is_active fields
- `017_add_user_oauth_sub.py` - Added oauth_sub to user table
- `018_add_function_is_global.py` - Added is_global to function table

### 2. Current Alembic State
The existing Alembic migration (`4fe53821c9e6_initial_schema.py`) already included:
- auth
- chat
- file
- group
- tag
- user

### 3. Missing Tables Identified
The following tables were missing from the Alembic schema and needed to be added:
- chatidtag
- document
- prompt
- memory
- model
- tool
- function
- channel
- message
- message_reaction
- note
- feedback
- folder
- knowledge

### 4. Migration Created
Created a new Alembic migration file: `add_missing_tables.py` that adds all the missing tables with their correct schema definitions based on the Peewee migrations and current SQLAlchemy models.

## Final Database Schema

The database now contains the following tables (all created via Alembic):

### Core Tables
1. **auth** - Authentication information
2. **user** - User accounts and profiles
3. **chat** - Chat conversations
4. **message** - Individual messages
5. **message_reaction** - Message reactions
6. **channel** - Communication channels
7. **chatidtag** - Chat tagging system
8. **tag** - Tagging system
9. **folder** - Folder organization
10. **group** - User groups

### Content Tables
11. **document** - Document storage
12. **file** - File management
13. **note** - User notes
14. **memory** - Memory/context storage
15. **knowledge** - Knowledge base entries

### AI/Model Tables
16. **model** - AI model configurations
17. **tool** - Tool definitions
18. **function** - Function definitions
19. **prompt** - Prompt templates

### System Tables
20. **feedback** - User feedback
21. **alembic_version** - Alembic migration tracking

## Migration Commands Used

```bash
# Run the migration
cd backend/open_webui
PYTHONPATH=/path/to/backend python -m alembic upgrade head

# Check current migration status
PYTHONPATH=/path/to/backend python -m alembic current

# Verify tables in database
sqlite3 data/webui.db ".schema" | grep -E "CREATE TABLE"
```

## Benefits of This Migration

1. **Complete Schema Coverage**: All tables from Peewee migrations are now properly represented in Alembic
2. **Consistent Migration System**: No more mixing of Peewee and Alembic migrations
3. **Future-Proof**: All future database changes will use Alembic
4. **Data Integrity**: The migration preserves all existing data while ensuring schema consistency
5. **Development Clarity**: Clear separation between old Peewee-based code and new SQLAlchemy-based code

## Next Steps

1. **Remove Peewee Dependencies**: Once all code has been migrated to SQLAlchemy, Peewee dependencies can be removed
2. **Update Documentation**: Update any documentation that references Peewee migrations
3. **Test Thoroughly**: Ensure all functionality works correctly with the new schema
4. **Monitor Performance**: Watch for any performance impacts from the migration

## Notes

- The `modelfile` table was intentionally excluded as it was migrated to the `model` table in Peewee migration 010
- All field types and constraints were preserved from the original Peewee schema
- The migration is reversible and includes proper downgrade functions
- All tables now use consistent naming and field types across the application 