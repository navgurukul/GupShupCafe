# PlantUML Diagram Migration Guide

## Overview

This document describes the migration of PlantUML diagrams from `.puml` to `.wsd` format and upgrading to PlantUML version 1.2024.8.

## Migration Summary

**Date:** October 15, 2025
**PlantUML Version:** Upgraded from 1.2020.02 to 1.2024.8
**File Format:** Migrated from `.puml` to `.wsd` (WebSequence Diagrams)
**Total Diagrams:** 13 diagrams successfully migrated

## Why Migrate?

### 1. Latest PlantUML Version
- **Old Version:** 1.2020.02 (released March 2020)
- **New Version:** 1.2024.8 (released November 2024)
- **Benefits:**
  - Latest features and syntax improvements
  - Better rendering quality
  - Enhanced diagram types support
  - Bug fixes and performance improvements

### 2. File Format Standardization
- `.wsd` (WebSequence Diagrams) is the standard format
- Better compatibility across tools and platforms
- More explicit about diagram format

## Changes Made

### Syntax Updates

#### 1. Component Diagram (01-component-diagram.wsd)
**Issue:** Nested components within components are no longer supported.

**Before:**
```plantuml
component [React Application] as ReactApp {
    component [Login Page] as LoginPage
    component [Lobby Page] as LobbyPage
}
```

**After:**
```plantuml
component [React Application] as ReactApp
component [Login Page] as LoginPage
component [Lobby Page] as LobbyPage

ReactApp ..> LoginPage
ReactApp ..> LobbyPage
```

**Reason:** PlantUML 1.2024.8 enforces stricter component diagram syntax.

#### 2. Sequence Diagram Notes (06-sequence-llm-agent-interaction.wsd)
**Issue:** `note bottom of` syntax deprecated for some elements.

**Before:**
```plantuml
note bottom of MCPServer
    MCP Server provides tools
end note
```

**After:**
```plantuml
note over MCPServer
    MCP Server provides tools
end note
```

**Reason:** Better positioning and compatibility with latest version.

#### 3. Activity Diagram Notes (07-activity-discussion-lifecycle.wsd)
**Issue:** Notes referencing swimlane names in quotes not supported.

**Before:**
```plantuml
note right of "LLM Agent"
    CEFR Feedback includes
end note
```

**After:**
```plantuml
floating note right
    CEFR Feedback includes
end note
```

**Reason:** Activity diagrams use swimlanes, and direct note references aren't supported.

#### 4. Package Diagram Artifacts (11-package-diagram-frontend.wsd)
**Issue:** Artifacts with content blocks inside packages cause errors.

**Before:**
```plantuml
package "public/" {
    artifact index.html
    artifact assets/
}

artifact package.json {
    dependencies
    devDependencies
}
```

**After:**
```plantuml
note "Configuration Files:\n- package.json\n- vite.config.js" as ConfigFiles
note "Public Assets:\n- index.html\n- assets/" as PublicAssets
```

**Reason:** Simplified representation using notes for configuration files.

## Diagrams Migrated

1. ✅ 01-component-diagram.wsd - Component relationships flattened
2. ✅ 02-deployment-diagram.wsd - No changes needed
3. ✅ 03-class-diagram-backend.wsd - No changes needed
4. ✅ 04-sequence-user-join-discussion.wsd - No changes needed
5. ✅ 05-sequence-webrtc-audio.wsd - No changes needed
6. ✅ 06-sequence-llm-agent-interaction.wsd - Note positioning updated
7. ✅ 07-activity-discussion-lifecycle.wsd - Floating notes used
8. ✅ 08-state-room-management.wsd - No changes needed
9. ✅ 09-usecase-diagram.wsd - No changes needed
10. ✅ 10-er-diagram-database.wsd - No changes needed
11. ✅ 11-package-diagram-frontend.wsd - Artifacts replaced with notes
12. ✅ 12-class-diagram-frontend.wsd - No changes needed
13. ✅ 13-sequence-speaker-turn-management.wsd - No changes needed

## Verification Process

All diagrams were tested and successfully rendered:

```bash
cd docs/diagrams/uml
for wsd in *.wsd; do
    java -jar plantuml-1.2024.8.jar "$wsd" -o /tmp/test_output
done
```

**Results:** All 13 diagrams generated without errors.

## Usage Instructions

### Generate Individual Diagram
```bash
java -jar plantuml-1.2024.8.jar 01-component-diagram.wsd
```

### Generate All Diagrams
```bash
cd docs/diagrams/uml
java -jar plantuml-1.2024.8.jar *.wsd
```

### Generate SVG Instead of PNG
```bash
java -jar plantuml-1.2024.8.jar -tsvg 01-component-diagram.wsd
```

## Installation

### Download Latest PlantUML
```bash
wget https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar
```

### Create Alias (Optional)
```bash
# Add to ~/.bashrc or ~/.zshrc
alias plantuml='java -jar /path/to/plantuml-1.2024.8.jar'
```

## Best Practices

1. **Always use latest PlantUML version** - Ensures compatibility and latest features
2. **Test diagrams after changes** - Verify rendering before committing
3. **Use .wsd extension** - Standard format for PlantUML diagrams
4. **Avoid deep nesting** - Keep component hierarchies flat
5. **Use floating notes** - More flexible positioning in complex diagrams
6. **Document complex diagrams** - Add comprehensive notes and comments

## Troubleshooting

### Issue: Diagram fails to render
**Solution:** Check PlantUML version. Must be 1.2024.8 or later.

### Issue: Nested components cause errors
**Solution:** Flatten the hierarchy and use relationships instead.

### Issue: Notes not positioning correctly
**Solution:** Use `note over`, `floating note`, or simple notes without specific positioning.

### Issue: Artifacts in packages cause errors
**Solution:** Replace with components or use notes for configuration files.

## References

- [PlantUML Official Documentation](https://plantuml.com/)
- [PlantUML Latest Release](https://github.com/plantuml/plantuml/releases)
- [Component Diagram Syntax](https://plantuml.com/component-diagram)
- [Sequence Diagram Syntax](https://plantuml.com/sequence-diagram)
- [Activity Diagram Syntax](https://plantuml.com/activity-diagram-beta)

## Future Maintenance

- **Version Updates:** Check for new PlantUML releases quarterly
- **Syntax Changes:** Review release notes for breaking changes
- **Diagram Reviews:** Validate all diagrams after PlantUML updates
- **Documentation:** Keep this migration guide updated with any new issues

## Support

For questions or issues with PlantUML diagrams:
1. Check this migration guide
2. Review PlantUML official documentation
3. Test with latest PlantUML version
4. Open an issue on GitHub with diagram snippet and error message

---

**Migration Status:** ✅ Complete
**Last Updated:** October 15, 2025
**PlantUML Version:** 1.2024.8
**Migrated Diagrams:** 13/13
