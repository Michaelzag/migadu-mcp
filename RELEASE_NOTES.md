# Migadu MCP Server - Release Notes

## Version 3.2.0 - Advanced Context Protection with AI-Powered Guidance (2025-06-17)

### 🚀 Major Enhancements

#### **Intelligent Context Protection System**
- **AI-Powered Guidance Messages**: Replaced generic "context explosion" warnings with intelligent, context-aware guidance generated using FastMCP's sampling feature
- **Tool-Specific Responses**: Each tool now provides specific, actionable guidance based on the actual data returned
- **Professional Language**: Eliminated technical jargon in favor of user-friendly instructions

#### **Enhanced User Experience**
- **Smart Tooltips**: Added comprehensive usage patterns and workflow examples to tool descriptions
- **Context-Aware Logging**: Tools now provide transparent feedback about response protection decisions
- **Real Data Examples**: Guidance messages include actual addresses and specific function calls from the response

#### **FastMCP Integration Improvements**
- **Advanced Sampling**: Leverages FastMCP's `ctx.sample()` for dynamic response generation
- **Robust Error Handling**: Intelligent fallbacks when AI sampling is unavailable
- **Async Optimization**: Fully async context protection with proper error boundaries

### 🔧 Technical Improvements

#### **Context Protection Enhancements**
- `truncate_response_if_needed()` now accepts `Context` and `tool_name` parameters
- AI-generated guidance messages using Claude Haiku for speed and efficiency
- Fallback to curated messages when sampling fails
- Tool-specific response formatters for different data types

#### **Developer Experience**
- Enhanced tool documentation with workflow examples
- Professional error messaging system
- Better type safety and async handling
- Comprehensive logging for debugging

### 📝 Examples of Enhanced Guidance

**Before (v3.1.5):**
```
"Response truncated to prevent context explosion. Use specific get_ commands for details."
```

**After (v3.2.0):**
```
"Found 87 mailboxes. For complete details, use: get_my_mailbox('admin') or get_my_mailbox('michael')"
```

### 🛠️ Breaking Changes
None - fully backward compatible

### 📦 Dependencies
- Added intelligent response handling for FastMCP `Context.sample()`
- Enhanced error boundary management
- Improved async response processing

---

## Version 3.1.5 - Context Protection Implementation (2025-06-17)

### 🛡️ Context Protection
- Initial implementation of response truncation to prevent AI context explosion
- Smart summarization for large list responses
- Token estimation and intelligent thresholds

### 🚀 Release Process Fixes  
- Fixed GitHub Actions workflow exclusions that broke quality gates
- Enhanced release script for proper version management
- Implemented comprehensive CI/CD pipeline

---

## Previous Versions

See Git history for complete version details.