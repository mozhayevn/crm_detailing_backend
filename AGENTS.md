Project: CRM for car detailing

Architecture rules:
- Do not break RBAC logic
- Do not recreate OrderItems unnecessarily
- Keep order_item_id stable during updates
- Respect pricing lock/unlock workflow
- Respect pricing snapshots
- Respect audit logs and detailed order audit
- Respect warning levels in pricing
- Keep business logic production-like and maintainable
- Do not simplify architecture in a way that breaks future scaling

Priorities:
1. Preserve backend integrity
2. Keep code clear and typed
3. Prefer safe changes over risky refactors
4. Suggest before making large architectural changes
