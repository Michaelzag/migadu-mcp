# Pydantic 2.0+ Integration Refactor Plan

## What We Need To Do
Complete Pydantic validation integration across all MCP tools to eliminate hybrid implementation patterns and finish the architectural refactor we started.

## The Problem We're Solving

### Original Goal
We set out to eliminate complex `Union[str, List[str]]` type handling across ~32 MCP tools that was causing validation nightmares. The goal was to "rip it apart and fully integrate pydantic 2.0+" to get compile-time type safety instead of runtime Union validation hell.

### What We Actually Built
We successfully created:
- **Comprehensive infrastructure:** `migadu_mcp/utils/bulk_processing.py` with iterator patterns and `@bulk_processor_with_schema()` decorator
- **Complete schema foundation:** `migadu_mcp/utils/schemas.py` with proper Pydantic 2.0+ models including all the missing API fields from official Migadu documentation
- **Working pattern:** `create_mailbox` tool demonstrates the full integration working perfectly

### The Hybrid Mess We're Stuck With
**Only 1 of 14+ tools actually uses the Pydantic integration.** The rest still use the old manual validation:

```python
# What we have everywhere (BAD):
@bulk_processor
async def process_update_mailbox(item: Dict[str, Any], ctx: Context):
    validate_required_fields(item, ["target"], "update_mailbox")  # Manual validation
    target = item["target"]  # Manual extraction
    name = get_field_with_default(item, "name")  # Manual defaults

# What we have in 1 tool (GOOD):
@bulk_processor_with_schema(MailboxCreateRequest)  
async def process_create_mailbox(validated_item: MailboxCreateRequest, ctx: Context):
    target = validated_item.target  # Type-safe access
    name = validated_item.name  # Pydantic validation already done
```

### Why This Is a Critical Problem

1. **Architecture Violation:** We have two completely different validation systems running side-by-side, violating .roorules "Half-measure integrations that maintain conflicting systems"

2. **Union Type Hell Still Exists:** 13+ tools still do manual `Union[str, List[str]]` handling instead of using our Pydantic schemas that solve this

3. **Type Safety Inconsistency:** MyPy can't properly validate the manual `Dict[str, Any]` patterns, leaving 90% of our tools without compile-time type safety

4. **Developer Confusion:** New developers see two different patterns and don't know which one to follow

5. **Dead Code Waste:** `migadu_mcp/utils/specs.py` (229 lines) was created for an alternative approach but is completely unused

6. **Incomplete Value Delivery:** We built all this sophisticated Pydantic infrastructure but only get the benefits in 1 tool

## Why We're Doing This Refactor

### Immediate Benefits
- **Eliminate Union Type Complexity:** All 14+ tools will use type-safe Pydantic validation instead of manual `Union[str, List[str]]` handling
- **Consistent Architecture:** Single validation pattern across entire codebase
- **Type Safety:** 100% MyPy coverage with compile-time validation
- **Code Cleanup:** Remove 229 lines of dead code and manual validation utilities

### Long-term Benefits  
- **Maintainability:** New tools follow established Pydantic pattern
- **Error Prevention:** Pydantic validation catches invalid inputs before they reach business logic
- **Developer Experience:** Clear, documented schemas instead of undocumented Dict structures
- **Future-proofing:** Established foundation for additional email management features

### Business Impact
- **Reliability:** Type-safe validation prevents runtime errors from malformed inputs
- **Performance:** Faster development of new features using established patterns
- **Quality:** Consistent error handling and validation messages across all tools
- **Compliance:** Aligns with .roorules architectural standards for production software

## Implementation Steps

### Schema Creation
- [ ] Add `MailboxDeleteRequest` schema to `migadu_mcp/utils/schemas.py`
- [ ] Add `MailboxPasswordResetRequest` schema 
- [ ] Add `AliasCreateRequest` schema with destinations validation
- [ ] Add `AliasUpdateRequest` schema
- [ ] Add `AliasDeleteRequest` schema  
- [ ] Add `IdentityCreateRequest` schema with password validation
- [ ] Add `IdentityUpdateRequest` schema
- [ ] Add `IdentityDeleteRequest` schema
- [ ] Add `RewriteCreateRequest` schema with pattern validation
- [ ] Add `RewriteUpdateRequest` schema
- [ ] Add `RewriteDeleteRequest` schema

### Tool Conversion - Mailbox Tools
- [ ] Convert `process_update_mailbox` to use `@bulk_processor_with_schema(MailboxUpdateRequest)`
- [ ] Convert `process_delete_mailbox` to use `@bulk_processor_with_schema(MailboxDeleteRequest)`  
- [ ] Convert `process_reset_password` to use `@bulk_processor_with_schema(MailboxPasswordResetRequest)`
- [ ] Convert `process_set_autoresponder` to use `@bulk_processor_with_schema(AutoresponderRequest)`

### Tool Conversion - Alias Tools
- [ ] Convert `process_create_alias` to use `@bulk_processor_with_schema(AliasCreateRequest)`
- [ ] Convert `process_update_alias` to use `@bulk_processor_with_schema(AliasUpdateRequest)`
- [ ] Convert `process_delete_alias` to use `@bulk_processor_with_schema(AliasDeleteRequest)`

### Tool Conversion - Identity Tools  
- [ ] Convert `process_create_identity` to use `@bulk_processor_with_schema(IdentityCreateRequest)`
- [ ] Convert `process_update_identity` to use `@bulk_processor_with_schema(IdentityUpdateRequest)`
- [ ] Convert `process_delete_identity` to use `@bulk_processor_with_schema(IdentityDeleteRequest)`

### Tool Conversion - Rewrite Tools
- [ ] Convert `process_create_rewrite` to use `@bulk_processor_with_schema(RewriteCreateRequest)`
- [ ] Convert `process_update_rewrite` to use `@bulk_processor_with_schema(RewriteUpdateRequest)`
- [ ] Convert `process_delete_rewrite` to use `@bulk_processor_with_schema(RewriteDeleteRequest)`

### Import Cleanup
- [ ] Add schema imports to `migadu_mcp/tools/mailbox_tools.py`
- [ ] Add schema imports to `migadu_mcp/tools/alias_tools.py`  
- [ ] Add schema imports to `migadu_mcp/tools/identity_tools.py`
- [ ] Add schema imports to `migadu_mcp/tools/rewrite_tools.py`
- [ ] Remove `validate_required_fields` and `get_field_with_default` imports from all tool files

### Code Cleanup
- [ ] Delete `migadu_mcp/utils/specs.py` file completely (unused 229 lines)
- [ ] Remove any remaining imports of specs.py from other files

## Success Criteria
- All 14+ tools use `@bulk_processor_with_schema()` decorator pattern
- Zero manual `validate_required_fields()` calls remaining in codebase
- Zero `get_field_with_default()` calls remaining in codebase  
- MyPy reports no type errors across entire codebase
- All tools maintain same JSON API structure for LLM compatibility
- Pydantic validation prevents invalid inputs with clear error messages
- No unused code files remain (specs.py deleted)