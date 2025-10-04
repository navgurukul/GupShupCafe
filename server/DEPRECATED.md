# ⚠️ DEPRECATED: Node.js Backend

## Status: DEPRECATED - Use Python Backend Instead

**Date:** October 2024

This Node.js/Express backend has been replaced by a Python/FastAPI backend located in `/server_py`.

## Why Deprecated?

The Python FastAPI backend provides:
- ✅ Better AWS EC2 deployment support
- ✅ Comprehensive test suite (36 tests)
- ✅ Better type safety with Python type hints
- ✅ Native async/await support
- ✅ Same API contract (no frontend changes needed)
- ✅ Complete deployment documentation

## Migration Path

If you're currently using this Node.js backend:

1. **Read Migration Guide**: See [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
2. **Install Python Backend**: Follow [server_py/README.md](../server_py/README.md)
3. **Test**: Run the test suite in `/server_py`
4. **Deploy**: Follow [server_py/DEPLOYMENT.md](../server_py/DEPLOYMENT.md)

## For Reference Only

This code is kept for reference purposes. It should NOT be used for new deployments.

**Use `/server_py` instead.**

## Key Differences

| Feature | Node.js (Deprecated) | Python (Current) |
|---------|---------------------|------------------|
| Framework | Express.js | FastAPI |
| Tests | None | 36 tests |
| Deployment | Basic | AWS EC2 ready |
| Documentation | Limited | Comprehensive |
| Status | ⛔ Deprecated | ✅ Active |

## Questions?

See:
- [MIGRATION_SUMMARY.md](../MIGRATION_SUMMARY.md)
- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
- [server_py/README.md](../server_py/README.md)

---

**⚠️ DO NOT USE FOR NEW DEPLOYMENTS**
**✅ USE `/server_py` INSTEAD**
